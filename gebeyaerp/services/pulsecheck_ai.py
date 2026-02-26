"""PulseCheck AI pipeline — Claude API integration.

Handles all Claude API calls including:
- Market intelligence gathering (web search)
- 4 specialist analyses (CFO, CMO, COO, Consultant)
- Pipeline orchestration
"""

import json
import time

import frappe
import requests


# ─── Specialist Prompts (ported from prompts.js) ─────────────────────────────

PROMPTS = {
    "cfo": (
        "You will be given business context including industry, stage, strategic priority, "
        "and live market intelligence. Use this context to make your financial analysis "
        "specific and relevant — reference the company's industry benchmarks, "
        "stage-appropriate expectations, and strategic goals.\n\n"
        "You are a Senior Fractional CFO. Analyze the financial KPIs and deliver:\n"
        "**Executive Summary** — 3-sentence health check grounded in the company's industry and stage\n"
        "**Red Flags** — ratios signaling risk, benchmarked against this specific industry\n"
        "**Green Flags** — genuine strengths relative to their competitive context\n"
        "**3 CFO Directives** — concrete actions tied to the company's stated strategic priority\n"
        "**Benchmark Context** — compare vs healthy benchmarks for this specific industry and stage\n"
        "Be direct, data-driven, and specific to this business. Use markdown."
    ),
    "cmo": (
        "You will be given business context including industry, competitors, strategic priority, "
        "and live market intelligence. Reference specific competitor intelligence and industry "
        "trends in your marketing recommendations.\n\n"
        "You are a data-driven CMO with expertise in growth and unit economics. Analyze the marketing KPIs:\n"
        "**Growth Engine Score** — 1 to 10, justify with LTV:CAC and Payback Period in the context of this industry\n"
        "**Growth vs. Burn** — over or under-investing relative to competitors and market conditions?\n"
        "**Retention Health** — is the bucket leaking? How does churn compare to industry norms?\n"
        "**3 CMO Strategies** — specific to this industry and competitive landscape, based on what the data demands\n"
        "**Revenue Impact** — how these metrics affect Net Income in 6 months given current market conditions\n"
        "Use markdown."
    ),
    "coo": (
        "You will be given business context including industry, business model, stage, "
        "and live market intelligence. Tailor your operational recommendations to the "
        "company's specific industry and stage.\n\n"
        "You are a COO with expertise in operational efficiency. Analyze the operating KPIs:\n"
        "**Operational Health Check** — overall rating in the context of this industry's operational norms\n"
        "**Bottlenecks and Risks** — where operations are bleeding, considering industry-specific constraints\n"
        "**Operational Strengths** — what's running well relative to industry benchmarks\n"
        "**3 COO Directives** — specific process improvements relevant to this business model and stage\n"
        "**30/60/90 Day Roadmap** — operational priorities aligned with the company's strategic goals\n"
        "Be execution-focused and industry-specific. Use markdown."
    ),
    "consultant": (
        "You will be given the full business context including profile, live market intelligence, "
        "and reports from the CFO, CMO, and COO. Your synthesis must directly reference the "
        "company's strategic priority, competitive landscape, and market conditions. "
        "This report will be delivered to the client — make it feel like it was written "
        "specifically for them.\n\n"
        "You are a Senior Business Consultant presenting a final board-level strategic report:\n"
        "**Company Verdict** — one bold sentence on this specific company's true position in their market\n"
        "**Alignment Audit** — are Finance, Marketing, and Operations working in sync toward the stated strategic priority?\n"
        "**Critical Interdependencies** — what the three reports reveal when read together, in light of market conditions\n"
        "**Strategic Recommendation** — ONE of: Aggressive Growth / Operational Efficiency / Capital Restructuring\n"
        "  — make the case using their specific competitive context\n"
        "**3 Board Directives** — cross-functional orders that directly address the competitive landscape\n"
        "**12-Month Outlook** — what this specific business looks like in a year if directives are followed\n"
        "Be decisive, visionary, and client-ready. Use markdown."
    ),
}

_API_URL = "https://api.anthropic.com/v1/messages"
_DEFAULT_MODEL = "claude-sonnet-4-6"


# ─── Config ──────────────────────────────────────────────────────────────────

def get_claude_config():
    """Get Claude API configuration from site_config or Shop Settings."""
    api_key = frappe.conf.get("claude_api_key")
    model = frappe.conf.get("claude_model", _DEFAULT_MODEL)

    if not api_key:
        try:
            settings = frappe.get_single("Shop Settings")
            api_key = settings.get_password("claude_api_key")
            if settings.claude_model:
                model = settings.claude_model
        except Exception:
            pass

    return api_key, model or _DEFAULT_MODEL


def _headers(api_key):
    return {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }


# ─── Claude API wrappers ──────────────────────────────────────────────────────

