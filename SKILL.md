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

## Default behavior — Company Context AND ICPs in one run

When the user triggers the skill (e.g., "fill out HubSpot company context for example.com"), the default behavior is to generate **both** the Company Context paste sheet **and** the ICPs in the same run. Reason: both halves share the same crawl, the same client folder reads, and the same Phase 1.5 intake answers. Doing them together is faster, more accurate (the ICPs benefit from the same competitor/reputation research), and matches how HubSpot's UI groups them.

**The user opts OUT explicitly:**
- "Just the company context" / "skip ICPs" / "company context only" → run Company Context phases only
- "Just the ICPs" / "skip company context" → run ICP phases only (still does the crawl + research)
- Otherwise → run both, in this order: Company Context first (Phases 1–5), then ICPs (Phases ICP-1 to ICP-3), then a single combined Phase 6 hand-off.

The user can also adjust ICP count inline ("...and 7 ICPs" / "just 3 ICPs"). Default is 5.

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
*"Are there words or phrases this company specifically avoids in content? (e.g., 'we never say synergy', 'they hate the word disruptive', 'avoid leverage as a verb'.) These go directly into HubSpot's Terms to Avoid field. Skip if unsure."*

**Question 3 — Target audiences.**
*"Who are the top 3–5 personas this company sells to? A short list — like 'K-12 nutrition directors, hospital foodservice operators, fast casual chain equipment buyers'. This sharpens the ICP synthesis if we generate ICPs in the same run. Skip if unsure."*

**Question 4 — Active campaigns or constraints.**
*"Any current campaigns, product launches, or competitive moves the AI context should reflect? Things HubSpot's AI shouldn't accidentally contradict. Skip if none."*

After all four are answered (including skips), confirm and proceed to Phase 2.

The `quick-context.md` file structure:

```markdown
# [Client Name] — Quick Context (intake interview, [date])

## Strategic priorities
[user's answer]

## Voice anti-patterns
[user's answer]

## Target audiences
[user's answer]

## Active campaigns
[user's answer]
```

Phase 3 reads this file the same way it reads a real client folder — the synthesis treats user-provided answers as authoritative.

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

The ICP workflow piggybacks on the same Phase 1–3 (validate, optional intake, crawl, read folder/quick-context). After Phase 3, branch:

### Phase ICP-1: Identify the ICP set

**Default count: 5 ICPs** (range 3–7 — fewer than 3 misses meaningful segments; more than 7 dilutes synthesis). If the user explicitly asks for a different count, honor it.

Two paths:

- **Pre-built ICP library exists** — the user maintains a per-industry library of ICPs (e.g., a CSV with one row per ICP). Match the client's stated target audiences to library entries. Generate a per-client subset by selecting library rows that match the client's verticals.
- **Greenfield** — derive ICPs from the website crawl + Phase 1.5 intake answers (especially Question 3 — "top 3-5 personas"). Look for "we serve" language on the homepage, case study verticals, blog audience signals, customer testimonials, and any explicit ICPs in the user's intake. If the client has a multi-channel model (sells direct AND through partners), include both end-users and channel partners.

**Generate the ICPs directly — do NOT pause for confirmation.** The HTML paste sheet is the review surface. The user inspects there, drops any ICP they don't want by simply not pasting it into HubSpot, or asks for adjustments after seeing the rendered output. Asking permission before doing the work adds friction without adding value.

### Phase ICP-2: Synthesize fields per ICP

For each confirmed ICP, populate the HubSpot ICP form fields per the schema in `references/hubspot-icp-fields.md`. Quality bar:

| Field | Bar |
|---|---|
| **Name** | Concrete role + segment, not generic. "K-12 School Nutrition Director" not "School Buyer." |
| **Job Titles** | 5–10 titles, semicolon-separated. Include senior + mid + procurement variants. Items often contain commas internally (e.g., "Director, Operations / Strategy") — this is why semicolons separate. |
| **Industry** | 2–4 industry tags. Picklist values where HubSpot enforces them. |
| **Location** | At least one country/region. US is fine if that's the ICP's primary market. |
| **Company Size** | 2–4 picklist brackets covering the ICP's typical org size. Default brackets: `1-10, 11-50, 51-200, 201-500, 501-1K, 1K-5K, 5K-10K, 10K-50K, 50K-100K, 100K+` |
| **Revenue** | 2–4 picklist brackets. Default brackets: `Less than $1M, $1M-$10M, $10M-$50M, $50M-$100M, $100M-$500M, $500M-$1B, $1B-$10B, $10B+` |
| **Age Range** | Buyer age (decision-maker), not end-customer. Default brackets: `18-24, 25-34, 35-44, 45-54, 55-64, 65+`. Most B2B ICPs are 35-54. |
| **Interests** | 5–7 specific phrases describing buying motivations, decision drivers, segment-specific concerns. Items often contain commas — semicolon-separate. |
| **Other** | Structured free text with three sections: `PAIN POINTS:` (operational frictions), `BUYING TRIGGERS:` (events that prompt purchase), `DECISION CONTEXT:` (who decides, what they evaluate, what wins). |

Plus the two extras (not in HubSpot's Create ICP form but useful for AI context downstream):
- **Description** — 1–2 sentence summary of who this ICP is and why they buy
- **Business Type** — operational category (e.g., "Multi-Unit Restaurant Chain", "Healthcare System")

### Phase ICP-3: Generate ICP outputs

**1. Write the CSV** at `output/[client-slug]-icps.csv` with this exact header (column order matters — the build script reads by column name):

```
"Grouping","Category","Name","Description","Business Type","Job Titles","Industry","Location","Company Size","Revenue","Age Range","Interests","Other","Slug"
```

Quote every cell. Newlines inside cells are fine if they're inside the quoted string. `Slug` is `slugify(Name)` — lowercase, hyphens for spaces, no punctuation.

`Grouping` and `Category` are display-only labels (e.g., Grouping = the client's industry; Category = "End-User Operator", "Channel Partner", or "Specifier").

**2. Build the HTML paste sheet:**

```
python scripts/build_icp_html.py output/[client-slug]-icps.csv output/[client-slug]-icps.html
```

Click-to-copy renders:
- **Location** as click-to-copy pills (HubSpot's Location field is one-tag-at-a-time)
- **Job Titles, Industry, Company Size, Revenue, Age Range, Interests** as semicolon-separated text with single Copy buttons
- **Name, Other, Description, Business Type** as single Copy buttons (long-form text)

**3. Open the HTML in the default browser.**

**4. Hand off** — print a short summary: ICP count, fields-per-ICP synthesized count, fields flagged for client input, and any ICPs the user might want to add/drop after seeing them rendered.

## Branding

The build scripts ship with the **CS2 brand by default** (Chad Stamm — author/maintainer brand: terracotta + Yankee blue + Sand + Signature teal, Montserrat + Open Sans). The output looks editorial out of the box.

To override with your own brand:
- Drop a `brand-override.local.py` in your working directory. The build scripts auto-load it.
- See `templates/brand-override.example.py` for the override structure (color palette, fonts, optional Google Fonts URL, optional logo).

## Notes

- **Verify the field map first** if HubSpot changes its Company Context UI. Don't paper over field changes inside the protocol — update `references/hubspot-company-context-fields.md`.
- **Don't overwrite an existing markdown source** without diffing — users may have edited a paste sheet post-generation.
- **Industry directory mappings are user-extensible.** Edit `references/industry-directories.md` to add canonical directories and search patterns for the industries you work in. The skill reads this file each run.
- **The skill is opinionated.** Synthesis decisions are documented inline. When you make an opinionated call (picklist swap, taxonomy override, tone shift), call it out in Phase 6 hand-off so the user can sharpen.
