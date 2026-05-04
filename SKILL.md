---
name: hubspot-ai-context
description: Fill HubSpot's Company Context and Ideal Customer Profile (ICP) pages by crawling a client website, researching competitors and brand reputation, and generating click-to-copy paste-sheet HTML. Use when setting up a new client in HubSpot's AI/Breeze Intelligence layer or when refreshing existing context. Triggers — "fill out company context", "set up HubSpot ICP", "create paste sheet for [client]", "generate Breeze Intelligence context", "research competitors for [client]".
---

# HubSpot Context — Company Context & ICP Paste Sheets

This skill turns HubSpot's "set up your AI" workflow into a repeatable protocol. It covers two HubSpot pages:

1. **Company Context** — top-of-page positioning, brand voice, industry classification, competitors, negative brand associations, content topics, technologies (~30 fields).
2. **Ideal Customer Profile (ICP)** — Name, Job Titles, Industry, Location, Company Size, Revenue, Age Range, Interests, Other (~9 fields per ICP, often 3–8 ICPs per client).

Output: per-client paste-sheet HTML files with click-to-copy on every value, sized to the rate at which HubSpot's UI accepts pasted picklist tags one at a time.

## When to use this skill

Trigger when the user says any of:
- "Fill out company context for [client]"
- "Set up HubSpot ICPs for [client]"
- "Generate the Breeze Intelligence context"
- "Build the paste sheet for [client]"
- "Research competitors for [client] in HubSpot"
- "Refresh [client]'s HubSpot context"

Do NOT use this skill for: HubSpot CRM data ops, workflow building, email campaigns, or any non-Company-Context / non-ICP HubSpot task.

## Inputs

Required:
- **Client website URL** — the canonical domain to crawl

Optional but improves quality:
- **Existing client context folder** — if the user already maintains per-client knowledge files (profile, voice profile, goals, etc.), pass the folder path. The skill reads them in addition to the crawl.
- **Custom field map** — to override the bundled HubSpot field map (e.g., when HubSpot ships new fields).

## Outputs

Always produces, in order:

1. **Markdown source** — `output/[client-slug]-hubspot-context.md` (the field-by-field paste content as plain markdown for archival or text-based review)
2. **Branded HTML paste sheet** — `output/[client-slug]-hubspot-context.html` (click-to-copy interactive paste sheet)
3. **Per-client products reference** — `output/[client-slug]-products.md` (durable record of every product/service from the deep crawl)
4. **Per-client competitors file** — `output/[client-slug]-competitors.md` (from Phase 3.5 research)
5. **Optional: ICP paste sheet** — `output/[client-slug]-icps.html` (when the user asks for ICPs in the same run)

Open the HTML paste sheets in the user's default browser at the end of the run.

## Protocol — Company Context

### Phase 1: Validate Inputs (silent)

1. **Resolve the canonical domain.** If the user passed a folder path, read its `foundation.md` or equivalent for the canonical URL. If only a domain was passed, use it directly.
2. **Read the bundled field map** — `references/hubspot-company-context-fields.md`. This is the ground-truth list of HubSpot fields, types, picklist constraints, and character limits. If HubSpot's UI has changed, update this file rather than papering over the change inside the protocol.
3. **Locate the data-dict template** — `templates/company-context-data.example.json` is the schema the build script consumes.

### Phase 2: Crawl the Site — Two Required Passes

**Pass A: Discovery (parallel)**

Pull, in parallel:
- Homepage
- `/about` or `/about-us/` (try common variants)
- Products / services index page (`/products/`, `/solutions/`, `/services/`)
- Blog index (`blog.[domain]` or `[domain]/blog`)
- `sitemap.xml` if accessible

Extract verbatim taglines, value-prop language, mission language, social/sustainability mentions, voice samples, and **the full list of product/service names with their detail-page URLs**.

**Pass B: Per-product deep crawl (parallel — REQUIRED, not optional)**

Fetch every individual product/service detail page identified in Pass A. For an SKU-rich client, that is 8–15+ fetches in parallel. Do NOT shortcut by inferring product descriptions from the homepage or index page — those are marketing summaries, not the operational detail HubSpot's Itemized Products field needs.

For each product page extract: full description, dimensions/specs, materials/construction, use cases, differentiators, pricing tier or category. The Itemized Products table should match the depth a sales engineer would write, not a homepage hero.

**Pass C (optional): high-signal supporting pages**

If still under-supplied for any field, pull 3–5 signature blog posts, case studies, or testimonials.

**Why two passes:** A homepage product list yields one-line summaries. The HubSpot Itemized Products field is one of the most-used fields downstream by Breeze, AI search, and sales — depth matters.

