# HubSpot AI Context — Customers Tab → ICP Field Map

Canonical reference for HubSpot's "Create ICP" form (lives on the Customers tab of the AI Context page, post the late-May 2026 UI reorganization).

This is the ground-truth field list. If HubSpot's UI changes again, edit this file rather than papering over the change inside the skill protocol.

**Tab:** Customers
**Section description (HubSpot):** "Define the characteristics of your ideal customers."
**Database structure:** Each ICP is a row in the Ideal Customer Profiles table (columns: Name · Description · Business Type · Updated By · Updated Date · Actions). Click "Add ICP" to open the create form.

**Last UI capture:** 2026-05-28 (verified against a live B2B client portal's 8 existing ICPs from a May 25, 2026 generation run).

---

## Create ICP form fields (in popup order)

| # | Field | Type | Required | Notes |
|---|---|---|---|---|
| 1 | **Name** | textarea (single-line equivalent) | **Yes** | The ICP label. Concrete role + segment, not generic. E.g., "Parks & Recreation Director", "K-12 School Playground Buyer", "Landscape Architect (Playground Specifier)". Avoid generic labels like "Operations Buyer". |
| 2 | **Description** | textarea | No | 1–2 sentence summary of who this ICP is and why they buy. **Now a NATIVE HubSpot field** (was an "extra" in the pre-reorg schema). For ICPs that previously had Buying Triggers or Decision Context bundled in the old "Other" field, fold those signals into the Description here (since the "Other" field is gone). |
| 3 | **Business type** | textarea | No | Operational category (e.g., "Municipal Government", "K-12 School District", "Healthcare System", "Distribution Channel Partner", "Landscape Architecture Firm"). **Now a NATIVE HubSpot field** (was an "extra" in the pre-reorg schema). |
| 4 | **Job titles** | multi-tag (free-form, type+Enter) | No | Job titles within accounts of this type. 5–10 titles per ICP. Items often contain commas internally (e.g., "Director, Parks & Recreation"). The form accepts them as separate tag entries via Enter; semicolons are the safe separator when pasting multiple at once into the type-ahead field. |
| 5 | **Interests** | multi-tag (free-form, type+Enter) | No | Buying motivations, decision drivers, segment-specific concerns. 5–7 phrases. Items often contain commas → use semicolons as the safe separator for paste. |
| 6 | **Industries** | multi-tag (free-form, type+Enter) | No | Industries the ICP operates in. **Plural label** (was singular "Industry" in pre-reorg schema). 2–4 industry tags typical. |
| 7 | **Locations** | multi-select picklist (by nation) | No | Country/region tags. **⚠️ 2026-07-08: NOT visible in Chad's latest live form capture** (Industries flows straight into Company sizes) — Locations may have been REMOVED in a HubSpot UI update. Verify in the live portal before including it in a paste sheet. *(Prior guidance:* North American foodservice ICPs default to `United States; Canada`.) |
| 8 | **Company sizes** | multi-select picklist | No | **Plural label.** No-space hyphen, abbreviated K/M, NO "employees" suffix (distinct from Business-tab). 2–4 brackets. Picklist (verified **2026-07-08 from Chad's live screenshots**): `1-10`, `11-50`, `51-250`, `251-1K`, `1K-5K`, `5K-10K`, `10K-50K`, `50K-100K`, `100K-500K`, `500K-1M`, `1M-2M`. **⚠️ CHANGED 2026-07-08:** old `100K+` split into `100K-500K` / `500K-1M` / `1M-2M`; spacing `" - "` → `"-"`. |
| 9 | **Revenue ranges** | multi-select picklist | No | **Relabeled "Revenue ranges" (was "Annual revenue"/"Revenue").** No-space hyphen. 2–4 brackets. Picklist (verified **2026-07-08 from Chad's live screenshots**): `$0-$1M`, `$1M-$10M`, `$10M-$50M`, `$50M-$100M`, `$100M-$250M`, `$250M-$500M`, `$500M-$1B`, `$1B-$10B`, `$10B-$50B`, `$50B-$100B`, `$100B-$500B`, `$500B-$1T`. **⚠️ CHANGED 2026-07-08:** old `$10B+` split into `$10B-$50B` / `$50B-$100B` / `$100B-$500B` / `$500B-$1T`; spacing. |
| 10 | **Age ranges** | multi-select picklist | No | **Plural label.** Buyer age (decision-maker), not end-customer. Picklist (verified **2026-07-08 from Chad's live screenshots**): `0-12`, `13-17`, `18-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65-74`, `75-84`, `85-94`, `95-125`. Most B2B ICPs are 35-54. **⚠️ CHANGED 2026-07-08:** `<12`→`0-12`, `12-17`→`13-17`, old `65+` split into `65-74` / `75-84` / `85-94` / `95-125`. |

## Fields gone from the pre-2026-05-28 schema

- **Other** (long-form text) — REMOVED. The old "Other" field bundled `PAIN POINTS:`, `BUYING TRIGGERS:`, `DECISION CONTEXT:` sections. Routing for that content in the new structure:
  - **Pain Points** → moved to Persona-level (see `hubspot-persona-fields.md`)
  - **Buying Triggers** → fold into ICP Description (1 sentence synthesis)
  - **Decision Context** → fold into ICP Description (1 sentence synthesis)

## Fields promoted from "extras" to native

These two were tracked as "extras not in HubSpot's Create ICP form" in the pre-reorg schema, but are now native HubSpot fields:

- **Description** — native (field #2 above)
- **Business type** — native (field #3 above)

## Field rendering recommendations (for paste-sheet HTML)

For pastable HTML output:

- **Multi-select picklist by nation (Locations)** → render as click-to-copy pills, one per country, plus a `Copy all` button with semicolon separators (`United States; Canada`). HubSpot accepts both one-at-a-time and semicolon-separated paste behaviors here.
- **Free-text multi-tag fields** (Job titles, Interests, Industries) → render as semicolon-separated text blocks with one Copy button. Items frequently contain commas internally; semicolons are the safe separator.
- **Picklist multi-select with no internal commas** (Company size, Annual revenue, Age range) → render as semicolon-separated text. Values must match HubSpot's picklist options exactly.
- **Textarea fields** (Name, Description, Business type) → single Copy button per field, no separators.

## Common HubSpot UI quirks

- **Picklist fields require exact matches** — as of **2026-07-08** the ICP form picklists use **no-space hyphens**, abbreviated K/M, and NO "employees" suffix (e.g., `51-250`, `251-1K`, `$250M-$500M`) — distinct from the Business-tab Company size (full numbers + " employees"). Match HubSpot's exact option strings. **(The old `" - "` spaced format is retired — HubSpot changed it. Any pre-2026-07-08 paste sheet has the wrong spacing AND is missing the new high-end brackets.)**
- **Job titles, Interests, Industries are free-text type-ahead** but HubSpot may auto-suggest from your portal's existing contact/company database; pasted values bypass suggestions.
- **Pasting one big string at once** sometimes splits unexpectedly on commas. Semicolon-separated paste is more predictable when items contain internal commas.
- **Locations is multi-select but the placeholder reads "Select a location"** (singular UI text on a multi-select control). Don't assume single-select from the placeholder.

## ICP → Persona derivation pass

Each ICP record should drive 1–3 Persona records on the same Customers tab. See `hubspot-persona-fields.md` for the Persona schema. Typical derivation:

- **1:1** — single buying decision-maker per ICP (e.g., Parks & Recreation Director ICP → Parks & Recreation Director Persona)
- **1:N** — buying-committee ICP with multiple decision-makers (e.g., K-12 Buyer ICP → Superintendent Persona + Director of Facilities Persona + Procurement Manager Persona)

The Persona Pain Points field is where ICP-level pain signals (formerly bundled in ICP Other) now land — at the persona granularity, not account-level.
