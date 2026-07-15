#!/usr/bin/env python3
"""Build a click-to-copy HubSpot AI Context paste sheet from a JSON data dict.

Updated 2026-05-28 for HubSpot's reorganized AI Context page structure.
The output is a three-tab paste sheet:

    Tab 1 — Business      (HubSpot's AI Context → Business tab)
    Tab 2 — Customers     (ICPs + Personas — HubSpot's AI Context → Customers tab)
    Tab 3 — Brand Kit     (HubSpot's Brand Kit surface, linked from Business tab)

Usage:
    python build_company_context_html.py path/to/data.json [output.html] \\
        --icps path/to/icps.csv --personas path/to/personas.csv

The JSON schema is documented in templates/company-context-data.example.json.

Brand overrides: if a file named `brand-override.local.py` exists in the
current working directory, its module-level constants override the defaults.
"""

import argparse
import html
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace


# CS2 brand defaults — canonical CS2 Brand Atlas tokens.
# Source: chadstamm-brand/brand-guide.html — Universe Palette + Four Rules.
#
# Hero move (Rule 3: one hero move per surface): the H1 client name in Impact
# display, set in RUMO blue against Sand. Everything else recedes. Algarve
# teal carries interactions only. Terracotta appears once, with intent.
#
# Override with brand-override.local.py in the user's working directory to
# apply your own brand.
DEFAULT_BRAND = SimpleNamespace(
    ACCENT_COLOR="#1EBEB1",        # Algarve teal — primary accent (interactive elements only)
    ACCENT_HOVER="#16998E",        # Algarve deepened for hover
    TEXT_PRIMARY="#0C2340",        # RUMO blue — anchor ink
    TEXT_SECONDARY="#1F628E",      # Tagus — secondary text
    BORDER_COLOR="#C4CED3",        # Cool gray — thin dividers
    BG_PRIMARY="#FFFFFF",          # White — card surface
    BG_SECONDARY="#FAF6F1",        # Sand — canonical warm paper (Brand Atlas)
    BG_TERTIARY="#F4EFE7",         # Sand deepened — layered surfaces
    SUCCESS_COLOR="#DA5525",       # Terracotta — used sparingly for high-importance accents
    FONT_FAMILY_BODY='"Open Sans", system-ui, sans-serif',
    FONT_FAMILY_HEADING='"Montserrat", sans-serif',
    FONT_FAMILY_MONO='"JetBrains Mono", Menlo, monospace',
    GOOGLE_FONTS_URL="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Open+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
    LOGO_DATA_URI=None,
    LOGO_ALT_TEXT=None,
    LOGO_HEIGHT_PX=40,
    FOOTER_LEFT="hubspot-ai-context · github.com/chadstamm/claude-skill-hubspot-ai-context",
    FOOTER_RIGHT=None,
)


