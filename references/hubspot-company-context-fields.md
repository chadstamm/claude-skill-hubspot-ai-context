# HubSpot AI Context — Business Tab Field Map

Canonical reference for HubSpot's "AI Context" page → **Business tab** (the page that replaced the old "Company Context" page in HubSpot's late-May 2026 UI reorganization).

This is the ground-truth field list. If HubSpot's UI changes again, edit this file rather than papering over the change inside the skill protocol.

**Page name:** AI Context
**Subtitle:** "Information, facts, and knowledge about your organization that enhances and powers AI across HubSpot."
**Tab structure:** Business · Customers · Team & Processes (this file covers Business only — Customers fields are in `hubspot-icp-fields.md` and `hubspot-persona-fields.md`; Team & Processes is out of scope for this skill since those fields are per-user, not company-context).

**Last UI capture:** 2026-05-28 (verified against a live B2B client portal).

---

## ⚠ 2026-06-05 CORRECTION — live UI verified

The live AI Context UI spans TWO surfaces. Verified against a live client portal; the build script (`scripts/build_company_context_html.py`) renders both. This overrides any conflicting claim below.

**Surface 1 — AI Context page → Business tab** (structured Edit-card sections, top to bottom):
1. **Brand Kits** (visual brand-kit list; "Manage Brand Kits" link).
2. **Identity and classification** — Name (Legal name), Domain, **Industry (SINGLE field)**, Type (Public/Private).
3. **Location and scale** — Headquarters location, Company size, Annual revenue, Founded year.
4. **Business profile** — Business description, Unique value propositions, Business model, Primary business goal, Mission, Vision, **Social responsibility**, **Customer sentiment** (NPS + Positive associations + Negative associations).
5. **Market and ecosystem context** — Main competitors, **Stakeholders**.
6. **Technology stack** — Existing apps and tools, Technology stack (key tools).
7. **Products and services** — per-product Name / Description / Category (paginated DB).

