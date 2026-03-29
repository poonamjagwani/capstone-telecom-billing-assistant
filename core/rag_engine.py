from __future__ import annotations

from pathlib import Path
import re

from config import Settings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.models import SourceItem


class RagEngine:
    """FAISS-backed semantic retrieval over billing and policy PDFs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.index_dir = settings.index_dir
        self.billing_dir = settings.billing_dir
        self.policies_dir = settings.policies_dir
        self.vectorstore: FAISS | None = None

    def _embedding_model(self):
        provider = self.settings.llm_provider.lower()
        if provider == "openai":
            return OpenAIEmbeddings(
                model=self.settings.openai_embedding_model,
                api_key=self.settings.openai_api_key or None,
                base_url=self.settings.openai_base_url or None,
            )
        return OllamaEmbeddings(
            model=self.settings.ollama_embedding_model,
            base_url=self.settings.ollama_base_url,
        )

    def _pdf_paths(self) -> list[Path]:
        policy_pdfs = sorted(self.policies_dir.glob("*.pdf"))
        billing_pdfs = sorted(self.billing_dir.glob("*.pdf"))
        return policy_pdfs + billing_pdfs

    def _load_pdf_documents(self):
        docs = []
        for pdf_path in self._pdf_paths():
            loader = PyPDFLoader(str(pdf_path))
            loaded = loader.load()
            for d in loaded:
                d.metadata["source_pdf"] = pdf_path.name
            docs.extend(loaded)
        return docs

    @staticmethod
    def _is_billing_source(source_pdf: str) -> bool:
        # Only monthly billing statements should be treated as billing evidence.
        # Example: billing_2026_03.pdf
        return bool(re.match(r"^billing_\d{4}_\d{2}\.pdf$", source_pdf))

    @staticmethod
    def _query_mentions_billing_or_month(question: str) -> bool:
        q = question.lower()
        month_tokens = {
            "jan",
            "january",
            "feb",
            "february",
            "mar",
            "march",
            "apr",
            "april",
            "may",
            "jun",
            "june",
            "jul",
            "july",
            "aug",
            "august",
            "sep",
            "sept",
            "september",
            "oct",
            "october",
            "nov",
            "november",
            "dec",
            "december",
        }
        if "billing" in q or "bill" in q or "charge" in q or "credit" in q or "roaming" in q:
            return True
        return any(m in q for m in month_tokens)

    def _semantic_candidates(self, question: str, top_k: int):
        assert self.vectorstore is not None
        fetch_k = max(top_k * 4, 14)
        pairs = self.vectorstore.similarity_search_with_score(question, k=fetch_k)
        mention_billing = self._query_mentions_billing_or_month(question)
        reranked = []
        for d, score in pairs:
            source_pdf = d.metadata.get("source_pdf") or Path(d.metadata.get("source", "unknown")).name
            adjusted = float(score)
            # Lower is better for FAISS distance; reduce score to prefer billing when prompt asks for it.
            if mention_billing and self._is_billing_source(source_pdf):
                adjusted -= 0.12
            # Slight preference for policy when explicit policy/dispute terminology is present.
            if ("policy" in question.lower() or "dispute" in question.lower()) and not self._is_billing_source(source_pdf):
                adjusted -= 0.05
            reranked.append((adjusted, d))
        reranked.sort(key=lambda x: x[0])
        return reranked

    @staticmethod
    def _dedupe_docs(reranked_pairs, top_k: int):
        unique: list = []
        seen: set[tuple[str, int | None]] = set()
        for _, d in reranked_pairs:
            source_pdf = d.metadata.get("source_pdf") or Path(d.metadata.get("source", "unknown")).name
            page = d.metadata.get("page") if isinstance(d.metadata.get("page"), int) else None
            key = (source_pdf, page)
            if key in seen:
                continue
            seen.add(key)
            unique.append(d)
            if len(unique) >= top_k:
                break
        return unique

    def build_index(self, force_rebuild: bool = False) -> dict[str, str]:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        embeddings = self._embedding_model()
        has_saved_index = any(self.index_dir.iterdir())
        try:
            if has_saved_index and not force_rebuild:
                self.vectorstore = FAISS.load_local(
                    str(self.index_dir),
                    embeddings,
                    allow_dangerous_deserialization=True,
                )
                return {"status": "ok", "detail": "Loaded existing FAISS index."}

            raw_docs = self._load_pdf_documents()
            if not raw_docs:
                return {"status": "error", "detail": "No PDF documents found to index."}

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            chunks = splitter.split_documents(raw_docs)
            if not chunks:
                return {"status": "error", "detail": "Document chunks are empty after splitting."}

            self.vectorstore = FAISS.from_documents(chunks, embeddings)
            self.vectorstore.save_local(str(self.index_dir))
            return {
                "status": "ok",
                "detail": f"Built FAISS index from {len(raw_docs)} pages into {len(chunks)} chunks.",
            }
        except Exception as exc:
            return {"status": "error", "detail": f"Failed to build/load FAISS index: {exc}"}

    def query(self, question: str, top_k: int = 4) -> tuple[str, list[SourceItem]]:
        if self.vectorstore is None:
            result = self.build_index(force_rebuild=False)
            if result["status"] != "ok":
                return (
                    f"RAG index is unavailable: {result['detail']}",
                    [],
                )

        assert self.vectorstore is not None  # for type-checkers
        try:
            reranked = self._semantic_candidates(question, top_k=top_k)
            docs = self._dedupe_docs(reranked, top_k=top_k)
        except Exception as exc:
            return (
                f"RAG search failed: {exc}",
                [],
            )

        if not docs:
            return (
                "I could not find relevant passages in the indexed documents. Try rephrasing with a month, charge type, or policy topic.",
                [],
            )

        sources: list[SourceItem] = []
        policy_lines: list[str] = []
        billing_lines: list[str] = []
        for d in docs:
            source = d.metadata.get("source_pdf") or Path(d.metadata.get("source", "unknown")).name
            page = d.metadata.get("page")
            snippet = re.sub(r"\s+", " ", d.page_content.strip())[:260]
            page_suffix = f" (page {page + 1})" if isinstance(page, int) else ""
            sources.append(SourceItem(source=f"{source}{page_suffix}", snippet=snippet))
            line = f"- {source}{page_suffix}: {snippet}"
            if self._is_billing_source(source):
                billing_lines.append(line)
            else:
                policy_lines.append(line)

        blocks: list[str] = ["Top semantic matches from documents:"]
        if policy_lines:
            blocks.append("Policy evidence:")
            blocks.extend(policy_lines)
        if billing_lines:
            blocks.append("Billing evidence:")
            blocks.extend(billing_lines)
        return "\n".join(blocks), sources