def load_brand() -> SimpleNamespace:
    """Load brand-override.local.py from CWD if present, else use defaults."""
    override_path = Path.cwd() / "brand-override.local.py"
    if not override_path.exists():
        return DEFAULT_BRAND
    spec = importlib.util.spec_from_file_location("brand_override", override_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    brand = SimpleNamespace(**vars(DEFAULT_BRAND))
    for key in vars(DEFAULT_BRAND):
        if hasattr(module, key):
            value = getattr(module, key)
            if value is not None:
                setattr(brand, key, value)
    return brand


def esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def attr(value) -> str:
    return html.escape(str(value or ""), quote=True)


def render_pill_field(label: str, items: list, copy_all_label: str = None) -> str:
    """Multi-tag field with click-to-copy on each pill + Copy-All button.
    Always renders the field — empty lists get a "[Confirm with client]"
    placeholder so the user sees the field exists. Synthesis discipline:
    never invent tags to fill a field.
    """
    if not items:
        return f"""
<div class="field field--empty">
  <div class="field-label">{esc(label)}</div>
  <div class="field-value field-value--placeholder"><p>[Confirm with client]</p></div>
</div>"""
    pills_html = "".join(
        f'<button class="pill" data-copy="{attr(i)}" title="Click to copy">'
        f'<span class="pill-text">{esc(i)}</span>'
        f'<span class="pill-icon" aria-hidden="true">⧉</span>'
        f'</button>'
        for i in items
    )
    join_str = "; ".join(items)
    return f"""
<div class="field">
  <div class="field-label">{esc(label)}</div>
  <div class="field-hint">Click any tag to copy it individually, or use Copy all below.</div>
  <div class="pills">{pills_html}</div>
  <button class="copy-all" data-copy="{attr(join_str)}">Copy all ({len(items)})</button>
</div>"""


def render_text_field(label: str, value: str, mono: bool = False) -> str:
    """Single-value text field. Always renders the field — empty values get a
    visible "[Confirm with client]" placeholder so the user sees the field
    exists rather than the section silently dropping. Synthesis discipline:
    never fabricate data to fill a field — leave it blank and the build script
    will flag it here.
    """
    if not value or not str(value).strip():
        return f"""
<div class="field field--empty">
  <div class="field-label">{esc(label)}</div>
  <div class="field-value field-value--placeholder"><p>[Confirm with client]</p></div>
</div>"""
    css_class = "field-value field-value--mono" if mono else "field-value"
    return f"""
<div class="field">
  <div class="field-label">{esc(label)}</div>
  <div class="{css_class}"><p>{esc(value)}</p></div>
  <button class="copy-btn" data-copy="{attr(value)}">Copy</button>
</div>"""


def render_pain_points(pain_points: list) -> str:
    """Pain points: bolded label + paragraph, single Copy for the entire field
    (HubSpot's pain points field accepts one bulk paste)."""
    if not pain_points:
        return ""
    items_html = []
    full_text_parts = []
    for label, body in pain_points:
        full_text_parts.append(f"**{label}** {body}")
        items_html.append(
            f'<div class="pain-item"><p><strong>{esc(label)}</strong> {esc(body)}</p></div>'
        )
    full_text = "\n\n".join(full_text_parts)
    return f"""
<div class="field">
  <div class="field-label">What pain points does your company solve?</div>
  <div class="field-value">{''.join(items_html)}</div>
  <button class="copy-btn" data-copy="{attr(full_text)}">Copy</button>
</div>"""


def render_products(products: list) -> str:
    """HubSpot's Itemized Products field has separate Product Name and
    Description columns — give each a Copy button so they can be pasted
    into their respective HubSpot fields independently."""
    if not products:
        return ""
    rows = []
    for p in products:
        title = p.get("title", "")
        url = p.get("url", "")
        models = p.get("models", "")
        blurb = p.get("blurb", "")
        rows.append(f"""
<tr>
  <td>
    <strong>{esc(title)}</strong>
    <button class="copy-btn copy-btn--mini" data-copy="{attr(title)}">Copy name</button>
    <div class="product-meta">
      <span class="mono">{esc(models)}</span>
      {('<br><a href="' + attr(url) + '" target="_blank">' + esc(url) + '</a>') if url else ''}
    </div>
  </td>
  <td>
    <div class="product-blurb">{esc(blurb)}</div>
    <button class="copy-btn copy-btn--mini" data-copy="{attr(blurb)}">Copy description</button>
  </td>
</tr>""")
    return f"""
<div class="field">
  <div class="field-label">Itemized products or services</div>
  <div class="field-hint">Product Name and Description are separate fields in HubSpot — copy each independently.</div>
  <table class="products-table">
    <thead><tr><th>Product Name</th><th>Description</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>"""


def render_industry_classification(rows: list) -> str:
    if not rows:
        return ""
    items_html = []
    for row in rows:
        items_html.append(f"""
<tr>
  <td><strong>{esc(row.get('field',''))}</strong></td>
  <td>{esc(row.get('value',''))}</td>
  <td><button class="copy-btn" data-copy="{attr(row.get('value',''))}">Copy</button></td>
  <td><span class="note">{esc(row.get('note',''))}</span></td>
</tr>""")
    return f"""
<div class="field">
  <div class="field-label">Industry Classification</div>
  <table class="cls-table">
    <thead><tr><th>Field</th><th>Value</th><th></th><th>Note</th></tr></thead>
    <tbody>{''.join(items_html)}</tbody>
  </table>
</div>"""


def render_competitors(competitors: list, note: str = "") -> str:
    """HubSpot's Main Competitors entry has separate fields for company name,
    URL, and competitive areas. Give each its own Copy button. Description
    is shown for context but not copyable (it's notes, not a HubSpot field)."""
    if not competitors:
        return ""
    items_html = []
    for c in competitors:
        name = c.get("name", "")
        domain = c.get("domain", "")
        areas = "; ".join(c.get("areas", []))
        note_text = c.get("note", "")
        items_html.append(f"""
<div class="competitor">
  <div class="competitor-row">
    <div class="competitor-row-label">Name</div>
    <div class="competitor-row-value"><strong>{esc(name)}</strong></div>
    <button class="copy-btn copy-btn--mini" data-copy="{attr(name)}">Copy</button>
  </div>
  <div class="competitor-row competitor-row--note">
    <div class="competitor-row-label">Notes</div>
    <div class="competitor-row-value">{esc(note_text)}</div>
  </div>
  <div class="competitor-row">
    <div class="competitor-row-label">URL</div>
    <div class="competitor-row-value"><a href="https://{attr(domain)}" target="_blank">{esc(domain)}</a></div>
    <button class="copy-btn copy-btn--mini" data-copy="{attr(domain)}">Copy</button>
  </div>
  <div class="competitor-row">
    <div class="competitor-row-label">Competitive Areas</div>
    <div class="competitor-row-value">{esc(areas)}</div>
    <button class="copy-btn copy-btn--mini" data-copy="{attr(areas)}">Copy</button>
  </div>
</div>""")
    note_html = f'<div class="note">{esc(note)}</div>' if note else ""
    return f"""
<div class="field">
  <div class="field-label">Main Competitors</div>
  <div class="field-hint">Each competitor has separate Copy buttons for Name, URL, and Competitive Areas — paste each into the matching HubSpot field.</div>
  {''.join(items_html)}
  {note_html}
</div>"""


def render_replacement_rules(rules: list, note: str = "") -> str:
    if not rules:
        return f"""
<div class="field field--empty">
  <div class="field-label">Replacement Rules</div>
  <div class="field-value field-value--placeholder"><p>[Confirm with client]</p></div>
</div>"""
    rows = []
    for r in rules:
        f, t = r.get("from", ""), r.get("to", "")
        rows.append(f"""
<tr>
  <td><span class="mono">{esc(f)}</span></td>
  <td><span class="mono">{esc(t)}</span></td>
  <td><button class="copy-btn" data-copy="{attr(f)}">Copy from</button></td>
  <td><button class="copy-btn" data-copy="{attr(t)}">Copy to</button></td>
</tr>""")
    note_html = f'<div class="note">{esc(note)}</div>' if note else ""
    return f"""
<div class="field">
  <div class="field-label">Replacement Rules</div>
  <table class="rules-table">
    <thead><tr><th>From</th><th>To</th><th></th><th></th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  {note_html}
</div>"""


def render_open_items(items: list) -> str:
    if not items:
        return ""
    lis = "\n".join(f"<li>{i}</li>" for i in items)  # items may contain inline HTML
    return f"""
<div class="field">
  <div class="field-label">Open Items for Client Confirmation</div>
  <ol class="open-items">{lis}</ol>
</div>"""


# ---------------------------------------------------------------------------
# ICP rendering — updated 2026-05-28 for new HubSpot Customers tab → Create ICP form
# ---------------------------------------------------------------------------
# CSV column names mirror HubSpot's form labels exactly. The "Other" field is
# gone (its Pain Points content moved to Persona records; Buying Triggers and
# Decision Context fold into Description). Industry → Industries (plural),
# Location → Locations (plural), Revenue → Annual Revenue.

ICP_FIELD_ORDER = [
    "Name", "Description", "Business Type",
    "Job Titles", "Interests", "Industries", "Locations",
    "Company Size", "Annual Revenue", "Age Range",
]
ICP_PILL_FIELDS = {"Locations"}
ICP_SEMICOLON_FIELDS = {"Job Titles", "Interests", "Industries", "Company Size", "Annual Revenue", "Age Range"}

# Persona rendering — new in 2026-05-28 reorg.
# Customers tab now has a Personas database in addition to ICPs. Persona form
# is simpler: Name + Job Titles (required) + Value Propositions + Pain Points.
PERSONA_FIELD_ORDER = [
    "Name", "Job Titles", "Value Propositions", "Pain Points",
]
PERSONA_SEMICOLON_FIELDS = {"Job Titles", "Value Propositions", "Pain Points"}


def split_items(value: str) -> list:
    s = (value or "").replace("\n", " ").strip()
    if not s:
        return []
    sep = ";" if ";" in s else ","
    items = [t.strip() for t in s.split(sep)]
    return [t for t in items if t]


def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9 \-]", "", s)
    s = s.replace(" ", "-")
    return re.sub(r"-+", "-", s).strip("-")


def load_icps(csv_path: Path) -> list:
    import csv
    if not csv_path or not csv_path.exists():
        return []
    with csv_path.open() as f:
        return list(csv.DictReader(f))


def load_personas(csv_path: Path) -> list:
    """Load Personas CSV. Schema:
        Source ICP, Name, Job Titles, Value Propositions, Pain Points, Slug
    """
    import csv
    if not csv_path or not csv_path.exists():
        return []
    with csv_path.open() as f:
        return list(csv.DictReader(f))


def render_icp_pill_field(label: str, value: str) -> str:
    items = split_items(value)
    if not items:
        return ""
    pills = "".join(
        f'<button class="pill" data-copy="{attr(i)}" title="Click to copy">'
        f'<span class="pill-text">{esc(i)}</span><span class="pill-icon">⧉</span></button>'
        for i in items
    )
    join_str = "; ".join(items)
    return f"""
<div class="field">
  <div class="field-label">{esc(label)}</div>
  <div class="field-hint">Click any tag to copy individually, or use Copy all below.</div>
  <div class="pills">{pills}</div>
  <button class="copy-all" data-copy="{attr(join_str)}">Copy all ({len(items)})</button>
</div>"""


def render_icp_semicolon_field(label: str, value: str) -> str:
    items = split_items(value)
    if not items:
        return ""
    joined = "; ".join(items)
    return f"""
<div class="field">
  <div class="field-label">{esc(label)}</div>
  <div class="field-value"><p>{esc(joined)}</p></div>
  <button class="copy-btn" data-copy="{attr(joined)}">Copy</button>
</div>"""


def render_icp_text_field(label: str, value: str) -> str:
    if not value:
        return ""
    paras = re.split(r"\n\s*\n", value.strip())
    paras_html = "".join(f"<p>{esc(p)}</p>" for p in paras if p)
    return f"""
<div class="field">
  <div class="field-label">{esc(label)}</div>
  <div class="field-value">{paras_html}</div>
  <button class="copy-btn" data-copy="{attr(value)}">Copy</button>
</div>"""


