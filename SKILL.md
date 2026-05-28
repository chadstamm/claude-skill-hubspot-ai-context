---
name: hubspot-ai-context
description: Fill HubSpot's AI Context page (Business tab + Customers tab — ICPs and Personas) by crawling a client website, researching competitors and brand reputation (positive + negative), and generating click-to-copy paste-sheet HTML. Use when setting up a new client in HubSpot's AI/Breeze Intelligence layer or when refreshing existing context. Triggers — "fill out AI context", "set up HubSpot ICPs", "create paste sheet for [client]", "generate Breeze Intelligence context", "research competitors for [client]".
---

# HubSpot AI Context — Paste Sheet Generator

This skill turns HubSpot's "set up your AI" workflow into a repeatable protocol. It covers the HubSpot **AI Context page** (page name verified 2026-05-28 after HubSpot's late-May reorganization):

1. **Business tab** — Identity & classification, Location & scale, Business profile (10 fields including Mission, Vision, NPS, Positive/Negative associations), Market & ecosystem context, Tech stack, Products & services (structured per-row database).
2. **Customers tab** — ICPs (per-row database with 10 fields each) AND Personas (separate per-row database with 4 fields each — Personas are a new concept since the 2026-05-28 reorg).
3. **Brand Kit** — managed via a separate "Manage Brand Kits" surface that HubSpot links out from the Business tab. Same Brand Kit fields as before (Personality, Default Tone, Mission, Terms to avoid, Replacement rules); the paste sheet keeps them on a dedicated tab even though HubSpot's UI now hosts them separately.