### Phase 3: Read Existing Client Context (if provided)

If the user passed an existing client folder, read in parallel any of these files that exist:
- `profile.md` — operational profile, ICPs, contacts, org structure
- `voice-profile.md` — written/blog voice analysis
- `voice-learnings.md` — voice corrections accumulated over time
- `foundation.md` — auto-load paths to external assets
- `goals.md` — active campaigns, priorities, recent decisions
- `huddle-notes.md` — recurring meeting notes
- `products.md` — durable product reference (often built by a previous run of this skill)

These augment the website crawl. The website tells you what the client SAYS publicly; the folder tells you what's TRUE operationally.

### Phase 3.5: Competitor + Reputation Research (web)

Don't punt Main Competitors and Negative Brand Associations to "client confirms" — research them. The HubSpot fields are stronger if they're populated with signal, even imperfect signal the user can sharpen.

**A. Identify the client's business model first.**

Read the client folder (or infer from the crawl) to determine which model applies:
- **Manufacturer's rep / rep-distributor hybrid** → industry's canonical rep directory (each industry has one — search "[industry] manufacturers rep association")
- **Manufacturer / OEM** → industry trade association
- **Distributor / dealer** → regional dealer associations + industry trade press
- **Marketing/services firm** → web search by category + region
- **SaaS / digital** → product-category competitive lists (G2, Capterra, etc.)
- **Other** → web search by category + region

The skill is industry-neutral. To improve research quality for a specific industry, optionally add directory URLs and search patterns to `references/industry-directories.md` (an editable file the skill reads each run).

**B. Pull the canonical directory or peer set for that business model.**

For the matched industry directory, query for firms in the client's region(s) or category. Cross-reference with any client-specific notes ("known competitors per [contact]") if provided.

**C. Reputation scan for the client + each top competitor.**

Run web searches across these surfaces for the client and (lighter pass) each top competitor:
- General reputation: `"[Firm Name]" reviews complaints reputation`
- Industry trade press
- Trustpilot, BBB-style listings
- Reddit (note: WebSearch coverage of Reddit is partial)
- LinkedIn employee posts and Glassdoor — also partial
- Google Business reviews if a public listing exists

For each finding, capture verbatim quotes + source URL. If nothing surfaces after a thorough pass, that's a finding too — write `"No significant negative associations found in public web as of [Month YYYY]"` for the Negative Brand Associations field. Don't claim "clean" without evidence; don't leave blank.

**D. Persist findings.**

Write `output/[client-slug]-competitors.md`:
- Top 5–10 competitors with HQ, territory/coverage, focus, source URL
- Flag any "also a customer" or "also a partner" relationships
- Date the research (the field decays — competitors come and go)

Append a "Reputation Scan" section:
- Surfaces checked
- Quotes/findings (if any) with source URLs
- Date of scan
- Caveats on what surfaces were not deeply scanned

This file becomes durable research — re-read on future runs instead of re-crawling unless >90 days stale.

### Phase 4: Synthesize Field-by-Field

Walk every field in the field map. Apply discipline:
- **First-person plural** ("we, our") in long-form fields where the client speaks in first person
- **Operational specificity** over hype — pull verbatim site language where possible
- **Respect HubSpot limits** — Mission ≤ 50 words, Terms to Avoid ≤ 20 words, Personality + Default Tone ≤ 4 each (verify in the field map for the latest)
- **Personality and Default Tone are FIXED PICKLISTS.** Only suggest values present in the picklist documented in the field map. If a perfect-fit voice trait isn't in the picklist, pick the closest valid option — never invent a tag.
- **Don't fabricate.** If a field can't be derived from the crawl + folder + Phase 3.5 research, flag it `[Confirm with client]`.

Always-flag fields (cannot be derived without the client):
- **NPS** — client-only data
- **Inclusivity toggles** — client preference call

