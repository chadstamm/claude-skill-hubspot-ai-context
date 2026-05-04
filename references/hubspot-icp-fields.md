# HubSpot Ideal Customer Profile (ICP) — Field Map

Canonical reference for HubSpot's "Create Ideal Customer Profile" form.

This is the ground-truth field list. If HubSpot's UI changes, edit this file rather than papering over the change inside the skill protocol.

---

## Form fields (verified 2026-05-04)

| # | Field | Type | Required | Notes |
|---|---|---|---|---|
| 1 | Name | text | Yes | The ICP label (e.g., "K-12 School Nutrition Director", "Multi-Unit Restaurant Equipment Buyer") |
| 2 | Job Titles | multi-tag (free text) | No | Each title pasted individually. Items often contain commas → semicolons are the natural item separator when copying multiple at once. |
| 3 | Industry | multi-tag (free text) | No | Industries the ICP operates in. |
| 4 | Location | multi-tag (HubSpot picklist — country/region tags) | No | Click-to-add country tags. Source values must match HubSpot's location picklist. |
| 5 | Company Size | multi-tag (HubSpot picklist) | No | Common picklist options: `1-10`, `11-50`, `51-200`, `201-500`, `501-1K`, `1K-5K`, `5K-10K`, `10K-50K`, `50K-100K`, `100K+`. Verify against HubSpot UI. |
| 6 | Revenue | multi-tag (HubSpot picklist) | No | Common picklist options: `Less than $1M`, `$1M-$10M`, `$10M-$50M`, `$50M-$100M`, `$100M-$500M`, `$500M-$1B`, `$1B-$10B`, `$10B+`. Verify. |
| 7 | Age Range | multi-tag (HubSpot picklist) | No | Common picklist options: `18-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65+`. Verify. |
| 8 | Interests | multi-tag (free text) | No | Buying motivations, decision drivers, segment-specific concerns. Items often contain commas → semicolons are the natural item separator. |
| 9 | Other | long-form text | No | Free text. Pain points, buying triggers, market context, anything that doesn't fit the structured fields above. |

## Optional / "extras" not in HubSpot's Create ICP form

These don't appear in the form but are useful to keep alongside each ICP for AI-content-generation context:

| Field | Type | Notes |
|---|---|---|
| Description | text | 1–2 sentence summary of who this ICP is and why they buy. Useful when feeding ICPs into other AI workflows. |
| Business Type | text | Operational category (e.g., "Multi-Unit Restaurant Chain", "Healthcare System", "Equipment Distributor"). Some HubSpot AI features use this. |

## Field rendering recommendations (for paste-sheet HTML)

For pastable HTML output:

- **Multi-tag picklist fields** (Location only) → render as click-to-copy pills, one per item. HubSpot's Location field is one-tag-at-a-time.
- **Free-text multi-value fields** (Job Titles, Industry, Interests) → render as a single semicolon-separated text block with one Copy button. Items frequently contain commas internally; semicolons are the safe separator.
- **Free-text picklist fields where items don't contain commas** (Company Size, Revenue, Age Range) → also render as semicolon-separated text. The values themselves still must match HubSpot's picklist options exactly.
- **Long-form text** (Other, Description, Business Type) → single Copy button, no separators.

This rendering pattern matches how HubSpot's UI actually accepts the data when pasted.

## Common HubSpot UI quirks

- **Picklist fields require exact matches** — `1-10` works, `1 to 10` does not. Always verify the punctuation HubSpot expects.
- **Job Titles, Industry, and Interests are free-text** but HubSpot may auto-suggest from your company database; pasted values bypass suggestions.
- **Pasting one big string at once** sometimes splits unexpectedly on commas. Semicolon-separated paste is more predictable when items contain internal commas.