def render_icp_field(label: str, value: str) -> str:
    if not value:
        return ""
    if label in ICP_PILL_FIELDS:
        return render_icp_pill_field(label, value)
    if label in ICP_SEMICOLON_FIELDS:
        return render_icp_semicolon_field(label, value)
    return render_icp_text_field(label, value)


# ---------------------------------------------------------------------------
# Per-product card rendering (Business tab → Products and services structured DB)
# ---------------------------------------------------------------------------
# Replaces the old single-table "Itemized products" field. Each product is its
# own row in HubSpot; the paste sheet renders one card per product with
# independently copyable Name, Description, and Category fields.

def render_product_card(product: dict, num: int) -> str:
    name = (product.get("name") or product.get("Name") or "Unnamed product").strip()
    description = (product.get("description") or product.get("Description") or "").strip()
    category = (product.get("category") or product.get("Category") or "").strip()
    url = (product.get("url") or product.get("URL") or "").strip()
    slug = slugify(name)

    url_html = ""
    if url:
        url_html = f'<div class="product-card-url"><a href="{attr(url)}" target="_blank">{esc(url)}</a></div>'

    desc_html = ""
    if description:
        desc_html = f"""
  <div class="field">
    <div class="field-label">Description</div>
    <div class="field-value"><p>{esc(description)}</p></div>
    <button class="copy-btn" data-copy="{attr(description)}">Copy</button>
  </div>"""

    cat_html = ""
    if category:
        cat_html = f"""
  <div class="field">
    <div class="field-label">Category</div>
    <div class="field-value"><p>{esc(category)}</p></div>
    <button class="copy-btn" data-copy="{attr(category)}">Copy</button>
  </div>"""
    else:
        cat_html = """
  <div class="field">
    <div class="field-label">Category</div>
    <div class="field-hint">Not synthesized — leave blank for client to define, or fill manually.</div>
  </div>"""

    return f"""
<article class="product-card" id="product-{esc(slug)}">
  <div class="product-card-header">
    <h3 class="product-card-name">{esc(name)}</h3>
    <button class="copy-btn copy-btn--mini" data-copy="{attr(name)}">Copy name</button>
  </div>
  {url_html}
  {desc_html}
  {cat_html}
</article>"""


# ---------------------------------------------------------------------------
# Per-Persona card rendering (Customers tab → Personas database — new in 2026-05-28 reorg)
# ---------------------------------------------------------------------------

def render_persona_field(label: str, value: str) -> str:
    if not value:
        return ""
    if label in PERSONA_SEMICOLON_FIELDS:
        return render_icp_semicolon_field(label, value)
    return render_icp_text_field(label, value)


def render_persona_card(persona: dict, num: int) -> str:
    name = (persona.get("Name") or "Unnamed persona").strip()
    source_icp = (persona.get("Source ICP") or "").strip()
    slug = (persona.get("Slug") or slugify(name)).strip()
    fields_html = "\n".join(
        render_persona_field(label, persona.get(label, ""))
        for label in PERSONA_FIELD_ORDER
        if label != "Name"  # Name renders as the card header, not as a field
    )

    parts = []
    for label in PERSONA_FIELD_ORDER:
        v = (persona.get(label) or "").strip()
        if not v:
            continue
        if label in PERSONA_SEMICOLON_FIELDS:
            v = "; ".join(split_items(v))
        parts.append(f"=== {label.upper()} ===\n{v}")
    copy_all_text = "\n\n".join(parts)

    meta = f"Source ICP: {source_icp}" if source_icp else ""
    return f"""
<article class="persona" id="persona-{esc(slug)}">
  <div class="persona-header">
    <div class="persona-titles">
      <div class="persona-title-row">
        <h3>{esc(name)}</h3>
        <button class="copy-btn copy-btn--mini" data-copy="{attr(name)}" title="Copy persona name">Copy name</button>
      </div>
      <div class="persona-meta">{esc(meta)}</div>
    </div>
    <button class="copy-all" data-copy="{attr(copy_all_text)}">Copy all fields</button>
  </div>
  {fields_html}
</article>"""