**Out of scope:** the Team & Processes tab (user-level fields like User Profile and Email personality — these are per-user data, not company AI context, and aren't generated from a website crawl).

Output: per-client paste-sheet HTML files with click-to-copy on every value, sized to the rate at which HubSpot's UI accepts pasted picklist tags and per-row record creation.

## When to use this skill

Trigger when the user says any of:
- "Fill out AI context for [client]"
- "Set up HubSpot ICPs (and Personas) for [client]"
- "Generate the Breeze Intelligence context"
- "Build the paste sheet for [client]"
- "Research competitors for [client] in HubSpot"
- "Refresh [client]'s HubSpot context"

Do NOT use this skill for: HubSpot CRM data ops, workflow building, email campaigns, Team & Processes / User Profile fields, or any other non-AI-Context HubSpot task.

## Inputs

Required:
- **Client website URL** — the canonical domain to crawl

Optional but improves quality:
- **Existing client context folder** — if the user already maintains per-client knowledge files (profile, voice profile, goals, etc.), pass the folder path. The skill reads them in addition to the crawl.
- **Custom field map** — to override the bundled HubSpot field maps (e.g., when HubSpot ships new fields).

## Default behavior — Business tab AND ICPs AND Personas in one run

When the user triggers the skill (e.g., "fill out HubSpot AI context for example.com"), the default behavior is to generate **all three artifacts** in the same run:
1. Business tab paste content (covers all sections except Team & Processes)
2. ICP records (Customers tab → top section)
3. Persona records (Customers tab → bottom section, derived from ICPs)

Reason: all three share the same crawl, the same client folder reads, and the same Phase 1.5 intake answers. Doing them together is faster, more accurate (Personas benefit from the same ICP synthesis context), and matches how HubSpot's UI groups them across the new Business + Customers tabs.

**The user opts OUT explicitly:**
- "Just the Business tab" / "skip Customers" / "Business only" → run Phases 1–5 (no ICPs, no Personas)
- "Just the ICPs" / "no Personas" → run Phases 1–3 + ICP phases, skip Persona derivation
- "Just the Personas" → still requires ICPs (Personas derive from them); run full Customers tab path
- Otherwise → run everything, in order: Business tab (Phases 1–5), then ICPs (Phase ICP-1 to ICP-3), then Personas (Phase Persona-1 to Persona-2), then a single Phase 6 hand-off.

The user can adjust ICP count inline ("...and 7 ICPs" / "just 3 ICPs"). Default is 5. Persona count derives 1–3 personas per ICP based on whether the account is single-decision-maker or buying-committee.

## Outputs

Always produces, in order:

1. **Markdown source** — `output/[client-slug]-hubspot-context.md` (the field-by-field paste content as plain markdown for archival or text-based review)
2. **Per-client products reference** — `output/[client-slug]-products.md` (durable record of every product/service from the deep crawl — feeds HubSpot's per-product Description field with synthesized one-line versions)
3. **Per-client competitors + reputation file** — `output/[client-slug]-competitors.md` (from Phase 3.5 — includes positive AND negative associations now)
4. **ICPs CSV** — `output/[client-slug]-icps.csv` (when ICPs are in scope; schema documented in Phase ICP-3)
5. **Personas CSV** — `output/[client-slug]-personas.csv` (when Personas are in scope; schema documented in Phase Persona-2)
6. **Branded HTML paste sheet** — `output/[client-slug]-paste-sheet.html` (click-to-copy interactive paste sheet — three tabs: Business · Customers · Brand Kit)

Open `output/[client-slug]-paste-sheet.html` in the user's default browser at the end of the run.

## Protocol — Business tab

### Phase 1: Validate Inputs (silent)

1. **Resolve the canonical domain.** If the user passed a folder path, read its `foundation.md` or equivalent for the canonical URL. If only a domain was passed, use it directly.
2. **Read the three bundled field maps:**
   - `references/hubspot-company-context-fields.md` — Business tab fields (ground-truth list, section structure, picklist constraints, character limits)
   - `references/hubspot-icp-fields.md` — ICP form fields (10 fields, picklist brackets)
   - `references/hubspot-persona-fields.md` — Persona form fields (4 fields)
   If HubSpot's UI has changed, update these files rather than papering over the change inside the protocol.
3. **Locate the data-dict templates** — `templates/company-context-data.example.json` is the schema the build script consumes.

### Phase 1.5: Get Client Context (always run)

After validating the domain and BEFORE crawling, surface a single up-front question to the user about what context they have. Real-world client context is messy — it might be a Google Doc, a Notion page, scattered notes, a brand brief PDF, or nothing structured. Don't assume `profile.md` exists in a folder somewhere.

**Ask this question — verbatim is fine, paraphrase is fine — once at the start:**

*"Before I crawl, do you have any context for this client I should read? You can:*
- *Paste it directly here (Google Docs content, Notion export, brand brief, sales notes — anything goes)*
- *Give me a file or folder path and I'll read whatever's there*
- *Say 'nope' and I'll ask 4 quick questions instead"*

**Branch on the response:**

**Branch A — User pastes content directly.**
Capture everything they paste. Write it to `output/[slug]-quick-context.md` verbatim under a heading like `## Pasted Context (from user, [date])`. Proceed to Phase 2.

**Branch B — User gives a file or folder path.**
- If a single file: read the file. Write a copy or summary into `output/[slug]-quick-context.md`.
- If a folder: read every markdown/text file in the folder (not picky about filenames). Common patterns to favor when present: any file matching `profile`, `voice`, `brand`, `goals`, `notes`, `brief`, `foundation`, `huddle`, or `learnings` in the name. But read ALL `.md`, `.txt`, `.json`, `.csv` in the folder regardless — users name files unpredictably.
- If the path doesn't exist or has no readable files, fall back to the intake interview (Branch C).

**Branch C — User says "nope" / "no context" / "I don't have anything".**
Run the four-question intake interview. Ask one at a time (never stack). Append each answer to `output/[slug]-quick-context.md` under the matching heading.

**Question 1 — Strategic priorities.**
*"What are 1–2 strategic priorities for this company that aren't obvious from their website? Things like: pivoting upmarket, launching a new vertical, consolidating product line, recovering from a launch miss. If you don't know, just say 'skip' and I'll work from the site alone."*

**Question 2 — Voice anti-patterns.**
*"Are there words or phrases this company specifically avoids in content? (e.g., 'we never say synergy', 'they hate the word disruptive', 'avoid leverage as a verb'.) These go directly into HubSpot's Terms to avoid field. Skip if unsure."*

**Question 3 — Target audiences.**
*"Who are the top 3–5 personas this company sells to? A short list — concrete role + segment, like 'VP of Engineering at mid-market SaaS' or 'Director of Operations at multi-site healthcare systems'. This sharpens the ICP synthesis (and seeds the Persona derivation). Skip if unsure."*

**Question 4 — Active campaigns or constraints.**
*"Any current campaigns, product launches, or competitive moves the AI context should reflect? Things HubSpot's AI shouldn't accidentally contradict. Skip if none."*

After all four are answered (including skips), confirm and proceed to Phase 2.

### Phase 2: Crawl the Site — Two Required Passes

**Pass A: Discovery (parallel)**

Pull, in parallel:
- Homepage
- `/about` or `/about-us/` (try common variants)
- Products / services index page (`/products/`, `/solutions/`, `/services/`)
- Blog index (`blog.[domain]` or `[domain]/blog`)
- `sitemap.xml` if accessible

Extract verbatim taglines, value-prop language, mission/vision language, social-responsibility mentions, voice samples, stakeholder/partner mentions, founding-year and headcount-style signals, **and the full list of product/service names with their detail-page URLs**.

**Pass B: Per-product deep crawl (parallel — REQUIRED, not optional)**

Fetch every individual product/service detail page identified in Pass A. For an SKU-rich client, that is 8–15+ fetches in parallel. Do NOT shortcut by inferring product descriptions from the homepage or index page — those are marketing summaries, not the operational detail HubSpot's per-product Description field needs.

For each product page extract: full description, dimensions/specs, materials/construction, use cases, differentiators, pricing tier or category. The durable `products.md` file holds the full depth; HubSpot's Description gets a synthesized one-line version.

**Pass C (optional): high-signal supporting pages**

If still under-supplied for any field, pull 3–5 signature blog posts, case studies, or testimonials.

**Why two passes:** A homepage product list yields one-line summaries. HubSpot's per-product DB is one of the most-used downstream surfaces by Breeze, AI search, and sales — depth matters. Even though the per-product Description field accepts only concise descriptor-style text, the synthesis quality comes from having the full per-product spec to compress from.

### Phase 3: Read Existing Client Context

Sources, in priority order (read all that exist, in parallel):

1. **Quick-context file** from Phase 1.5 — `output/[slug]-quick-context.md`. Treat user-provided answers as authoritative.
2. **Client folder** — if the user passed a folder path, read in parallel any of these files that exist:
- `profile.md` — operational profile, ICPs, contacts, org structure
- `voice-profile.md` — written/blog voice analysis
- `voice-learnings.md` — voice corrections accumulated over time
- `foundation.md` — auto-load paths to external assets
- `goals.md` — active campaigns, priorities, recent decisions
- `huddle-notes.md` — recurring meeting notes
- `products.md` — durable product reference (often built by a previous run of this skill)

These augment the website crawl. The website tells you what the client SAYS publicly; the folder tells you what's TRUE operationally.

### Phase 3.5: Competitor + Reputation Research (web)

The 2026-05-28 HubSpot UI reorganization added a **Positive associations** field (counterpart to the existing Negative associations field). Phase 3.5 now produces BOTH outputs from the same research pass — don't only look for negative signals.

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

**C. Reputation scan for the client + each top competitor (positive + negative).**

Run web searches across these surfaces for the client and (lighter pass) each top competitor:
- General reputation: `"[Firm Name]" reviews complaints reputation`
- Industry trade press (positive coverage, customer wins, awards)
- Trustpilot, BBB-style listings
- Reddit (note: WebSearch coverage of Reddit is partial)
- LinkedIn employee posts, Glassdoor — also partial
- Google Business reviews if a public listing exists
- Customer testimonials on the client's own site (positive associations)

For each finding, capture verbatim quotes + source URL. Bucket into:
- **Positive associations** — testimonials, trade-press wins, third-party praise, "things customers consistently say good about"
- **Negative associations** — complaints, friction signals, "things customers consistently say bad about"

If nothing surfaces on the negative side after a thorough pass, that's a finding too — write `"No significant negative associations found in public web as of [Month YYYY]"` for the Negative associations field. Don't claim "clean" without evidence; don't leave blank.

**D. Persist findings.**

Write `output/[client-slug]-competitors.md`:
- Top 5–10 competitors with HQ, territory/coverage, focus, source URL
- Flag any "also a customer" or "also a partner" relationships
- Date the research (the field decays — competitors come and go)

Append a "Reputation Scan" section to the same file with two subsections:
- **Positive findings** — quotes/sources for the Positive associations field
- **Negative findings** — quotes/sources for the Negative associations field
- Date of scan
- Caveats on what surfaces were not deeply scanned

This file becomes durable research — re-read on future runs instead of re-crawling unless >90 days stale.

### Phase 4: Synthesize Field-by-Field (Business tab)

Walk every field in `references/hubspot-company-context-fields.md` in the section order HubSpot's UI shows. Apply discipline:

- **First-person plural** ("we, our") in long-form fields where the client speaks in first person
- **Operational specificity** over hype — pull verbatim site language where possible
- **Respect HubSpot limits** — Mission ≤ 50 words (per Brand Kit convention; verify the new Business profile Mission field shares this limit on first paste), Terms to avoid ≤ 20 words, Personality + Default tone ≤ 4 each (verify in the field map for the latest)
- **Personality and Default Tone are FIXED PICKLISTS.** Only suggest values present in the picklist documented in the Brand Kit fields section. If a perfect-fit voice trait isn't in the picklist, pick the closest valid option — never invent a tag.
- **Never fabricate or hallucinate data.** This is the hardest rule. If a field can't be derived from the crawl + folder + Phase 3.5 research, leave it blank in the data dict — the build script automatically renders empty fields as a visible `[Confirm with client]` placeholder. Every field on every HubSpot tab MUST appear in the output paste sheet (even if empty) so nothing silently disappears. Better to have a visible flag than a fabricated value or a missing section.

**Order to walk fields:**

1. **Brand Kits** (paste-sheet tab; goes to HubSpot's external Brand Kit surface):
   - Personality (picklist)
   - Default tone (picklist)
   - Mission (≤50 words)
   - Terms to avoid (≤20 words)
   - Replacement rules
   - Inclusivity toggles (client-only)
2. **Identity and classification** (Business tab):
   - Name (Legal name)
   - Domain
   - Industry (single value — sub-fields collapsed in 2026-05-28 reorg)
   - Type (Public / Private)
3. **Location and scale** (Business tab):
   - Headquarters location (free text, "City, State, Country")
   - Company size (picklist — "11 – 50 employees" en-dash format)
   - Annual revenue (picklist — client-required for private companies)
   - Founded year (numeric)
4. **Business profile** (Business tab):
   - Business description (long-form textarea, 1–3 sentences)
   - Unique value propositions (multi-tag picklist, 10–15 tags typical)
   - Business model (short text input, ~80 chars)
   - Primary business goal (short text input, ~80 chars)
   - Mission (multi-paragraph textarea — may or may not be synced with Brand Kit Mission)
   - Vision (multi-paragraph textarea — NEW field, aspirational future-state)
   - Social responsibility (multi-tag, 8–12 tags)
   - NPS score (client-only — flag)
   - Positive associations (multi-tag — from Phase 3.5)
   - Negative associations (multi-tag — from Phase 3.5)
5. **Market and ecosystem context** (Business tab):
   - Main competitors (multi-tag — from Phase 3.5)
   - Stakeholders (multi-tag — NEW field; parent companies, regulators, certifying bodies, channel partners)
6. **Technology stack** (Business tab):
   - Existing apps and tools (multi-tag — business-facing apps from About / blog / partnerships pages)
   - Technology stack (key tools) (multi-tag — Breeze auto-detect + manual)
7. **Products and services** (Business tab — structured DB):
   - One record per product. Each record: Name (required) · Description (concise descriptor style) · Category (1–2 word category)

Always-flag fields (cannot be derived without the client):
- **NPS score** — client-only data
- **Annual revenue** — client-only for private companies
- **Inclusivity toggles** — client preference call (may or may not have moved with the reorg; verify)

Researched in Phase 3.5 (populate from the competitors file, don't blank-flag):
- **Main competitors** — pull from the competitors file
- **Positive associations** — pull from the Positive findings subsection
- **Negative associations** — pull from the Negative findings subsection

### Phase 5: Generate Outputs (Business tab → paste sheet)

The skill produces **one tabbed HTML paste sheet** with three tabs (color-coded per HubSpot's UI logic):

- **Tab 1 — Business** (terracotta accent): Identity & classification, Location & scale, Business profile (all 10 fields), Market & ecosystem context, Tech stack, Products & services (one click-to-copy card per product)
- **Tab 2 — Customers** (rumo-blue accent): ICPs (one card per ICP, 10 fields per card) + Personas (one card per persona, 4 fields per card)
- **Tab 3 — Brand Kit** (signature teal accent): Personality, Default Tone, Mission, Terms to Avoid, Replacement Rules + Open Items

Tabs map to HubSpot's UI grouping (Business / Customers / external Brand Kit). Each tab is independently scrollable; alternating accent colors signal which tab is active.

Write these files to `output/`:

1. **Per-client products reference:** `[client-slug]-products.md` — durable, deeper-than-HubSpot record of every product/service from Pass B. Categories at top (table), then per-product blocks with URL, models, specs, differentiators, and an "open product data gaps" section.
2. **Per-client competitors + reputation file:** `[client-slug]-competitors.md` — from Phase 3.5. Includes Positive findings, Negative findings, and Top competitors sections.
3. **Per-client data dict:** `[client-slug]-data.json` — structured input for the HTML build script. Schema in `templates/company-context-data.example.json` (updated for the 2026-05-28 reorg field structure).
4. **ICPs CSV** (only if ICPs are in scope): `[client-slug]-icps.csv` — column order specified in Phase ICP-3 below.
5. **Personas CSV** (only if Personas are in scope): `[client-slug]-personas.csv` — column order specified in Phase Persona-2 below.
6. **Tabbed HTML paste sheet:** Run

   ```
   python scripts/build_company_context_html.py output/[client-slug]-data.json output/[client-slug]-paste-sheet.html --icps output/[client-slug]-icps.csv --personas output/[client-slug]-personas.csv
   ```

   The `--icps` and `--personas` flags are omitted when the user opted to skip those scopes.

Open `output/[client-slug]-paste-sheet.html` in the default browser at the end of the run. **One file. Three tabs. The user clicks between them as they paste each section into HubSpot's matching UI surface.**

### Phase 6: Hand Off

Print a short summary:
- Files written (paths)
- Field count: total / synthesized / flagged for client input
- Top synthesis decisions worth the user's eye (anything opinionated — picklist swaps, taxonomy overrides, tone changes from existing settings)
- Open items list (numbered, copy-pasteable for client confirmation)

Then stop. Don't ask "want me to do X next?" — let the user direct the next step.

## Protocol — ICPs

### Phase ICP-1: Identify the ICP set

**Default count: 5 ICPs** (range 3–7 — fewer than 3 misses meaningful segments; more than 7 dilutes synthesis). If the user explicitly asks for a different count, honor it.

Two paths:

- **Pre-built ICP library exists** — the user maintains a per-industry library of ICPs (e.g., a CSV with one row per ICP). Match the client's stated target audiences to library entries. Generate a per-client subset by selecting library rows that match the client's verticals.
- **Greenfield** — derive ICPs from the website crawl + Phase 1.5 intake answers (especially Question 3 — "top 3-5 personas"). Look for "we serve" language on the homepage, case study verticals, blog audience signals, customer testimonials, and any explicit ICPs in the user's intake. If the client has a multi-channel model (sells direct AND through partners), include both end-users and channel partners.

**Generate the ICPs directly — do NOT pause for confirmation.** The HTML paste sheet is the review surface. The user inspects there, drops any ICP they don't want by simply not pasting it into HubSpot, or asks for adjustments after seeing the rendered output.

### Phase ICP-2: Synthesize fields per ICP

For each ICP, populate the form fields per `references/hubspot-icp-fields.md` (10 fields). Quality bar:

| Field | Bar |
|---|---|
| **Name** | Concrete role + segment, not generic. "VP of Engineering at mid-market SaaS" not "Engineering Buyer." |
| **Description** | 1–2 sentence summary of who this ICP is and why they buy. **Native HubSpot field as of 2026-05-28 reorg** (was an "extra" before). Fold in any Buying Triggers / Decision Context signals here (the old "Other" field is gone). |
| **Business type** | Operational category (e.g., "Mid-Market SaaS", "Healthcare System", "Distribution Channel Partner", "K-12 School District"). **Native HubSpot field as of 2026-05-28 reorg.** |
| **Job titles** | 5–10 titles, semicolon-separated. Include senior + mid + procurement variants. Items often contain commas internally (e.g., "Director, Operations") — this is why semicolons separate. |
| **Interests** | 5–7 specific phrases describing buying motivations, decision drivers, segment-specific concerns. Items often contain commas — semicolon-separate. |
| **Industries** | 2–4 industry tags. Picklist values where HubSpot enforces them. (Plural label in 2026-05-28 reorg — was singular "Industry".) |
| **Locations** | At least one country/region. Multi-select picklist (placeholder reads "Select a location" but the field accepts multi-select — confirmed with Chad 2026-05-28). Click-to-copy pills + Copy-all with semicolons. **Foodservice ICPs default to `United States; Canada`. Hyperscaling / data center ICPs commonly include `United States; Canada; Mexico`.** For other industries, default to `United States` if primary; surface as a question if the client's footprint is broader. |
| **Company size** | 2–4 picklist brackets covering the ICP's typical org size. **New bracket format in HubSpot UI: `11 – 50 employees` (en-dash + " employees" suffix).** Old default brackets to verify: `1-10, 11-50, 51-200, 201-500, 501-1K, 1K-5K, 5K-10K, 10K-50K, 50K-100K, 100K+`. |
| **Annual revenue** | 2–4 picklist brackets. **Renamed from "Revenue".** Default brackets to verify: `Less than $1M, $1M-$10M, $10M-$50M, $50M-$100M, $100M-$500M, $500M-$1B, $1B-$10B, $10B+`. |
| **Age range** | Buyer age (decision-maker), not end-customer. Default brackets: `18-24, 25-34, 35-44, 45-54, 55-64, 65+`. Most B2B ICPs are 35-54. |

**Fields removed in the 2026-05-28 reorg:**
- The old `Other` long-form text field — GONE. The PAIN POINTS / BUYING TRIGGERS / DECISION CONTEXT content that lived there now routes to:
  - **Pain Points** → Persona records (see Phase Persona-2 below)
  - **Buying Triggers** + **Decision Context** → fold into ICP Description (1 sentence synthesis each)

### Phase ICP-3: Generate ICP outputs

**Write the CSV** at `output/[client-slug]-icps.csv` with this exact header (column order matters — the build script reads by column name):

```
"Grouping","Category","Name","Description","Business Type","Job Titles","Industries","Locations","Company Size","Annual Revenue","Age Range","Interests","Slug"
```

Quote every cell. Newlines inside cells are fine if they're inside the quoted string. `Slug` is `slugify(Name)` — lowercase, hyphens for spaces, no punctuation.

`Grouping` and `Category` are display-only labels (e.g., Grouping = the client's industry; Category = "End-User Operator", "Channel Partner", or "Specifier").

**Notes on the new CSV schema (changes from pre-2026-05-28):**
- Removed: `Other` column
- Renamed: `Industry` → `Industries`, `Location` → `Locations`, `Revenue` → `Annual Revenue`
- `Description` and `Business Type` are still in the same columns but are now native HubSpot fields (they used to be "extras")

**The ICPs render in Tab 2 of the unified tabbed paste sheet** — see Phase 5 for the build script invocation.

Click-to-copy renders within Tab 2 ICP cards:
- **Locations** as click-to-copy pills + Copy-all with semicolons
- **Job Titles, Industries, Company Size, Annual Revenue, Age Range, Interests** as semicolon-separated text with single Copy buttons
- **Name, Description, Business Type** as single Copy buttons (textarea fields)

## Protocol — Personas

### Phase Persona-1: Derive the Persona set from ICPs

Personas are individual-buyer-level records that live on the same Customers tab as ICPs. Each ICP drives 1–3 Personas:

- **1:1** — single buying decision-maker per ICP (e.g., Parks & Recreation Director ICP → Parks & Recreation Director Persona). Typical for small organizations with consolidated authority.
- **1:N** — buying-committee ICP with multiple decision-makers (e.g., K-12 Buyer ICP → Superintendent + Director of Facilities + Procurement Manager). Typical for larger / regulated organizations.

To decide 1:1 vs 1:N per ICP: look at the ICP's `Company Size` and `Business type` fields. Small orgs (1-50 employees) usually map 1:1. Medium-to-large orgs (200+) and regulated verticals (healthcare, government, K-12) usually map 1:N.

### Phase Persona-2: Synthesize fields per Persona

For each Persona, populate the form fields per `references/hubspot-persona-fields.md` (4 fields). Quality bar:

| Field | Bar |
|---|---|
| **Name** | Specific role + (optionally) segment. "Parks & Recreation Director", "K-12 Director of Facilities", "Independent Landscape Architect". Single concrete role, not a category. |
| **Job Titles** | Required. 1–3 titles this individual goes by (narrower than the ICP's Job titles list). E.g., "Parks & Recreation Director", "Director, Parks", "Parks Superintendent". |
| **Value Propositions** | What resonates with THIS specific buyer (may differ from company-wide UVPs). 3–6 role-resonant phrases. "Reduces my evening proposal-review workload" beats "AI-powered proposal scoring". |
| **Pain Points** | **Migration target for the pre-reorg ICP "Other" Pain Points content.** 4–8 operational frictions this buyer faces, as individual tags. Translate up from account-level pain ("budget constraints") to role-level pain ("scoring lowest-bid proposals when I know the cheap option will fail"). |

**Write the CSV** at `output/[client-slug]-personas.csv` with this header:

```
"Source ICP","Name","Job Titles","Value Propositions","Pain Points","Slug"
```

Quote every cell. `Source ICP` references the parent ICP's `Slug` so the build script can group personas under their ICPs on the Customers tab if desired (rendering decision in the build script).

**The Personas render in Tab 2 of the unified tabbed paste sheet** alongside ICPs — see Phase 5 for the build script invocation.

Click-to-copy renders within Tab 2 Persona cards:
- **Job Titles, Value Propositions, Pain Points** as semicolon-separated text with single Copy buttons
- **Name** as a single Copy button

## Branding

The build scripts ship with the **CS2 brand by default** (Chad Stamm — author/maintainer brand: signature teal accent + Yankee blue text + cool paper background, Montserrat + Open Sans). The output is editorial and visually distinct from any common client brand (deliberately not orange-on-warm-sand, which is TMC's territory).

### CRITICAL RULE — DO NOT AUTO-CREATE BRAND OVERRIDES

When running this skill, **NEVER auto-generate a `brand-override.local.py` file based on inference about who the user is or what brand they work for.** Brand overrides are USER-PROVIDED, not skill-derived. The skill defaults to CS2 brand; if the user wants a different brand applied, they must drop their own `brand-override.local.py` in the working directory before running.

This rule exists because:
- The user's CLAUDE.md or memory files may mention employers, clients, or brand colors. A well-meaning Claude will infer "I should apply that brand," which is the wrong call — the user invoked the *public skill*, expecting the *public default*.
- Auto-created overrides leak the user's workplace identity into outputs that may be shared externally.
- Override files persist in the output directory and silently affect every future run from that CWD — a single bad inference contaminates all subsequent paste sheets.

**Specifically forbidden actions during any skill run:**
- Writing a `brand-override.local.py` file anywhere
- Labeling output markdown source files with a brand other than CS2 (e.g., `**Brand:** TMC` is forbidden unless the user explicitly requested TMC branding via passing their own override)
- Inferring brand color choices from memory or CLAUDE.md content
- "Helpfully" customizing the paste sheet aesthetic based on the client being researched (the client gets HubSpot-formatted data, not branding decisions)

If the user explicitly says *"apply my [TMC / Acme / X] brand to this output"*, then route them to: *"Drop a `brand-override.local.py` in this directory with your color palette and re-run"*, OR ask them to share the override values and write the file ONLY after explicit confirmation. Never infer.

### Override structure (for users)

To apply your own brand:
- Drop a `brand-override.local.py` in the directory you run the build script from. The build script auto-loads it.
- See `templates/brand-override.example.py` for the override structure (color palette, fonts, optional Google Fonts URL, optional logo).

## Notes

- **Verify the field maps first** if HubSpot changes its AI Context UI. Don't paper over field changes inside the protocol — update `references/hubspot-company-context-fields.md`, `references/hubspot-icp-fields.md`, and `references/hubspot-persona-fields.md` as needed.
- **Don't overwrite an existing markdown source** without diffing — users may have edited a paste sheet post-generation.
- **Industry directory mappings are user-extensible.** Edit `references/industry-directories.md` to add canonical directories and search patterns for the industries you work in. The skill reads this file each run.
- **The skill is opinionated.** Synthesis decisions are documented inline. When you make an opinionated call (picklist swap, taxonomy override, tone shift), call it out in Phase 6 hand-off so the user can sharpen.
- **2026-05-28 reorg legacy note:** the pre-reorg structure had tabs Products & Services / Brand Kit / ICPs. The new tabs are Business / Customers / Brand Kit. If you encounter old paste sheets or older client data dicts, the `[client-slug]-data.json` schema documents how old fields map to new fields.