Researched in Phase 3.5 (populate from the competitors file, don't blank-flag):
- **Main Competitors** — pull from the competitors file. Note any flagged relationships.
- **Negative Brand Associations** — pull from the Reputation Scan. If empty, write `"No significant negative associations found in public web as of [Month YYYY]"` rather than leaving blank.

Always-verify fields (HubSpot's Breeze sometimes miscategorizes):
- **Sub-Industry** — Breeze frequently miscategorizes. Always sanity-check.

### Phase 5: Generate Outputs

Write four artifacts:

1. **Per-client products reference:** `output/[client-slug]-products.md` — durable, deeper-than-HubSpot record of every product/service from Pass B. Categories at top (table), then per-product blocks with URL, models, dimensions, materials, load ratings, differentiators, and a closing "open product data gaps" section.
2. **Markdown source:** `output/[client-slug]-hubspot-context.md` — field-by-field paste content as plain markdown.
3. **Per-client data dict:** `output/[client-slug]-data.json` — structured input for the HTML build script. Generate from synthesis. Schema in `templates/company-context-data.example.json`.
4. **Branded HTML paste sheet:** Run `scripts/build_company_context_html.py [client-slug]-data.json` → `output/[client-slug]-hubspot-context.html`. Click-to-copy on every individual pill (Personality, Default Tone, Terms to Avoid, Industry-Related Tags, Technologies, Tech Categories, Content Topics, Content Formats), single Copy button on long-form fields. Pain points get individual + Copy-All. Replacement rules get per-token Copy buttons.

Open `output/[client-slug]-hubspot-context.html` in the default browser.

### Phase 6: Hand Off

Print a short summary:
- Files written (paths)
- Field count: total / synthesized / flagged for client input
- Top synthesis decisions worth the user's eye (anything opinionated — picklist swaps, taxonomy overrides, tone changes from existing settings)
- Open items list (numbered, copy-pasteable for client confirmation)

Then stop. Don't ask "want me to do X next?" — let the user direct the next step.

## Protocol — ICP Paste Sheet

The ICP workflow piggybacks on the same Phase 1–3 (validate, crawl, read folder). After Phase 3, branch:

### Phase ICP-1: Identify the ICP set

Two paths:

- **Pre-built ICP library exists** — the user maintains a per-industry library of ICPs (e.g., a CSV with one row per ICP). Match the client's stated target audiences to library entries. Generate a per-client subset.
- **Greenfield** — derive ICPs from the website crawl + folder. Look for "we serve" language, case study verticals, blog audience signals, customer testimonials.

In both cases, surface the proposed ICP set to the user for confirmation BEFORE generating outputs. ICPs are opinionated; let the client validate.

### Phase ICP-2: Synthesize fields per ICP

For each confirmed ICP, populate the HubSpot ICP form fields:
- **Name** (required)
- **Job Titles** (semicolon-separated; long phrases — items often contain commas internally)
- **Industry** (semicolon-separated)
- **Location** (HubSpot picklist — e.g., country tags)
- **Company Size** (HubSpot picklist — e.g., "1-10, 11-50, 51-200, 201-500, 501-1K, 1K-5K, 5K-10K, 10K-50K, 50K-100K, 100K+")
- **Revenue** (HubSpot picklist — e.g., "Less than $1M, $1M-$10M, $10M-$50M, $50M-$100M, $100M-$500M, $500M-$1B, $1B-$10B, $10B+")
- **Age Range** (HubSpot picklist — e.g., "18-24, 25-34, 35-44, 45-54, 55-64, 65+")
- **Interests** (semicolon-separated; longer phrases describing motivations and priorities)
- **Other** (free text — pain points, buying triggers, market context)

Optional / "extras" not always shown in HubSpot's Create ICP form but useful to keep:
- **Description** (1–2 sentence summary of the ICP)
- **Business Type** (operational category like "Multi-Unit Restaurant Chain" or "Healthcare System")

See `references/hubspot-icp-fields.md` for the field map and picklist values.

### Phase ICP-3: Generate ICP outputs

1. **CSV source** — `output/[client-slug]-icps.csv`. The build script reads this.
2. **HTML paste sheet** — Run `scripts/build_icp_html.py [client-slug]-icps.csv` → `output/[client-slug]-icps.html`.

The HTML uses semicolon-separated text + single-Copy buttons for: Job Titles, Industry, Company Size, Revenue, Age Range, Interests. Location renders as click-to-copy pills (HubSpot's Location field accepts country tags individually).

Open the HTML in the default browser.

## Branding

The build scripts ship with a **neutral default palette** (clean grayscale + a single accent color, no embedded logo). To override with your own brand:
- Edit the `BRAND` config dict at the top of each build script (palette, fonts, optional logo data URI).
- See `templates/brand-override.example.py` for an annotated branded override and the minimal-neutral default side-by-side.

## Notes

- **Verify the field map first** if HubSpot changes its Company Context UI. Don't paper over field changes inside the protocol — update `references/hubspot-company-context-fields.md`.
- **Don't overwrite an existing markdown source** without diffing — users may have edited a paste sheet post-generation.
- **Industry directory mappings are user-extensible.** Edit `references/industry-directories.md` to add canonical directories and search patterns for the industries you work in. The skill reads this file each run.
- **The skill is opinionated.** Synthesis decisions are documented inline. When you make an opinionated call (picklist swap, taxonomy override, tone shift), call it out in Phase 6 hand-off so the user can sharpen.