def render_icp_card(icp: dict, num: int) -> str:
    name = (icp.get("Name") or "Unnamed").strip()
    category = (icp.get("Category") or "").strip()
    grouping = (icp.get("Grouping") or "").strip()
    slug = (icp.get("Slug") or slugify(name)).strip()
    fields_html = "\n".join(render_icp_field(label, icp.get(label, "")) for label in ICP_FIELD_ORDER)

    parts = []
    for label in ICP_FIELD_ORDER:
        v = (icp.get(label) or "").strip()
        if not v:
            continue
        if label in (ICP_PILL_FIELDS | ICP_SEMICOLON_FIELDS):
            v = "; ".join(split_items(v))
        parts.append(f"=== {label.upper()} ===\n{v}")
    copy_all_text = "\n\n".join(parts)

    meta = " · ".join(p for p in [grouping, category] if p)
    return f"""
<article class="icp" id="icp-{esc(slug)}">
  <div class="icp-header">
    <div class="icp-titles">
      <div class="icp-title-row">
        <h2>{esc(name)}</h2>
        <button class="copy-btn copy-btn--mini" data-copy="{attr(name)}" title="Copy ICP name">Copy name</button>
      </div>
      <div class="icp-meta">{esc(meta)}</div>
    </div>
    <button class="copy-all" data-copy="{attr(copy_all_text)}">Copy all fields</button>
  </div>
  {fields_html}
</article>"""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_html(data: dict, brand: SimpleNamespace, icps: list = None, personas: list = None) -> str:
    """Build the three-tab HubSpot AI Context paste sheet.

    Tab structure (post 2026-05-28 reorg):
      Tab 1 — Business     (HubSpot AI Context → Business tab)
      Tab 2 — Customers    (ICPs + Personas — HubSpot AI Context → Customers tab)
      Tab 3 — Brand Kit    (HubSpot Brand Kit surface, linked from Business tab)
    """
    client_name = data.get("client_name", "Client")
    research_date = data.get("research_date", "")

    # ---- Tab 1: Business (HubSpot AI Context → Business tab) ----
    # Section order mirrors HubSpot's UI:
    #   Identity & classification → Location & scale → Business profile →
    #   Market & ecosystem context → Technology stack → Products & services

    identity_sections = [
        render_text_field("Name (Legal name)", data.get("legal_name", "")),
        render_text_field("Domain", data.get("domain", "")),
        render_text_field("Industry", data.get("industry", "")),
        render_text_field("Type (Public / Private)", data.get("company_type", "")),
    ]
    industry_class_sections = [
        render_text_field("Industry", data.get("industry", "")),
        render_text_field("Sub-industry", data.get("sub_industry", "")),
        render_text_field("Industry group", data.get("industry_group", "")),
        render_text_field("Business sector", data.get("business_sector", "")),
        render_pill_field("Industry-related tags", data.get("industry_related_tags", [])),
    ]
    customer_sentiment_sections = [
        render_text_field("NPS score", data.get("nps_score", "")),
        render_pill_field("Positive associations", data.get("positive_associations", [])),
        render_pill_field("Negative associations", data.get("negative_associations", [])),
    ]

    # Every field renders regardless of whether the synthesis found data —
    # empty values get a "[Confirm with client]" placeholder from
    # render_text_field / render_pill_field. Synthesis discipline: never
    # fabricate data to fill a field; leave the field blank and let the
    # build script flag it.
    location_scale_sections = [
        render_text_field("Headquarters location", data.get("hq_location", "")),
        render_text_field("Company size (employee count)", data.get("company_size", "")),
        render_text_field("Annual revenue", data.get("annual_revenue", "")),
        render_text_field("Founded year", data.get("founded_year", "")),
    ]

    business_profile_sections = [
        render_text_field("Business description", data.get("business_description", "")),
        render_pill_field("Unique value propositions", data.get("unique_value_propositions", [])),
        render_text_field("Business model", data.get("business_model", "")),
        render_text_field("Primary business goal", data.get("primary_business_goal", "")),
        render_text_field("Mission (≤ 50 words)", data.get("mission", "")),
        render_text_field("Vision", data.get("vision", "")),
        render_pill_field("Social responsibility", data.get("social_responsibility", [])),
        render_text_field("NPS score", data.get("nps_score", "")),
        render_pill_field("Positive associations", data.get("positive_associations", [])),
        render_pill_field("Negative associations", data.get("negative_associations", [])),
    ]

    # Main competitors: dict-format entries → structured cards (separate Name / URL / Competitive-Areas
    # copy buttons via render_competitors); plain strings → flat pills (backward-compatible).
    _mc = data.get("main_competitors", [])
    _main_competitors_field = (
        render_competitors(_mc, data.get("competitors_note", ""))
        if (_mc and isinstance(_mc[0], dict))
        else render_pill_field("Main competitors", _mc)
    )

    market_sections = [
        render_pill_field("Competitive advantages", data.get("competitive_advantages", [])),
        _main_competitors_field,
    ]

    tech_sections = [
        render_pill_field("Existing apps and tools", data.get("existing_apps_and_tools", [])),
        render_pill_field("Technology stack (key tools)", data.get("tech_stack_key_tools", [])),
    ]

    # Market and ecosystem context (Business tab structured section): Main competitors + Stakeholders
    market_eco_sections = [
        _main_competitors_field,
        render_pill_field("Stakeholders", data.get("stakeholders", [])),
    ]

    # Products and services: structured DB. One card per product.
    products_db = data.get("products_db") or data.get("products", [])  # backward-compat with old key
    if products_db:
        product_cards = "\n".join(
            render_product_card(p, i + 1) for i, p in enumerate(products_db)
        )
        products_section = (
            '<div class="field-hint">'
            'HubSpot\'s Products and services is a structured database. Click '
            '"Add Product or Service" in HubSpot, then paste Name, Description, '
            'and Category from each card below. Repeat per product.'
            '</div>'
            + product_cards
        )
    else:
        products_section = (
            '<div class="empty-state"><p>No products synthesized.</p>'
            '<p class="empty-state-hint">Run the skill with a Phase 2 Pass B deep crawl to populate.</p></div>'
        )

    tab_business = (
        '<h2 class="tab-section-title">Identity and classification</h2>'
        + "\n".join(s for s in identity_sections if s)
        + '<h2 class="tab-section-title">Location and scale</h2>'
        + "\n".join(s for s in location_scale_sections if s)
        + '<h2 class="tab-section-title">Business profile</h2>'
        + "\n".join(s for s in business_profile_sections if s)
        + '<h2 class="tab-section-title">Market and ecosystem context</h2>'
        + "\n".join(s for s in market_eco_sections if s)
        + '<h2 class="tab-section-title">Technology stack</h2>'
        + "\n".join(s for s in tech_sections if s)
        + '<h2 class="tab-section-title">Products and services</h2>'
        + products_section
    )

    # ---- Tab 2: Customers (ICPs + Personas) ----
    if icps:
        icp_cards = "\n".join(render_icp_card(icp, i + 1) for i, icp in enumerate(icps))
        icps_section = (
            '<h2 class="tab-section-title">Ideal Customer Profiles</h2>'
            '<div class="field-hint">Click "Add ICP" in HubSpot, then paste each field from the card below.</div>'
            + icp_cards
        )
    else:
        icps_section = (
            '<h2 class="tab-section-title">Ideal Customer Profiles</h2>'
            '<div class="empty-state"><p>No ICPs included in this run.</p>'
            '<p class="empty-state-hint">Pass <code>--icps PATH</code> to populate.</p></div>'
        )

    if personas:
        persona_cards = "\n".join(render_persona_card(p, i + 1) for i, p in enumerate(personas))
        personas_section = (
            '<h2 class="tab-section-title">Personas</h2>'
            '<div class="field-hint">Personas are new in HubSpot\'s 2026-05-28 reorg. Click "Add Persona" in HubSpot, then paste each field.</div>'
            + persona_cards
        )
    else:
        personas_section = (
            '<h2 class="tab-section-title">Personas</h2>'
            '<div class="empty-state"><p>No Personas included in this run.</p>'
            '<p class="empty-state-hint">Pass <code>--personas PATH</code> to populate.</p></div>'
        )

    tab_customers = icps_section + personas_section

    # ---- Tab 3: Brand Kit (HubSpot's separate Brand Kit surface) ----
    brand_voice_sections = [
        render_pill_field("Personality (HubSpot picklist — max 4)", data.get("personality", [])),
        render_pill_field("Default Tone (HubSpot picklist — max 4)", data.get("default_tone", [])),
        render_text_field("Mission (≤ 50 words)", data.get("mission_brandkit") or data.get("mission", "")),
        render_pill_field("Terms to Avoid (≤ 20 words)", data.get("terms_to_avoid", [])),
        render_replacement_rules(data.get("replacement_rules", []), data.get("replacement_note", "")),
        render_pill_field("Inclusivity", data.get("inclusivity", [])),
    ]
    open_items_html = render_open_items(data.get("open_items", []))
    addl = (
        '<h2 class="tab-section-title">Additional context</h2>'
        '<div class="field-hint">Crawl-derived knowledge — in HubSpot these sit under "Additional context" beneath Brand voice.</div>'
        + '<h3 class="tab-section-title" style="font-size:16px;margin-top:28px">Industry classification</h3>'
        + "\n".join(s for s in industry_class_sections if s)
        + '<h3 class="tab-section-title" style="font-size:16px;margin-top:28px">Customer sentiment</h3>'
        + "\n".join(s for s in customer_sentiment_sections if s)
        + '<h3 class="tab-section-title" style="font-size:16px;margin-top:28px">Competitive landscape</h3>'
        + "\n".join(s for s in market_sections if s)
        + '<h3 class="tab-section-title" style="font-size:16px;margin-top:28px">Content themes</h3>'
        + (render_pill_field("Primary content topics", data.get("content_themes", [])) or "")
        + (render_pill_field("Content format types", data.get("content_format_types", [])) or "")
        + '<h3 class="tab-section-title" style="font-size:16px;margin-top:28px">Tech stack</h3>'
        + (render_pill_field("Technologies", data.get("technologies", [])) or "")
        + (render_pill_field("Technology categories", data.get("technology_categories", [])) or "")
        + '<h3 class="tab-section-title" style="font-size:16px;margin-top:28px">Social responsibility</h3>'
        + (render_pill_field("Supported social causes", data.get("supported_social_causes", [])) or "")
        + (render_pill_field("Sustainability initiatives", data.get("sustainability_initiatives", [])) or "")
    )
    tab_brand = (
        '<div class="field-hint">Brand voice + Additional context — together on HubSpot\'s Brand Kit surface.</div>'
        + "\n".join(s for s in brand_voice_sections if s)
        + addl
        + (open_items_html if open_items_html else "")
    )

    body = f"""
<div class="tabs">
  <nav class="tab-nav">
    <button class="tab-button is-active" data-tab="business">Business</button>
    <button class="tab-button" data-tab="customers">Customers</button>
    <button class="tab-button" data-tab="brand">Brand Kit</button>
  </nav>
  <section class="tab-panel is-active" data-tab-panel="business">{tab_business}</section>
  <section class="tab-panel" data-tab-panel="customers">{tab_customers}</section>
  <section class="tab-panel" data-tab-panel="brand">{tab_brand}</section>
</div>"""

    logo_html = ""
    if brand.LOGO_DATA_URI:
        logo_html = f'<img class="logo" src="{attr(brand.LOGO_DATA_URI)}" alt="{attr(brand.LOGO_ALT_TEXT or "")}" style="height: {brand.LOGO_HEIGHT_PX}px; width: auto;">'

    css = f"""
:root {{
  --accent: {brand.ACCENT_COLOR};
  --accent-deep: {brand.ACCENT_HOVER};
  --accent-soft: color-mix(in srgb, var(--accent) 8%, transparent);
  --accent-line: color-mix(in srgb, var(--accent) 22%, transparent);
  --accent-glow: color-mix(in srgb, var(--accent) 35%, transparent);
  --ink: {brand.TEXT_PRIMARY};
  --ink-soft: {brand.TEXT_SECONDARY};
  --ink-mute: #6F6A5E;
  --ink-faint: #9A9285;
  --rumo: #1A2744;
  --rumo-line: color-mix(in srgb, var(--rumo) 22%, transparent);
  --tile: #003087;
  --tile-line: color-mix(in srgb, var(--tile) 22%, transparent);
  --paper: {brand.BG_PRIMARY};
  --paper-warm: {brand.BG_SECONDARY};
  --paper-deep: {brand.BG_TERTIARY};
  --rule: color-mix(in srgb, {brand.BORDER_COLOR} 50%, transparent);
  --success: {brand.SUCCESS_COLOR};
  --serif: {brand.FONT_FAMILY_HEADING};
  --sans: {brand.FONT_FAMILY_BODY};
  --mono: {brand.FONT_FAMILY_MONO};
  --lift-1: 0 1px 0 rgba(12, 35, 64, 0.04), 0 12px 28px -16px rgba(12, 35, 64, 0.10);
  --lift-2: 0 1px 0 rgba(12, 35, 64, 0.05), 0 18px 40px -20px rgba(12, 35, 64, 0.16);
  --ease: cubic-bezier(0.2, 0.8, 0.2, 1);
}}

*, *::before, *::after {{ box-sizing: border-box; }}
* {{ margin: 0; padding: 0; }}
html {{ -webkit-text-size-adjust: 100%; }}

body {{
  font-family: var(--sans);
  font-size: 16px; line-height: 1.65;
  color: var(--ink); background: var(--paper-warm);
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "kern", "liga";
  min-height: 100vh; padding: 56px 24px 80px; position: relative;
}}

body::before {{
  content: ''; position: fixed; inset: 0; pointer-events: none;
  z-index: 100; opacity: 0.03; mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence baseFrequency='0.9' seed='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}}

body::after {{
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: -1;
  background:
    radial-gradient(ellipse 80% 60% at 15% 0%, color-mix(in srgb, var(--accent) 4%, transparent), transparent 60%),
    radial-gradient(ellipse 60% 50% at 90% 100%, color-mix(in srgb, var(--success) 3%, transparent), transparent 60%);
}}

::selection {{ background: var(--accent); color: var(--paper); }}

a {{
  color: var(--accent); text-decoration: none;
  border-bottom: 1px solid var(--accent-line);
  transition: border-color 180ms var(--ease), color 180ms var(--ease);
}}
a:hover {{ border-bottom-color: var(--accent); color: var(--accent-deep); }}

button:focus-visible, a:focus-visible {{
  outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px;
}}

.container {{ max-width: 880px; margin: 0 auto; }}

.header {{
  position: relative; background: var(--paper);
  padding: 64px 56px 48px; margin-bottom: 32px;
  border: 1px solid var(--rule); border-radius: 4px;
  box-shadow: var(--lift-1); overflow: hidden;
  display: flex; flex-direction: column;
}}
.header::before {{
  content: ''; position: absolute; top: 0; left: 0;
  width: 96px; height: 5px; background: var(--accent);
}}
.header::after {{
  content: ''; display: none;
}}
.header h1 {{
  order: 2;
  display: flex; flex-direction: column; gap: 6px;
  margin: 0; text-wrap: balance;
}}
.h1-client {{
  font-family: var(--serif); font-weight: 800;
  font-size: clamp(44px, 6vw, 72px);
  line-height: 0.98; letter-spacing: -0.015em;
  color: var(--ink); text-wrap: balance;
}}
.h1-page {{
  font-family: var(--serif);
  font-size: clamp(13px, 1.4vw, 16px); font-weight: 700;
  line-height: 1.2; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--ink);
}}
.subtitle {{
  order: 1; font-family: var(--serif);
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 18px;
  display: flex; align-items: center; gap: 10px;
}}
.subtitle::before {{
  content: ''; display: inline-block;
  width: 24px; height: 1px; background: var(--accent);
}}
.logo {{ order: 0; margin-bottom: 28px; vertical-align: middle; width: auto !important; max-width: max-content; align-self: flex-start; display: block; }}

.field {{
  position: relative; background: var(--paper);
  border: 1px solid var(--rule); border-radius: 4px;
  padding: 32px 36px 28px 40px; margin-bottom: 14px;
  box-shadow: var(--lift-1);
  transition: box-shadow 280ms var(--ease);
}}
.field--empty {{
  background: color-mix(in srgb, var(--paper-warm) 60%, var(--paper) 40%);
  border-style: dashed; box-shadow: none;
}}
.icp-title-row, .persona-title-row {{
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}}
.icp-title-row h2, .persona-title-row h3 {{
  margin: 0;
}}
.field--empty .field-label {{ opacity: 0.85; }}
.field-value--placeholder {{
  color: var(--ink-mute); font-style: italic;
  font-family: var(--mono); font-size: 0.85em;
  letter-spacing: 0.02em;
}}
.field::before {{
  content: ''; position: absolute;
  top: 32px; bottom: 32px; left: 0;
  width: 3px; background: var(--accent);
  border-radius: 0 2px 2px 0;
  transition: top 280ms var(--ease), bottom 280ms var(--ease);
}}
.field:hover {{ box-shadow: var(--lift-2); }}
.field:hover::before {{ top: 24px; bottom: 24px; }}

.field-label {{
  font-family: var(--serif); font-size: 11px; font-weight: 700;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--rumo); margin-bottom: 8px;
  display: flex; align-items: baseline; gap: 14px;
}}
.field-label::after {{
  content: ''; flex: 1; height: 1px;
  background: var(--rumo-line);
  position: relative; bottom: 3px;
}}
.field-hint {{
  font-family: var(--sans); font-size: 13px; font-style: italic;
  color: var(--ink-mute); margin-bottom: 18px; letter-spacing: 0.005em;
}}
.field-value {{
  font-family: var(--sans); font-size: 16px; line-height: 1.72;
  color: var(--ink-soft); margin-bottom: 18px;
}}
.field-value p {{ margin-bottom: 14px; text-wrap: pretty; }}
.field-value p:last-child {{ margin-bottom: 0; }}
.field-value--mono {{ font-family: var(--mono); font-size: 14px; }}
.note {{
  font-family: var(--sans); font-size: 13px; font-style: italic;
  color: var(--ink-mute); margin-top: 14px;
  padding: 8px 0 8px 14px; border-left: 2px solid var(--rule); line-height: 1.55;
}}

.pills {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }}
.pill {{
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 12px; font-weight: 500;
  letter-spacing: 0.005em; color: var(--ink);
  background: var(--paper-deep); border: 1px solid transparent;
  padding: 7px 12px; border-radius: 3px; cursor: pointer;
  transition: all 180ms var(--ease); font-feature-settings: "tnum";
}}
.pill .pill-text {{ line-height: 1; }}
.pill .pill-icon {{
  font-size: 11px; color: var(--ink-faint); line-height: 1;
  transition: color 180ms var(--ease), transform 180ms var(--ease);
}}
.pill:hover {{
  background: var(--accent-soft); border-color: var(--accent);
  color: var(--accent-deep); transform: translateY(-1px);
}}
.pill:hover .pill-icon {{ color: var(--accent); transform: scale(1.1); }}
.pill.copied {{ background: var(--success); border-color: var(--success); color: var(--paper); }}
.pill.copied .pill-icon {{ color: var(--paper); }}

.copy-btn, .copy-all {{
  display: inline-flex; align-items: center; gap: 6px;
  font-family: var(--serif); font-size: 11px; font-weight: 700;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--paper); background: var(--accent);
  border: none; padding: 11px 20px; border-radius: 3px; cursor: pointer;
  transition: background 180ms var(--ease), transform 180ms var(--ease), box-shadow 240ms var(--ease);
}}
.copy-btn:hover, .copy-all:hover {{
  background: var(--accent-deep); transform: translateY(-1px);
  box-shadow: 0 8px 16px -8px var(--accent-glow);
}}
.copy-btn:active, .copy-all:active {{ transform: translateY(0); }}
.copy-btn.copied, .copy-all.copied {{ background: var(--success); }}
.copy-btn--inline {{ font-size: 9px; padding: 6px 12px; margin-left: 10px; letter-spacing: 0.18em; }}
.copy-btn--mini {{ font-size: 9px; padding: 5px 11px; margin-left: 10px; letter-spacing: 0.18em; vertical-align: middle; }}

.products-table, .cls-table {{
  width: 100%; border-collapse: collapse; margin-top: 10px;
  border-bottom: 1px solid var(--rule);
}}
.products-table th, .cls-table th {{
  font-family: var(--serif); font-size: 10px; font-weight: 700;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-mute); text-align: left;
  padding: 12px 14px; border-bottom: 2px solid var(--accent); background: transparent;
}}
.products-table td, .cls-table td {{
  padding: 18px 14px; border-bottom: 1px solid var(--rule);
  font-family: var(--sans); font-size: 14px; line-height: 1.6;
  color: var(--ink-soft); vertical-align: top;
}}
.products-table td strong, .cls-table td strong {{
  font-family: var(--serif); font-weight: 700; color: var(--ink);
  font-size: 15px; display: inline-block; margin-bottom: 2px;
}}
.products-table tbody tr:hover {{
  background: linear-gradient(90deg, var(--accent-soft) 0%, transparent 60%);
}}

/* Replacement Rules — extra breathing room between From/To text columns and the Copy buttons */
.rules-table th:nth-child(2),
.rules-table td:nth-child(2) {{
  padding-right: 32px;
}}
.rules-table td:nth-child(3),
.rules-table td:nth-child(4) {{
  padding-left: 8px;
  padding-right: 8px;
}}
.product-meta {{ margin-top: 8px; font-size: 12px; line-height: 1.5; color: var(--ink-mute); }}
.product-meta a {{ font-family: var(--mono); font-size: 11px; }}
.product-blurb {{ margin-bottom: 10px; color: var(--ink-soft); }}
.mono, span.mono {{ font-family: var(--mono); font-size: 12px; color: var(--ink-mute); letter-spacing: 0.005em; }}

.competitor {{
  background: var(--paper-warm); border: 1px solid var(--rule);
  border-left: 2px solid var(--accent-line); border-radius: 3px;
  padding: 22px 26px; margin-bottom: 12px;
  transition: border-left-color 280ms var(--ease), box-shadow 280ms var(--ease);
}}
.competitor:last-child {{ margin-bottom: 0; }}
.competitor:hover {{ border-left-color: var(--accent); box-shadow: var(--lift-1); }}
.competitor-row {{
  display: grid; grid-template-columns: 110px 1fr auto; gap: 18px;
  align-items: center; padding: 11px 0; border-bottom: 1px dashed var(--rule);
}}
.competitor-row:first-child {{ padding-top: 0; }}
.competitor-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
.competitor-row-label {{
  font-family: var(--serif); font-size: 9px; font-weight: 700;
  letter-spacing: 0.22em; text-transform: uppercase; color: var(--ink-mute);
}}
.competitor-row-value {{
  font-family: var(--sans); font-size: 15px; line-height: 1.55; color: var(--ink);
}}
.competitor-row-value strong {{
  font-family: var(--serif); font-size: 17px; font-weight: 700;
  color: var(--ink); letter-spacing: -0.005em;
}}
.competitor-row-value a {{
  font-family: var(--mono); font-size: 13px;
  color: var(--accent); border-bottom-color: var(--accent-line);
}}
.competitor-row--note {{ align-items: start; }}
.competitor-row--note .competitor-row-value {{
  font-size: 13px; line-height: 1.6; color: var(--ink-mute);
  font-style: italic; padding: 2px 0;
}}

.pain-item {{ padding: 16px 0; border-bottom: 1px dashed var(--rule); }}
.pain-item:first-child {{ padding-top: 0; }}
.pain-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
.pain-item p {{ margin: 0; font-size: 15px; line-height: 1.7; color: var(--ink-soft); }}
.pain-item strong {{
  display: block; font-family: var(--serif); font-weight: 700;
  font-size: 13px; letter-spacing: 0.04em; color: var(--accent); margin-bottom: 6px;
}}

.open-items {{ list-style: none; counter-reset: open-counter; padding: 0; margin: 0; }}
.open-items li {{
  counter-increment: open-counter; position: relative;
  padding: 14px 0 14px 48px; border-bottom: 1px dashed var(--rule);
  font-family: var(--sans); font-size: 14px; line-height: 1.65; color: var(--ink-soft);
}}
.open-items li::before {{
  content: counter(open-counter, decimal-leading-zero);
  position: absolute; left: 0; top: 16px;
  font-family: var(--mono); font-size: 11px; font-weight: 600;
  color: var(--accent); letter-spacing: 0.06em; font-feature-settings: "tnum";
}}
.open-items li:first-child {{ padding-top: 4px; }}
.open-items li:first-child::before {{ top: 6px; }}
.open-items li:last-child {{ border-bottom: none; }}
.open-items li strong {{ font-family: var(--serif); font-weight: 700; color: var(--ink); letter-spacing: -0.003em; }}

.footer {{
  margin-top: 56px; padding: 24px 0 0;
  border-top: 1px solid var(--rule);
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.06em; color: var(--ink-faint);
}}

/* ============= TABS ============= */
.tabs {{ margin-top: 16px; }}
.tab-nav {{
  display: flex; gap: 0; margin-bottom: 24px;
  border-bottom: 1px solid var(--rule);
  position: sticky; top: 0; z-index: 50;
  background: var(--paper-warm); padding-top: 8px;
  backdrop-filter: blur(8px);
}}
.tab-button {{
  background: transparent; border: none; cursor: pointer;
  font-family: var(--serif); font-size: 12px; font-weight: 700;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-mute);
  padding: 16px 20px; position: relative;
  transition: color 180ms var(--ease);
}}
.tab-button:hover {{ color: var(--ink); }}
.tab-button::after {{
  content: ''; position: absolute;
  bottom: -1px; left: 16px; right: 16px;
  height: 3px; background: transparent;
  transition: background 200ms var(--ease);
}}
/* Tab 1 — Business — terracotta */
.tab-button[data-tab="business"].is-active {{ color: var(--success); }}
.tab-button[data-tab="business"].is-active::after {{ background: var(--success); }}
/* Tab 2 — Customers — rumo blue */
.tab-button[data-tab="customers"].is-active {{ color: var(--rumo); }}
.tab-button[data-tab="customers"].is-active::after {{ background: var(--rumo); }}
/* Tab 3 — Brand Kit — Algarve teal */
.tab-button[data-tab="brand"].is-active {{ color: var(--accent); }}
.tab-button[data-tab="brand"].is-active::after {{ background: var(--accent); }}

.tab-panel {{ display: none; animation: tab-fade-in 280ms var(--ease); }}
.tab-panel.is-active {{ display: block; }}
@keyframes tab-fade-in {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* Business tab active — terracotta field stripes, labels, section rules */
.tab-panel[data-tab-panel="business"].is-active .field::before {{ background: var(--success); }}
.tab-panel[data-tab-panel="business"].is-active .field-label {{ color: var(--success); }}
.tab-panel[data-tab-panel="business"].is-active .field-label::after {{ background: color-mix(in srgb, var(--success) 22%, transparent); }}
.tab-panel[data-tab-panel="business"].is-active .tab-section-title::before {{ background: var(--success); }}

/* Customers tab active — rumo-blue ICP + Persona card stripes, labels, section rules */
.tab-panel[data-tab-panel="customers"].is-active .icp::before,
.tab-panel[data-tab-panel="customers"].is-active .persona::before {{ background: var(--rumo); }}
.tab-panel[data-tab-panel="customers"].is-active .field-label {{ color: var(--rumo); }}
.tab-panel[data-tab-panel="customers"].is-active .field-label::after {{ background: var(--rumo-line); }}
.tab-panel[data-tab-panel="customers"].is-active .tab-section-title::before {{ background: var(--rumo); }}

/* Brand Kit tab active — Algarve teal field stripes + labels */
.tab-panel[data-tab-panel="brand"].is-active .field::before {{ background: var(--accent); }}
.tab-panel[data-tab-panel="brand"].is-active .field-label {{ color: var(--accent); }}
.tab-panel[data-tab-panel="brand"].is-active .field-label::after {{ background: var(--accent-line); }}

.tab-section-title {{
  font-family: var(--serif); font-size: clamp(22px, 2.4vw, 30px);
  font-weight: 700; letter-spacing: -0.012em; line-height: 1.15;
  color: var(--ink);
  margin: 56px 0 20px;
  padding-top: 20px;
  position: relative;
  text-wrap: balance;
}}
.tab-section-title::before {{
  content: ''; position: absolute; top: 0; left: 0;
  width: 56px; height: 3px; background: var(--accent);
}}
.tab-section-title:first-child {{ margin-top: 16px; }}

.empty-state {{
  background: var(--paper); border: 1px dashed var(--rule);
  padding: 40px 32px; text-align: center; border-radius: 4px;
  color: var(--ink-mute);
}}
.empty-state p {{ margin: 0 0 8px; }}
.empty-state-hint {{ font-size: 13px; font-style: italic; }}
.empty-state code {{
  font-family: var(--mono); font-size: 12px;
  background: var(--paper-deep); padding: 2px 6px; border-radius: 3px;
  color: var(--ink);
}}

/* ============= ICP CARDS ============= */
.icp {{
  position: relative; background: var(--paper);
  padding: 32px 36px 28px 40px; margin-bottom: 16px;
  border: 1px solid var(--rule); border-radius: 4px;
  box-shadow: var(--lift-1);
  transition: box-shadow 280ms var(--ease);
}}
.icp::before {{
  content: ''; position: absolute;
  top: 32px; bottom: 32px; left: 0; width: 3px;
  background: var(--success); border-radius: 0 2px 2px 0;
  transition: top 280ms var(--ease), bottom 280ms var(--ease);
}}
.icp:hover {{ box-shadow: var(--lift-2); }}
.icp:hover::before {{ top: 24px; bottom: 24px; }}
.icp-header {{
  display: flex; align-items: center; gap: 18px;
  padding-bottom: 18px; margin-bottom: 22px;
  border-bottom: 1px solid var(--rule);
}}
.icp-titles {{ flex: 1; }}
.icp-titles h2 {{
  margin: 0; font-family: var(--serif); font-weight: 700;
  font-size: 22px; letter-spacing: -0.01em; color: var(--ink);
}}
.icp-meta {{
  font-family: var(--serif); font-size: 10px; font-weight: 600;
  color: var(--ink-mute); margin-top: 4px;
  text-transform: uppercase; letter-spacing: 0.18em;
}}
.icp-header .copy-all {{ margin-left: auto; }}
.icp .field {{
  background: transparent; box-shadow: none; border: none;
  padding: 18px 0; margin-bottom: 0;
  border-bottom: 1px dashed var(--rule); border-radius: 0;
}}
.icp .field::before {{ display: none; }}
.icp .field:last-child {{ border-bottom: none; padding-bottom: 0; }}

/* ============= PERSONA CARDS ============= */
/* Personas sit on the Customers tab below ICPs. Same card chrome as ICPs but a
   slightly smaller h3 title to read as a sub-unit of its parent ICP. */
.persona {{
  position: relative; background: var(--paper);
  padding: 32px 36px 28px 40px; margin-bottom: 16px;
  border: 1px solid var(--rule); border-radius: 4px;
  box-shadow: var(--lift-1);
  transition: box-shadow 280ms var(--ease);
}}
.persona::before {{
  content: ''; position: absolute;
  top: 32px; bottom: 32px; left: 0; width: 3px;
  background: var(--rumo); border-radius: 0 2px 2px 0;
  transition: top 280ms var(--ease), bottom 280ms var(--ease);
}}
.persona:hover {{ box-shadow: var(--lift-2); }}
.persona:hover::before {{ top: 24px; bottom: 24px; }}
.persona-header {{
  display: flex; align-items: center; gap: 18px;
  padding-bottom: 18px; margin-bottom: 22px;
  border-bottom: 1px solid var(--rule);
}}
.persona-titles {{ flex: 1; }}
.persona-titles h3 {{
  font-family: var(--serif); font-weight: 700;
  font-size: 19px; letter-spacing: -0.01em; color: var(--ink);
}}
.persona-meta {{
  font-family: var(--serif); font-size: 10px; font-weight: 600;
  color: var(--ink-mute); margin-top: 4px;
  text-transform: uppercase; letter-spacing: 0.18em;
}}
.persona-header .copy-all {{ margin-left: auto; }}
.persona .field {{
  background: transparent; box-shadow: none; border: none;
  padding: 18px 0; margin-bottom: 0;
  border-bottom: 1px dashed var(--rule); border-radius: 0;
}}
.persona .field::before {{ display: none; }}
.persona .field:last-child {{ border-bottom: none; padding-bottom: 0; }}

@media (max-width: 720px) {{
  body {{ padding: 32px 16px 48px; }}
  .header {{ padding: 40px 28px 32px; }}
  .header h1 {{ font-size: 26px; }}
  .field {{ padding: 24px 22px 22px 28px; }}
  .field-label {{ gap: 10px; }}
  .competitor-row {{ grid-template-columns: 1fr; gap: 4px; padding: 12px 0; }}
  .competitor-row .copy-btn--mini {{ margin-left: 0; margin-top: 6px; align-self: flex-start; }}
  .competitor-row-label {{ font-size: 9px; }}
  .products-table thead {{ display: none; }}
  .products-table tr {{ display: block; border-bottom: 1px solid var(--rule); padding: 12px 0; }}
  .products-table td {{ display: block; padding: 8px 0; border-bottom: none; }}
}}

@media print {{
  body {{ background: white; padding: 24px; }}
  body::before, body::after {{ display: none; }}
  .field, .header, .competitor {{ box-shadow: none; page-break-inside: avoid; }}
  .copy-btn, .copy-all, .pill .pill-icon {{ display: none; }}
}}
"""

    js = """
// Tab switching
document.addEventListener('click', (e) => {
  const tabBtn = e.target.closest('.tab-button');
  if (tabBtn) {
    const tab = tabBtn.getAttribute('data-tab');
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('is-active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('is-active'));
    tabBtn.classList.add('is-active');
    document.querySelector(`.tab-panel[data-tab-panel="${tab}"]`).classList.add('is-active');
    return;
  }
});

// Click-to-copy
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-copy]');
  if (!btn) return;
  const text = btn.getAttribute('data-copy');
  navigator.clipboard.writeText(text).then(() => {
    btn.classList.add('copied');
    const originalHtml = btn.innerHTML;
    if (btn.classList.contains('pill')) {
      btn.innerHTML = '<span class="pill-text">✓ Copied</span>';
    } else {
      btn.innerHTML = '✓ Copied';
    }
    setTimeout(() => {
      btn.classList.remove('copied');
      btn.innerHTML = originalHtml;
    }, 1200);
  });
});
"""

    footer_left = brand.FOOTER_LEFT or ""
    footer_right = brand.FOOTER_RIGHT or ""

    fonts_link = (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link rel="stylesheet" href="{attr(brand.GOOGLE_FONTS_URL)}">'
        if getattr(brand, "GOOGLE_FONTS_URL", None) else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(client_name)} — HubSpot Company Context</title>
{fonts_link}
<style>{css}</style>
</head>
<body>
<div class="container">
  <div class="header">
    {logo_html}
    <h1>
      <span class="h1-client">{esc(client_name)}</span>
      <span class="h1-page">HubSpot AI Context</span>
    </h1>
    <div class="subtitle">Field-by-field paste sheet · Generated {esc(research_date)}</div>
  </div>
  {body}
  <div class="footer">
    <div>{esc(footer_left)}</div>
    <div>{esc(footer_right)}</div>
  </div>
