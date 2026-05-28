# HubSpot AI Context — Customers Tab → Persona Field Map

Canonical reference for HubSpot's "Create Persona" form (lives on the Customers tab of the AI Context page, post the late-May 2026 UI reorganization).

**Persona is a new concept in the 2026-05-28 reorganization** — the pre-reorg schema only had ICPs. Personas now sit alongside ICPs on the Customers tab, capturing individual-buyer-level traits (role, pain points, value-prop resonance) that previously got bundled into ICPs.

**Tab:** Customers
**Section description (HubSpot):** "Define the types of buyers your business targets."
**Database structure:** Each Persona is a row in the Personas table (columns: similar to ICPs, with Name as the primary identifier). Click "Add Persona" to open the create form.

**Last UI capture:** 2026-05-28.

---

## ICP vs Persona — conceptual split

| | ICP | Persona |
|---|---|---|
| **Granularity** | Account / company-level | Individual buyer / decision-maker |
| **Example** | "K-12 School Playground Buyer" (the type of district / institution that buys) | "K-12 Director of Facilities" (the specific person within that district who signs off) |
| **Primary fields** | Industry, Company size, Annual revenue, Location, Job titles within the account | Job titles for THIS specific role, Value Propositions that resonate, Pain Points |
| **Volume** | 3–8 typical per client | 1–3 per ICP — often 1:1, sometimes 1:N for buying-committee accounts |

---

## Create Persona form fields (in popup order)

| # | Field | Type | Required | Notes |
|---|---|---|---|---|
| 1 | **Name** | single-line text | **Yes** | The Persona label. Specific role + (optionally) segment. E.g., "Parks & Recreation Director", "K-12 Director of Facilities", "Independent Landscape Architect". Should be a single concrete role, not a category. |
| 2 | **Job Titles** | multi-tag (free-form, type+Enter) | **Yes** | The specific title(s) this individual goes by. Narrower than the ICP's Job titles list. Often 1–3 titles per Persona (e.g., "Parks & Recreation Director", "Director, Parks", "Parks Superintendent"). |
| 3 | **Value Propositions** | multi-tag (free-form, type+Enter) | No | What resonates with THIS specific buyer (may differ from the company-wide UVPs on the Business profile). Persona-level UVPs are typically more specific and role-driven. 3–6 tags per Persona. |
| 4 | **Pain Points** | multi-tag (free-form, type+Enter) | No | **The migration target for ICP-level Pain Points from the pre-reorg schema.** Each operational friction this buyer faces, as a single tag. 4–8 tags per Persona typical. Items often contain commas → use semicolons for paste. |

---

## Field rendering recommendations (for paste-sheet HTML)

- **Single-line text** (Name) → single Copy button.
- **Free-text multi-tag fields** (Job Titles, Value Propositions, Pain Points) → render as semicolon-separated text blocks with one Copy button per field. Optionally render individual click-to-copy pills for high-tag-count fields. Items often contain commas; semicolons are the safe separator.

---

## ICP → Persona derivation discipline

When generating Personas from ICPs, hold these synthesis rules:

1. **One Persona per Buying Decision-Maker.** If an ICP's account has a single decision-maker (e.g., a small parks department where the Director signs everything), generate 1 Persona. If the account is committee-driven (K-12 districts with a Superintendent + Facilities Director + Procurement Manager), generate one Persona per voting role.
2. **Don't reuse ICP Pain Points wholesale.** The ICP had pain at account level ("budget constraints", "insufficient inclusive equipment"). The Persona has pain at role level ("scoring lowest-bid proposals when I know the cheap option will fail", "explaining to the board why we're paying more"). Translate up.
3. **Value Propositions on Persona should be role-resonant, not feature-listy.** "Reduces my evening proposal-review workload" beats "AI-powered proposal scoring".
4. **Job Titles on Persona is narrower than on ICP.** ICP lists every title that exists in the account (5–10 titles); Persona lists only the titles this specific role goes by (1–3 titles).
5. **Optional Value Propositions field — if you can't pull strong role-specific UVPs from the client context, leave it blank and let the client refine.** Half-derived UVPs are worse than blank.

---

## Common HubSpot UI quirks

- **Job Titles is required** on Persona (unlike on ICP where it's optional). At least one title must be entered before save.
- **Pasting comma-separated values** into the type-ahead field may auto-split unexpectedly. Semicolon-separated paste is more predictable.
- **Persona records are independent of ICP records** in HubSpot's data model — you can have Personas with no matching ICP, and ICPs with no derived Persona. The conceptual mapping is something the skill maintains in synthesis; HubSpot doesn't enforce a relationship.