**Surface 2 — Brand Kit page** (opened via "Manage Brand Kits"; = the build script's Brand Kit tab):
- **Brand voice** — Personality, Default Tone, Mission, Terms to Avoid, Replacement Rules, **Inclusivity**.
- **Additional context** (crawl-derived; Data / Content / Source columns) — six subsections, DISTINCT from the Business-tab fields:
  - **Industry classification** — Industry, Sub-industry, Industry group, Business sector, Industry-related tags (the FIVE-field version; the Business tab keeps a single Industry).
  - **Customer sentiment** — NPS, Positive associations, Negative associations.
  - **Competitive landscape** — Competitive advantages, Main competitors (Stakeholders is NOT here; it lives in Business-tab Market and ecosystem context).
  - **Content themes** — Primary content topics, Content format types.
  - **Tech stack** — Technologies, Technology categories.
  - **Social responsibility** — Supported social causes, Sustainability initiatives.

**Build-script tab mapping:** Business tab = Identity (single Industry) / Location / Business profile (with Social responsibility + Customer sentiment) / Market and ecosystem context / Technology stack / Products. Brand Kit tab = Brand voice + the six Additional-context subsections.

**Data keys for the Additional-context subsections** (see `templates/company-context-data.example.json`): `sub_industry`, `industry_group`, `business_sector`, `industry_related_tags`, `competitive_advantages`, `content_themes`, `content_format_types`, `technologies`, `technology_categories`, `supported_social_causes`, `sustainability_initiatives`, `inclusivity`.

**Company size picklist (Business tab):** `1 – 10` · `11 – 50` · `51 – 250` · `251 – 1,000` · `1,000 – 5,000` · `5,000 – 10,000` · `10,000 – 50,000` · `50,000 – 100,000` · `100,000+` employees. (ICP-form picklists differ — see `hubspot-icp-fields.md`.)

---

## Section 1 — Brand Kits

**Location:** Top of Business tab.
**Behavior:** Now a separate management surface (not edited inline). Opens via "Manage Brand Kits" button to an external Brand Kit editor.

The AI Context page shows only a list of existing Brand Kits (Name + Updated Date) with a "Manage Brand Kits" link button.

Per the skill's paste-sheet design, Brand Kit fields still ship as a paste-sheet tab even though HubSpot now hosts them on a separate UI surface — having them at hand during the AI Context fill is faster than tab-switching mid-task. See "Brand Kit fields (managed separately)" below.

### Brand Kit fields (managed separately)

| Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|
| Personality | multi-tag (HubSpot **fixed picklist** — see below) | Yes | 4 max | Voice analysis. **Pick ONLY from the picklist.** |
| Default tone | multi-tag (HubSpot **fixed picklist** — see below) | Yes | 4 max | Voice analysis. **Pick ONLY from the picklist.** |
| Mission | text | No | **50 words** | Site (About, footer) + existing context. Note: Mission also appears under Business profile (Section 4) — HubSpot may keep these in sync or treat them as separate. Verify on first paste. |
| Terms to avoid | multi-word | No | **20 words** | Voice analysis (avoid lists in any voice profile) |
| Replacement rules | case-sensitive word→word | No | none visible | Voice analysis (replacement rules in any voice profile) |
| Inclusivity | 3 toggles | No | n/a | Client preference (3 checkboxes: gender-neutral / cultural / global idioms). May or may not have moved with the reorg — verify on first paste. |

#### Personality picklist (verified 2026-04-29; assume unchanged in 2026-05-28 reorg unless verified otherwise)

Adventurous, Authentic, Bold, Charismatic, Compassionate, Curious, Diverse, Down-to-earth, Driven, Dynamic, Eccentric, Edgy, Elegant, Helpful, Human, Innovative, Irreverent, Kind, Nurturing, Professional, Quirky, Rebellious, Relatable, Sophisticated, Supportive, Thoughtful, Trustworthy

**27 options. NEVER suggest a Personality value outside this list.** Common LLM-generated picks that fail HubSpot validation: "Knowledgeable", "Practical", "Direct", "Confident" — none exist in HubSpot's Personality picklist (some live in the Default Tone picklist instead).

#### Default Tone picklist (verified 2026-04-29; assume unchanged in 2026-05-28 reorg unless verified otherwise)

Affectionate, Assertive, Authoritative, Businesslike, Casual, Cheerful, Colloquial, Commanding, Compassionate, Confident, Contemplative, Conversational, Corporate, Courteous, Cynical, Deferential, Doubtful, Earnest, Educational, Empathetic, Encouraging, Energetic, Enlightening, Enthusiastic, Excited, Fanciful, Formal, Friendly, Funny, Grave, Hopeful, Humorous, Immediate, Impartial, Incredulous, Informal, Informative, Insistent, Inspirational, Instructive, Introspective, Inviting, Ironical, Literal, Loving, Matter-of-fact, Mocking, Motivating, Neutral, Objective, Optimistic, Passionate, Playful, Polite, Positive, Precise, Pressing, Professional, Questioning, Quirky, Reflective, Relaxed, Respectful, Romantic, Sarcastic, Serious, Skeptical, Solemn, Straightforward, Sympathetic, Technical, Unbiased, Understanding, Unemotional, Uplifting, Urgent, Warm, Whimsical, Witty

**~80 options. NEVER suggest a Default Tone value outside this list.**

**Important:** "Direct" is NOT in the picklist. Closest analogues for direct/clear voices: **Straightforward, Matter-of-fact, Assertive, Commanding, Authoritative.**

---

## Section 2 — Identity and classification

**HubSpot description:** "Foundational company identifiers, including its legal name, web domain, industry classification, and ownership structure."

| Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|
| Name (Legal name) | text | Likely yes | none visible | Site footer / About / legal page. Use the full legal entity name. |
| Domain | text (URL) | Likely yes | none visible | Canonical web domain. |
| Industry | single value | Likely yes | none visible | **Single industry classification** — Breeze may auto-populate. Override with human-readable name if needed. The pre-reorg "Industry Classification" 5-field cluster (Industry / Sub-Industry / Industry Group / Business Sector / Industry-Related Tags) has collapsed to a single Industry field in the new UI. |
| Type (Public/Private) | picklist (likely Public / Private; possibly Nonprofit / Other) | No | n/a | Site footer / About / "About us". |

**Deprecated from pre-2026-05-28 structure:**
- Sub-Industry (gone)
- Industry Group (gone)
- Business Sector (gone)
- Industry-Related Tags (gone — possibly absorbed by other multi-tag fields elsewhere)

---

## Section 3 — Location and scale

**HubSpot description:** "Core firmographic indicators capturing where the company is based, its size and revenue footprint, and when it was established."

| Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|
| Headquarters location | text (free-form, single line) | No | none visible | "City, State, Country" format works (e.g., "Chattanooga, Tennessee, United States"). |
| Company size (employee count) | picklist | No | n/a | Bracket format: `11 – 50 employees` (en-dash + " employees" suffix). Derive from LinkedIn company page if not on site. |
| Annual revenue | picklist | No | n/a | "Select a range" dropdown. Source from public filings if available, otherwise leave for client to confirm. |
| Founded year | numeric text input | No | 4 digits | Year only (e.g., `1976`). Source: About page, Wikipedia, or LinkedIn. |

---

## Section 4 — Business profile

**HubSpot description:** "Company's core identity, including what it offers, who it serves, how it creates differentiated value, how it monetizes, and its primary business objective."

| # | Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|---|
| 1 | Business description | textarea (long-form) | No | none visible | Site-derivable (homepage hero, About page). 1–3 sentences. |
| 2 | Unique value propositions | multi-tag (free-form, type+Enter) | No | rich (10–15 tags typical) | Site-derivable (homepage USPs, About differentiators, product detail pages). One UVP per tag. |
| 3 | Business model | short text input (single line) | No | likely ~80 chars | One-line description of how the company operates and monetizes. E.g., "Design, manufacture, product sales and project-based installation." |
| 4 | Primary business goal | short text input (single line) | No | likely ~80 chars | One-line statement of the company's primary mission/objective. E.g., "Creating fun, inclusive, and imaginative play spaces that inspire joy and well-being for everyone." |
| 5 | Mission | textarea (multi-paragraph) | No | likely ≤50 words per Brand Kit convention | Site (About, footer) + existing client context. **May or may not be synced with the Brand Kit's Mission field — verify on first paste.** |
| 6 | Vision | textarea (multi-paragraph) | No | none visible | **NEW field in 2026-05-28 reorg** (separate from Mission). Aspirational future-state statement. Site (About, leadership pages). |
| 7 | Social responsibility | multi-tag (free-form) | No | rich (8–12 tags typical) | Site (About, blog, CSR / impact pages). Each social-cause or community-impact theme as one tag. |
| 8 | NPS score | numeric input | No | 0–100 | Client-required — not derivable from website. Flag `[Confirm with client]`. |
| 9 | Positive associations | multi-tag (free-form) | No | rich (10–15 tags typical) | **NEW field in 2026-05-28 reorg.** Phase 3.5 reputation research now produces positive findings too, not just negative. Pull from reviews, testimonials, trade press, customer quotes. |
| 10 | Negative associations | multi-tag (free-form) | No | none visible | Renamed from "Negative Brand Associations". Off-site research (reviews, forums, Reddit, BBB, Glassdoor, Google Business). If empty, write `"No significant negative associations found in public web as of [Month YYYY]"` rather than leaving blank. |

**Read-only view note:** HubSpot's read-only display rolls fields 8/9/10 into a single "Customer sentiment" display row (e.g., "NPS: 60"). The edit popup reveals them as three separate fields. Paste sheet renders each independently.

**Deprecated from pre-2026-05-28 structure:**
- "Value Proposition" single-text field → split into Business description + Unique value propositions
- "What pain points does your company solve?" → gone from Business tab. Pain Points are now a **Persona-level** field (see `hubspot-persona-fields.md`).
- "Itemized products or services" single-field → now a structured DB (see Section 7 below).

---

## Section 5 — Market and ecosystem context

**HubSpot description:** "A view of the company's competitive landscape and the key stakeholders that influence, enable, or are impacted by its success."

| Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|
| Main competitors | multi-tag (free-form) | No | rich (5–10 typical) | Off-site research (industry directory + web search). Phase 3.5 in the skill protocol covers this. |
| Stakeholders | multi-tag (free-form) | No | rich | **NEW field in 2026-05-28 reorg.** Non-competitor parties that influence the business: parent companies, regulators, certifying bodies, key channel partners, contract vehicles. Pull from About page + financial disclosures + partnership pages. |

**Deprecated from pre-2026-05-28 structure:**
- "Competitive Advantages" bullet list → folded into Unique Value Propositions (Business profile section).

---

## Section 6 — Technology stack

**HubSpot description:** "An overview of the core applications and technology stack that power the business."

| Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|
| Existing apps and tools | multi-tag (free-form) | No | rich | Business-facing apps the company uses (e.g., procurement cooperatives, channel platforms, ERP). Derive from About, blog mentions, channel pages. |
| Technology stack (key tools) | multi-tag (Breeze auto-detect + manual) | No | rich | Web/cloud infrastructure (Apache, asp_net, AWS, etc.). Breeze auto-populates via BuiltWith-style detection; manual additions allowed. Tags often stay lowercase_with_underscores. |

---

## Section 7 — Products and services

**HubSpot description:** "Product offerings, pricing, and service details."

**Format change:** This section is now a **structured database** (one row per product/service), replacing the single "Itemized products or services" text field from the pre-reorg structure.

### Per-product record fields

| # | Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|---|
| 1 | Name | short text input | **Yes (required)** | none visible | Product or service name. Pulled from product/services index pages. |
| 2 | Description | textarea | No | none visible / no documented limit | Concise descriptor style (the HubSpot sample reads as comma-separated descriptor list, not full prose). One-line to one-paragraph synthesis of what the product is and what it does. |
| 3 | Category | free text (behavior may vary — possibly Breeze-derived suggestions) | No | none visible | Free text by default; HubSpot may suggest categories via Breeze. Synthesis: derive a 1–2 word category from the product family (e.g., "Playground line", "Service / Toolkit", "Inclusive design"). |

### Workflow

1. User clicks "Add Product or Service" → opens the per-product edit popup.
2. User pastes Name, Description, Category individually.
3. Save → record appears in the Products and services table.
4. Repeat per product.

**Paste-sheet rendering implication:** One click-to-copy card per product, each with three independently copyable fields. For SKU-rich clients (50+ products typical), that's a substantial card stack — but the workflow is mechanical and parallel-pasteable.

**Durable per-client products reference (`output/[slug]-products.md`)** retains the full per-product depth from Phase 2 Pass B (dimensions, materials, differentiators, model numbers, URLs). HubSpot's Description field gets the synthesized one-line version pulled from that file.

---

## What changed between the pre-2026-05-28 structure and now

### Renamed

| Old | New |
|---|---|
| Negative Brand Associations | Negative associations |
| Positive Brand Associations | Positive associations |
| Revenue | Annual revenue |
| Industry | Industries (on ICP form — Business tab keeps singular "Industry") |
| Location | Locations (on ICP form — Business tab has "Headquarters location") |

### Newly added (no pre-reorg equivalent)

- Type (Public/Private)
- Headquarters location
- Company size (employee count)
- Annual revenue
- Founded year
- Business model
- Primary business goal
- Vision (separate from Mission)
- Stakeholders
- Positive associations (counterpart to existing Negative)
- Per-product Category field on the Products and services records

### Structural changes

- "Products and services" is now a structured DB (per-row records), not a single text field
- Brand Kit moved to a separate external surface (still listed on Business tab as a link-out only)
- ICPs moved to their own tab (Customers) — see `hubspot-icp-fields.md`
- Personas are now a separate concept from ICPs (also on Customers tab) — see `hubspot-persona-fields.md`

### Gone entirely

- Sub-Industry / Industry Group / Business Sector / Industry-Related Tags (Industry Classification cluster collapsed to single Industry field)
- "What pain points does your company solve?" (moved to Persona-level — see `hubspot-persona-fields.md`)
- Competitive Advantages (folded into Unique value propositions)
- Sustainability Initiatives (folded into Social responsibility)
- Primary Content Topics / Content Format Types (no replacement visible — Content Themes section appears to be gone from AI Context)
- ICP "Other" field (gone — content split between ICP Description and Persona Pain Points)

---

## Source-strategy summary

- **Site-derivable** (homepage crawl + About is enough): Name, Domain, Type, HQ location, Founded year, Business description, UVPs, Business model, Primary business goal, Mission, Vision, Social responsibility, Stakeholders
- **Voice-analysis required** (existing client context + voice profile read): Personality, Default Tone, Terms to avoid, Replacement rules
- **Off-site research required (Phase 3.5)**: Main competitors, Positive associations, Negative associations
- **Breeze auto-populates, may need override**: Industry, Technology stack (key tools)
- **Per-product deep crawl required (Phase 2 Pass B)**: Products and services (Name + Description + Category per record)
- **Client must provide**: NPS score, Company size (if not on LinkedIn), Annual revenue (if private), Inclusivity preferences (if applicable)