</div>
<script>{js}</script>
</body>
</html>
"""


def validate_persona_records(icps: list, personas: list) -> None:
    """Surface structural warnings about Persona records before the build runs.

    Catches unambiguous schema violations:
      1. Source ICP references a slug that doesn't exist in the ICPs CSV
      2. Job Titles count exceeds the documented 1-3 range

    Semantic / synthesis-quality checks (account-level pain bleed, fuzzy field
    overlap) are intentionally NOT here — they belong in the protocol where the
    rule has human judgment behind it, not in the build script where false
    positives train operators to dismiss warnings.

    Warnings go to stderr. The build proceeds regardless — these are nudges,
    not blockers.
    """
    if not personas:
        return

    icp_slugs = {(icp.get("Slug") or "").strip() for icp in icps}
    icp_slugs.discard("")

    warnings_issued = 0

    for persona in personas:
        name = (persona.get("Name") or "(unnamed)").strip()
        source_icp = (persona.get("Source ICP") or "").strip()
        job_titles_raw = (persona.get("Job Titles") or "").strip()

        # Check 1: Source ICP slug references a real ICP
        if source_icp and icps and source_icp not in icp_slugs:
            print(
                f"⚠️  Persona \"{name}\" references Source ICP "
                f"\"{source_icp}\" — no matching ICP slug found in the ICPs CSV.",
                file=sys.stderr,
            )
            warnings_issued += 1

        # Check 2: Job Titles count within 1-3
        if job_titles_raw:
            titles = [t.strip() for t in job_titles_raw.replace("\n", ";").split(";") if t.strip()]
            if len(titles) > 3:
                print(
                    f"⚠️  Persona \"{name}\" has {len(titles)} job titles "
                    f"(field map rule: 1-3 max — narrower than the parent ICP).",
                    file=sys.stderr,
                )
                warnings_issued += 1
            elif len(titles) == 0:
                print(
                    f"⚠️  Persona \"{name}\" has no Job Titles "
                    f"(field map rule: 1-3 required).",
                    file=sys.stderr,
                )
                warnings_issued += 1

    if warnings_issued:
        print(f"   ({warnings_issued} validation warning(s) — non-blocking)", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Build the HubSpot AI Context paste sheet HTML — a tabbed page covering "
                    "Business, Customers (ICPs + Personas), and Brand Kit. "
                    "Mirrors HubSpot's 2026-05-28 AI Context tab structure."
    )
    parser.add_argument("data_path", help="Path to JSON data dict (Business tab fields)")
    parser.add_argument(
        "--icps",
        help="Optional path to an ICPs CSV (schema in references/hubspot-icp-fields.md). "
             "When provided, the Customers tab's ICP section is populated.",
        default=None,
    )
    parser.add_argument(
        "--personas",
        help="Optional path to a Personas CSV (schema in references/hubspot-persona-fields.md). "
             "When provided, the Customers tab's Personas section is populated.",
        default=None,
    )
    parser.add_argument(
        "output_path", nargs="?",
        help="Output HTML path (defaults to alongside data file).",
    )
    args = parser.parse_args()

    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"Error: data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(data_path.read_text())

    icps = []
    if args.icps:
        icp_path = Path(args.icps)
        if not icp_path.exists():
            print(f"Warning: ICP CSV not found: {icp_path} — generating without ICPs.", file=sys.stderr)
        else:
            icps = load_icps(icp_path)

    personas = []
    if args.personas:
        persona_path = Path(args.personas)
        if not persona_path.exists():
            print(f"Warning: Personas CSV not found: {persona_path} — generating without Personas.", file=sys.stderr)
        else:
            personas = load_personas(persona_path)

    # Surface non-blocking structural warnings about Persona records (dangling
    # Source ICP refs, Job Titles count outside the documented 1-3 range) before
    # the build. Warnings go to stderr; the build proceeds regardless.
    validate_persona_records(icps, personas)

    if args.output_path:
        out_path = Path(args.output_path)
    else:
        slug = data.get("client_slug", data_path.stem)
        out_path = data_path.parent / f"{slug}-hubspot-paste-sheet.html"

    brand = load_brand()
    html_str = build_html(data, brand, icps=icps, personas=personas)
    out_path.write_text(html_str)
    icp_msg = f", {len(icps)} ICPs" if icps else ""
    persona_msg = f", {len(personas)} Personas" if personas else ""
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes{icp_msg}{persona_msg})")


if __name__ == "__main__":
    main()