def call_claude(system, user, api_key, model):
    """Make a single Claude API call.

    Args:
        system: System prompt (specialist persona)
        user: User message (context + KPIs)
        api_key: Anthropic API key
        model: Claude model identifier

    Returns:
        str: Claude's response text
    """
    payload = {
        "model": model,
        "max_tokens": 10000,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    response = requests.post(
        _API_URL,
        headers=_headers(api_key),
        json=payload,
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(data["error"]["message"])
    return (data.get("content") or [{}])[0].get("text") or "No response."


def gather_intelligence(profile, api_key, model):
    """Gather live market intelligence via Claude web search.

    Args:
        profile: Business profile dict
        api_key: Anthropic API key
        model: Claude model identifier

    Returns:
        str: Market intelligence brief as markdown
    """
    industry = profile.get("industry", "retail")
    competitors = profile.get("competitors") or "major players in this industry"

    prompt = (
        f"Search for and summarize the following intelligence to support a business strategy analysis:\n\n"
        f"1. Recent trends, challenges, and opportunities in the \"{industry}\" industry (last 6-12 months)\n"
        f"2. Recent news, funding rounds, product launches, or strategic moves for these competitors: {competitors}\n"
        f"3. Any relevant macroeconomic, regulatory, or market shifts affecting this industry\n\n"
        "Return a concise but information-dense summary (300-400 words) organized under three headings:\n"
        "**Industry Trends**, **Competitor Intelligence**, **Market Conditions**.\n"
        "This will be used as context for a business strategy report."
    )

    payload = {
        "model": model,
        "max_tokens": 1500,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        response = requests.post(
            _API_URL,
            headers=_headers(api_key),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        text = "\n".join(
            block.get("text", "")
            for block in (data.get("content") or [])
            if block.get("type") == "text"
        )
        return text.strip() or "No market intelligence gathered."
    except Exception:
        frappe.log_error(frappe.get_traceback(), "PulseCheck: web search failed")
        return "Market intelligence unavailable (web search failed)."


def build_context_block(profile, intelligence_brief):
    """Build the shared context string injected into every specialist prompt."""
    return (
        f"BUSINESS CONTEXT:\n"
        f"- Company: {profile.get('companyName', 'Not specified')}\n"
        f"- Industry: {profile.get('industry', 'Not specified')}\n"
        f"- Business Model: {profile.get('businessModel', 'Not specified')}\n"
        f"- Stage: {profile.get('stage', 'Not specified')}\n"
        f"- Strategic Priority: {profile.get('strategicPriority', 'Not specified')}\n"
        f"- Mission: {profile.get('mission', 'Not specified')}\n"
        f"- Vision: {profile.get('vision', 'Not specified')}\n"
        f"- Top Competitors: {profile.get('competitors', 'Not specified')}\n\n"
        f"LIVE MARKET INTELLIGENCE:\n{intelligence_brief}\n\n"
    )


# ─── Main pipeline ────────────────────────────────────────────────────────────

@frappe.whitelist()
def run_pulsecheck_analysis(company, from_date, to_date, overrides=None):
    """Run the full PulseCheck analysis pipeline.

    Creates a PulseCheck Report document and runs:
    1. Data extraction from ERPNext
    2. KPI computation
    3. Market intelligence gathering (web search)
    4. Four specialist AI analyses (CFO, CMO, COO, Consultant)

    Args:
        company: Company name
        from_date: Analysis period start (YYYY-MM-DD)
        to_date: Analysis period end (YYYY-MM-DD)
        overrides: Optional JSON string of user-overridden data fields

    Returns:
        str: Name of the created PulseCheck Report document
    """
    api_key, model = get_claude_config()
    if not api_key:
        frappe.throw(
            "Claude API key not configured. "
            "Please set it in Shop Settings or add claude_api_key to site_config.json."
        )

    start_time = time.time()

    # Create the report doc in Processing state so the UI can poll it
    report = frappe.get_doc({
        "doctype": "PulseCheck Report",
        "company": company,
        "from_date": from_date,
        "to_date": to_date,
        "status": "Processing",
        "claude_model": model,
    })
    report.insert(ignore_permissions=True)
    frappe.db.commit()

    try:
        # ── 1. Extract raw data ──────────────────────────────────────────────
        from gebeyaerp.services.pulsecheck import (
            get_financial_snapshot,
            get_marketing_snapshot,
            get_operating_snapshot,
        )
        fin_data = get_financial_snapshot(company, from_date, to_date)
        mkt_data = get_marketing_snapshot(company, from_date, to_date)
        ops_data = get_operating_snapshot(company, from_date, to_date)

        # Apply user overrides (allows correcting auto-extracted numbers)
        if overrides:
            ov = json.loads(overrides) if isinstance(overrides, str) else overrides
            fin_data.update(ov.get("financial", {}))
            mkt_data.update(ov.get("marketing", {}))
            ops_data.update(ov.get("operating", {}))

        # ── 2. Compute KPIs ──────────────────────────────────────────────────
        from gebeyaerp.services.pulsecheck_kpis import (
            calc_financial_kpis,
            calc_marketing_kpis,
            calc_operating_kpis,
        )
        fin_kpis = calc_financial_kpis(fin_data)
        mkt_kpis = calc_marketing_kpis(mkt_data)
        ops_kpis = calc_operating_kpis(ops_data)

        # ── 3. Build business profile from Shop Settings ─────────────────────
        settings = frappe.get_single("Shop Settings")
        profile = {
            "companyName":       settings.shop_name or company,
            "industry":          settings.shop_type or "Retail",
            "businessModel":     "Retail",
            "stage":             "SME",
            "strategicPriority": "Operational Efficiency",
            "mission":           "",
            "vision":            "",
            "competitors":       "",
        }

        # ── 4. Gather market intelligence ────────────────────────────────────
        intelligence = gather_intelligence(profile, api_key, model)

        # ── 5. Build shared context block ────────────────────────────────────
        context = build_context_block(profile, intelligence)

        # ── 6. Run specialist analyses sequentially ──────────────────────────
        fin_kpis_str = json.dumps(fin_kpis, indent=2, ensure_ascii=False)
        mkt_kpis_str = json.dumps(mkt_kpis, indent=2, ensure_ascii=False)
        ops_kpis_str = json.dumps(ops_kpis, indent=2, ensure_ascii=False)

        cfo_report = call_claude(
            PROMPTS["cfo"],
            f"{context}FINANCIAL KPIs:\n{fin_kpis_str}",
            api_key, model,
        )
        cmo_report = call_claude(
            PROMPTS["cmo"],
            f"{context}MARKETING KPIs:\n{mkt_kpis_str}",
            api_key, model,
        )
        coo_report = call_claude(
            PROMPTS["coo"],
            f"{context}OPERATING KPIs:\n{ops_kpis_str}",
            api_key, model,
        )
        consultant_user = (
            f"{context}"
            f"FINANCIAL KPIs:\n{fin_kpis_str}\n\n"
            f"MARKETING KPIs:\n{mkt_kpis_str}\n\n"
            f"OPERATING KPIs:\n{ops_kpis_str}\n\n"
            f"--- CFO REPORT ---\n{cfo_report}\n\n"
            f"--- CMO REPORT ---\n{cmo_report}\n\n"
            f"--- COO REPORT ---\n{coo_report}"
        )
        consultant_report = call_claude(
            PROMPTS["consultant"], consultant_user, api_key, model
        )

        # ── 7. Persist results ───────────────────────────────────────────────
        report.status             = "Complete"
        report.run_duration       = round(time.time() - start_time, 1)
        report.profile_data       = json.dumps(profile, ensure_ascii=False)
        report.financial_data     = json.dumps(fin_data, ensure_ascii=False)
        report.marketing_data     = json.dumps(mkt_data, ensure_ascii=False)
        report.operating_data     = json.dumps(ops_data, ensure_ascii=False)
        report.financial_kpis     = json.dumps(fin_kpis, ensure_ascii=False)
        report.marketing_kpis     = json.dumps(mkt_kpis, ensure_ascii=False)
        report.operating_kpis     = json.dumps(ops_kpis, ensure_ascii=False)
        report.intelligence_brief = intelligence
        report.cfo_report         = cfo_report
        report.cmo_report         = cmo_report
        report.coo_report         = coo_report
        report.consultant_report  = consultant_report
        report.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        report.status       = "Error"
        report.error_log    = frappe.get_traceback()
        report.run_duration = round(time.time() - start_time, 1)
        report.save(ignore_permissions=True)
        frappe.db.commit()
        raise

    return report.name


@frappe.whitelist()
def get_pulsecheck_report(report_name):
    """Fetch a PulseCheck Report for the UI.

    Args:
        report_name: Name of the PulseCheck Report document

    Returns:
        dict: All report fields
    """
    doc = frappe.get_doc("PulseCheck Report", report_name)
    frappe.has_permission("PulseCheck Report", "read", doc=doc, throw=True)
    return {
        "name":               doc.name,
        "company":            doc.company,
        "from_date":          str(doc.from_date),
        "to_date":            str(doc.to_date),
        "status":             doc.status,
        "run_duration":       doc.run_duration,
        "claude_model":       doc.claude_model,
        "intelligence_brief": doc.intelligence_brief,
        "cfo_report":         doc.cfo_report,
        "cmo_report":         doc.cmo_report,
        "coo_report":         doc.coo_report,
        "consultant_report":  doc.consultant_report,
        "financial_kpis":     doc.financial_kpis,
        "marketing_kpis":     doc.marketing_kpis,
        "operating_kpis":     doc.operating_kpis,
        "error_log":          doc.error_log,
    }
