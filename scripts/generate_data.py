"""
Single source of truth for synthetic dataset files (policy + billing PDFs and *_summary.json pairs).

Run from capstone root:
  python scripts/generate_data.py

Requires: pip install -r requirements.txt
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
POLICIES_DIR = ROOT / "data" / "policies"
BILLING_DIR = ROOT / "data" / "billing"

CARRIER = "NovaTel Communications"
CARRIER_TAG = f"{CARRIER} (fictional demo content)"


class PolicyPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


class BillingPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()} | {CARRIER}", align="C")


def _write_policy_pdf(
    path: Path,
    title: str,
    header_line: str,
    sections: Sequence[tuple[str, str]],
) -> int:
    """Write a policy PDF; return page count."""
    pdf = PolicyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, title)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, header_line)
    pdf.ln(6)

    for sec_title, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 6, sec_title)
        pdf.ln(1)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(4)

    pdf.output(str(path))
    return pdf.page_no()


def _emit_policy_pair(
    out_dir: Path,
    pdf_name: str,
    title: str,
    header_line: str,
    sections: Sequence[tuple[str, str]],
    topics: list[str],
    short_description: str,
    version: str,
    effective_date: str,
) -> None:
    stem = Path(pdf_name).stem
    json_name = f"{stem}_summary.json"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / pdf_name
    json_path = out_dir / json_name

    pages = _write_policy_pdf(pdf_path, title, header_line, sections)
    summary = {
        "document_type": "policy",
        "source_pdf": pdf_name,
        "title": title,
        "topics": topics,
        "effective_date": effective_date,
        "version": version,
        "page_count": pages,
        "short_description": short_description,
        "carrier_name": CARRIER,
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote {pdf_path}")
    print(f"Wrote {json_path} ({pages} pages)")


def generate_all_policies(out_dir: Path) -> None:
    """Four policy PDFs + matching *_summary.json files."""

    # --- 1. Billing & payment ---
    _emit_policy_pair(
        out_dir,
        pdf_name="billing_and_payment_policy.pdf",
        title="Billing and Payment Policy",
        header_line=f"Effective date: January 1, 2025 | Document version: 2.1 | {CARRIER_TAG}",
        sections=[
            (
                "1. Purpose",
                "This policy describes how NovaTel bills your account, when payments are due, which payment methods we accept, "
                "how late fees apply, and how you can enroll in automatic payments or paperless billing. This document is for "
                "educational and demonstration purposes only.",
            ),
            (
                "2. Billing cycle and statement date",
                "Your wireless service is billed on a monthly cycle. Your bill covers the upcoming month of service charges plus "
                "any usage-based charges, taxes, government fees, and one-time purchases from the prior period. "
                "Statements are generated on the same calendar day each month (your bill date). You can view your current and "
                "past statements in the customer portal under Billing > Statements.",
            ),
            (
                "3. Payment due date",
                "Payment is due by the due date printed on your bill, typically 21 days after the statement date. "
                "If the due date falls on a weekend or public holiday, payment received on the next business day is considered on time. "
                "Payments post to your account on the business day they are received by our payment processor.",
            ),
            (
                "4. Accepted payment methods",
                "NovaTel accepts: (a) pre-authorized debit from a linked bank account; (b) major credit and debit cards (Visa, Mastercard, American Express); "
                "(c) online bill payment through your financial institution using the account number shown on your bill; "
                "(d) one-time payments through the customer portal or mobile app. Cash payments are not accepted by mail.",
            ),
            (
                "5. Late payment and suspended service",
                "If we do not receive payment by the due date, a late payment fee may apply as shown on your rate card or welcome letter. "
                "The standard late fee is $15.00 CAD per missed due date for residential accounts unless prohibited by applicable law. "
                "Repeated late payments may result in collection activity or suspension of non-voicemail services until the balance is paid. "
                "Emergency access to 911 is not suspended for non-payment where prohibited by regulation.",
            ),
            (
                "6. Auto-pay and payment guarantees",
                "When you enroll in Auto-Pay, we will charge your selected payment method on the due date or up to three business days "
                "after if the due date is not a business day. You may cancel Auto-Pay at any time in the portal; cancellation must "
                "be received at least five business days before the next scheduled charge to guarantee that charge will not occur.",
            ),
            (
                "7. Partial payments and credits",
                "Partial payments are applied to the oldest outstanding charges first unless otherwise required by law. "
                "Promotional credits and account adjustments appear as separate line items and may reduce your balance before taxes "
                "where applicable.",
            ),
            (
                "8. Disputes before payment",
                "If you believe a charge is incorrect, contact us before the due date through the Refund and Dispute Policy channel. "
                "While a good-faith dispute is under review, we may request that you pay the undisputed portion of your bill on time.",
            ),
            (
                "9. Paperless billing",
                "You may opt in to paperless billing in the portal. When enrolled, we send an email when your statement is ready. "
                "You are responsible for maintaining a valid email address and reviewing your statement each month.",
            ),
            (
                "10. Contact",
                "Billing inquiries: billing@novatel-demo.example | Phone: 1-800-555-0100 (fictional). "
                "Hours: Monday to Friday, 8:00 a.m. to 8:00 p.m. local time.",
            ),
        ],
        topics=[
            "billing_cycle",
            "payment_due_date",
            "payment_methods",
            "late_fees",
            "auto_pay",
            "partial_payments",
            "disputes",
            "paperless_billing",
        ],
        short_description="How NovaTel bills accounts, when payments are due, accepted payment methods, late fees, Auto-Pay, and paperless billing.",
        version="2.1",
        effective_date="2025-01-01",
    )

    # --- 2. Refund & dispute (matches plan example filename) ---
    _emit_policy_pair(
        out_dir,
        pdf_name="refund_policy.pdf",
        title="Refund and Dispute Policy",
        header_line=f"Effective date: January 1, 2025 | Document version: 1.4 | {CARRIER_TAG}",
        sections=[
            (
                "1. Purpose",
                "This policy explains how to request refunds or billing credits, how we investigate disputes, and expected timelines. "
                "It applies to postpaid wireless accounts unless a promotion states otherwise.",
            ),
            (
                "2. Good-faith disputes",
                "You may dispute a charge you believe is incorrect. Contact us through the customer portal under Support > Billing dispute "
                "or by phone. Provide your account number, bill date, and the specific charge(s) in question. "
                "We may place a note on your account while we review; you may still owe any undisputed balance by the due date.",
            ),
            (
                "3. Investigation timeline",
                "We acknowledge receipt of a written dispute within five business days. Most investigations complete within 30 calendar days. "
                "Complex cases involving third-party content or roaming partners may take up to 60 days; we will notify you of any extension.",
            ),
            (
                "4. Refunds and credits",
                "If we find in your favor, we will issue a credit on a future bill or a refund to your original payment method where possible. "
                "Refunds to cards typically post within two billing cycles. Credits are shown as line items labeled Account adjustment or Credit.",
            ),
            (
                "5. Charges not eligible for refund",
                "Usage that matches network records, third-party purchases you authorized, and taxes remitted to governments are generally not refundable "
                "except where required by law or if we made a demonstrable billing error.",
            ),
            (
                "6. Chargebacks and payment reversals",
                "If you initiate a chargeback with your bank, we may suspend certain self-serve features until the dispute is resolved. "
                "We will provide evidence of charges as permitted by law. Duplicate credits (chargeback plus NovaTel credit) may be reversed.",
            ),
            (
                "7. Escalation",
                "If you disagree with our decision, you may ask for a supervisor review. You may also contact your provincial or territorial "
                "consumer telecom regulator or commissioner as applicable.",
            ),
            (
                "8. Contact",
                "Disputes: disputes@novatel-demo.example | Phone: 1-800-555-0101 (fictional).",
            ),
        ],
        topics=[
            "refunds",
            "billing_disputes",
            "investigation_timeline",
            "credits",
            "chargebacks",
            "escalation",
        ],
        short_description="Rules for refunds, credits, billing disputes, investigations, and chargebacks.",
        version="1.4",
        effective_date="2025-01-01",
    )

    # --- 3. Roaming & international ---
    _emit_policy_pair(
        out_dir,
        pdf_name="roaming_international_policy.pdf",
        title="Roaming and International Services Policy",
        header_line=f"Effective date: February 1, 2025 | Document version: 1.2 | {CARRIER_TAG}",
        sections=[
            (
                "1. Purpose",
                "This policy describes how roaming and international usage are rated, optional travel passes, and how to avoid unexpected charges when traveling.",
            ),
            (
                "2. Domestic coverage vs roaming",
                "Service included in your plan applies within Canada unless your plan explicitly includes U.S. or Mexico roaming. "
                "Outside your home coverage area, standard per-minute, per-SMS, and per-MB rates or travel bundles may apply.",
            ),
            (
                "3. International roaming",
                "When your device connects to a partner network abroad, voice, SMS, and data are billed according to the destination zone in your rate sheet. "
                "Data roaming can accumulate quickly; we recommend disabling data roaming in device settings unless you have purchased a travel pass.",
            ),
            (
                "4. Travel passes and add-ons",
                "Travel passes (e.g., daily or weekly bundles) may include a bucket of minutes, texts, and data in eligible destinations. "
                "Unused portions expire when the pass period ends. Activation times are shown at purchase.",
            ),
            (
                "5. Ship and aircraft networks",
                "Maritime and in-flight roaming may use satellite backhaul at premium rates. Usage may appear on your bill under International roaming.",
            ),
            (
                "6. International long distance from Canada",
                "Calls from Canada to international numbers are billed per minute based on destination. "
                "Some plans include discounted international long distance; check your plan details in the portal.",
            ),
            (
                "7. Alerts and spending caps",
                "You may enable usage alerts and optional roaming spend notifications in the app. Regulatory spend caps may apply where required.",
            ),
            (
                "8. Contact",
                "Travel support: travel@novatel-demo.example | Phone: 1-800-555-0102 (fictional).",
            ),
        ],
        topics=[
            "roaming",
            "international_rates",
            "travel_passes",
            "data_roaming",
            "long_distance",
            "usage_alerts",
        ],
        short_description="Roaming zones, travel passes, international rates, and how usage is billed outside Canada.",
        version="1.2",
        effective_date="2025-02-01",
    )

    # --- 4. Plan & fair usage ---
    _emit_policy_pair(
        out_dir,
        pdf_name="plan_fair_usage_policy.pdf",
        title="Plan Terms and Fair Usage Policy",
        header_line=f"Effective date: January 1, 2025 | Document version: 3.0 | {CARRIER_TAG}",
        sections=[
            (
                "1. Purpose",
                "This policy describes plan types, acceptable use of unlimited and high-data features, and network management when usage is unusually high.",
            ),
            (
                "2. Plan commitments",
                "Monthly plans renew each bill cycle unless you change or cancel according to your agreement. "
                "Device financing and promotional pricing may have minimum terms; early termination fees may apply as disclosed at sale.",
            ),
            (
                "3. Unlimited and high-usage plans",
                "Plans marketed as unlimited may include fair usage thresholds. After a threshold (for example 100 GB per line per month for demo purposes), "
                "we may reduce data speeds for the remainder of the cycle so that the experience remains fair for all customers on the cell.",
            ),
            (
                "4. Acceptable use",
                "Service is for personal or individual business use consistent with your agreement. Prohibited uses include reselling airtime without authorization, "
                "automated bulk messaging without consent, or activity that harms the network or other customers.",
            ),
            (
                "5. Network management",
                "During congestion, we may prioritize certain traffic types (for example voice and SMS) over heavy background downloads. "
                "This is not a pay-for-priority scheme for specific internet destinations.",
            ),
            (
                "6. Hotspot and tethering",
                "Mobile hotspot usage may count toward the same fair usage thresholds as on-device data unless your plan specifies a separate hotspot allowance.",
            ),
            (
                "7. Changes to terms",
                "We may update this policy with notice as required by law. Continued use after the effective date constitutes acceptance unless you cancel within any applicable window.",
            ),
            (
                "8. Contact",
                "Plans: plans@novatel-demo.example | Phone: 1-800-555-0103 (fictional).",
            ),
        ],
        topics=[
            "plan_terms",
            "unlimited_data",
            "fair_usage",
            "acceptable_use",
            "network_management",
            "hotspot",
        ],
        short_description="Plan commitments, fair usage on unlimited plans, acceptable use, and network management.",
        version="3.0",
        effective_date="2025-01-01",
    )


# --- Billing statements (Oct 2025 -> Mar 2026): normal months, Feb roaming spike, Mar dispute credit ---

BILLING_ACCOUNT = {"id": "TEL-2025-78432", "customer_name": "Sarah Mitchell"}
BILLING_PLAN = {"name": "Unlimited Plus", "monthly_charge": 85.0, "currency": "CAD"}


def _totals_from_line_items(line_items: list[dict[str, Any]]) -> dict[str, Any]:
    total_due = round(sum(float(x["amount"]) for x in line_items), 2)
    taxes = round(sum(float(x["amount"]) for x in line_items if x.get("category") == "taxes_fees"), 2)
    subtotal = round(
        sum(float(x["amount"]) for x in line_items if x.get("category") != "taxes_fees"),
        2,
    )
    return {
        "subtotal": subtotal,
        "taxes": taxes,
        "total_due": total_due,
        "currency": "CAD",
    }


def _fmt_cad(amount: float) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f} CAD"


def _write_billing_pdf(path: Path, stmt: dict[str, Any]) -> int:
    """Render one synthetic wireless bill PDF from statement dict."""
    pdf = BillingPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Wireless monthly statement", ln=1)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 4, CARRIER_TAG)
    pdf.ln(3)

    period = stmt["period"]
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, f"Statement period: {period['label']}", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Service dates: {period['start']} to {period['end']}", ln=1)
    pdf.cell(0, 5, f"Payment due: {stmt['due_date']}", ln=1)
    pdf.ln(2)

    acct = stmt["account"]
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "Account", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Account number: {acct['id']}", ln=1)
    pdf.cell(0, 5, f"Customer: {acct['customer_name']}", ln=1)
    pdf.ln(2)

    pl = stmt["plan"]
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "Plan", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"{pl['name']} - recurring {pl['monthly_charge']:.2f} {pl['currency']}/mo", ln=1)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(130, 6, "Description", border="B")
    pdf.cell(50, 6, "Amount (CAD)", border="B", align="R", ln=1)
    pdf.set_font("Helvetica", "", 10)
    for li in stmt["line_items"]:
        pdf.cell(130, 6, li["description"], border=0)
        pdf.cell(50, 6, _fmt_cad(float(li["amount"])), border=0, align="R", ln=1)

    pdf.ln(2)
    tot = stmt["totals"]
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(130, 6, "Total due", border="T")
    pdf.cell(50, 6, _fmt_cad(float(tot["total_due"])), border="T", align="R", ln=1)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "Notes", ln=1)
    pdf.set_font("Helvetica", "", 9)
    for note in stmt.get("notes", []):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 4, f"- {note}")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, "Demo-only statement. Amounts and names are fictional.")

    pdf.output(str(path))
    return pdf.page_no()


def _billing_statements_source() -> list[dict[str, Any]]:
    """Ordered Oct 2025 -> Mar 2026; amounts drive both PDF and JSON."""
    return [
        {
            "pdf_name": "billing_2025_10.pdf",
            "period": {"label": "Oct 2025", "start": "2025-10-01", "end": "2025-10-31"},
            "due_date": "2025-11-21",
            "line_items": [
                {"category": "base_plan", "description": "Unlimited Plus (monthly)", "amount": 85.0},
                {"category": "taxes_fees", "description": "GST/HST and regulatory fees", "amount": 12.5},
            ],
            "notes": ["Normal month - no roaming or international usage."],
        },
        {
            "pdf_name": "billing_2025_11.pdf",
            "period": {"label": "Nov 2025", "start": "2025-11-01", "end": "2025-11-30"},
            "due_date": "2025-12-22",
            "line_items": [
                {"category": "base_plan", "description": "Unlimited Plus (monthly)", "amount": 85.0},
                {"category": "taxes_fees", "description": "GST/HST and regulatory fees", "amount": 12.5},
            ],
            "notes": ["Regular monthly charges.", "Paperless discount already included in plan where applicable."],
        },
        {
            "pdf_name": "billing_2025_12.pdf",
            "period": {"label": "Dec 2025", "start": "2025-12-01", "end": "2025-12-31"},
            "due_date": "2026-01-21",
            "line_items": [
                {"category": "base_plan", "description": "Unlimited Plus (monthly)", "amount": 85.0},
                {"category": "usage_overage", "description": "Additional data (one-time)", "amount": 5.0},
                {"category": "taxes_fees", "description": "GST/HST and regulatory fees", "amount": 13.0},
            ],
            "notes": ["Small data overage during holiday travel within Canada."],
        },
        {
            "pdf_name": "billing_2026_01.pdf",
            "period": {"label": "Jan 2026", "start": "2026-01-01", "end": "2026-01-31"},
            "due_date": "2026-02-20",
            "line_items": [
                {"category": "base_plan", "description": "Unlimited Plus (monthly)", "amount": 85.0},
                {"category": "taxes_fees", "description": "GST/HST and regulatory fees", "amount": 12.5},
            ],
            "notes": ["Normal month - usage within plan limits."],
        },
        {
            "pdf_name": "billing_2026_02.pdf",
            "period": {"label": "Feb 2026", "start": "2026-02-01", "end": "2026-02-28"},
            "due_date": "2026-03-21",
            "line_items": [
                {"category": "base_plan", "description": "Unlimited Plus (monthly)", "amount": 85.0},
                {
                    "category": "roaming_international",
                    "description": "International roaming - voice, SMS, data (Europe)",
                    "amount": 142.5,
                },
                {"category": "taxes_fees", "description": "GST/HST and regulatory fees", "amount": 24.5},
            ],
            "notes": [
                "Unusually high international roaming charges.",
                "If you did not travel, review device settings or report possible SIM misuse.",
            ],
        },
        {
            "pdf_name": "billing_2026_03.pdf",
            "period": {"label": "Mar 2026", "start": "2026-03-01", "end": "2026-03-31"},
            "due_date": "2026-04-21",
            "line_items": [
                {"category": "base_plan", "description": "Unlimited Plus (monthly)", "amount": 85.0},
                {"category": "taxes_fees", "description": "GST/HST and regulatory fees", "amount": 12.5},
                {
                    "category": "credit_adjustment",
                    "description": "Billing adjustment - Feb 2026 roaming dispute (approved)",
                    "amount": -142.5,
                },
            ],
            "notes": [
                "Credit applied for disputed international roaming from Feb 2026 statement.",
                "No payment due this cycle; a small credit balance may appear on your next bill.",
            ],
        },
    ]


def _build_billing_statement_record(src: dict[str, Any]) -> dict[str, Any]:
    totals = _totals_from_line_items(src["line_items"])
    pdf_name = src["pdf_name"]
    return {
        "document_type": "billing_statement",
        "source_pdf": pdf_name,
        "period": src["period"],
        "due_date": src["due_date"],
        "account": dict(BILLING_ACCOUNT),
        "plan": dict(BILLING_PLAN),
        "line_items": [dict(x) for x in src["line_items"]],
        "totals": totals,
        "notes": list(src["notes"]),
    }


def generate_all_billing(out_dir: Path) -> list[dict[str, Any]]:
    """Emit 6 billing PDFs + matching *_summary.json; return summary dicts for rollup."""
    out_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    for src in _billing_statements_source():
        stmt = _build_billing_statement_record(src)
        pdf_path = out_dir / src["pdf_name"]
        stem = Path(src["pdf_name"]).stem
        json_path = out_dir / f"{stem}_summary.json"

        pages = _write_billing_pdf(pdf_path, stmt)
        stmt["page_count"] = pages
        json_path.write_text(json.dumps(stmt, indent=2), encoding="utf-8")
        summaries.append(stmt)
        print(f"Wrote {pdf_path}")
        print(f"Wrote {json_path} ({pages} pages)")
    return summaries


def write_billing_rollup(out_dir: Path, summaries: list[dict[str, Any]]) -> None:
    """Optional single file for quick chart loads (see plan §12.1)."""
    rollup = {
        "currency": "CAD",
        "account": dict(BILLING_ACCOUNT),
        "months": [
            {
                "period": s["period"]["label"],
                "source_pdf": s["source_pdf"],
                "total_due": s["totals"]["total_due"],
            }
            for s in summaries
        ],
    }
    path = out_dir / "billing_rollup.json"
    path.write_text(json.dumps(rollup, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    generate_all_policies(POLICIES_DIR)
    print("Done. Policy dataset: 4 PDFs + 4 *_summary.json under data/policies/")
    billing_summaries = generate_all_billing(BILLING_DIR)
    write_billing_rollup(BILLING_DIR, billing_summaries)
    print("Done. Billing dataset: 6 PDFs + 6 *_summary.json + billing_rollup.json under data/billing/")


if __name__ == "__main__":
    main()
