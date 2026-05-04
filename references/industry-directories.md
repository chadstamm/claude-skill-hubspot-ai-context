# Industry Directories — Competitor Research Plug-Ins

User-extensible map of industry-specific directories the skill can use during Phase 3.5 (Competitor + Reputation Research).

The skill is industry-neutral by default. To improve research quality for a specific industry, add directory URLs and search patterns below. The skill reads this file each run.

---

## Format

For each industry, provide:

```
### Industry name

- **Business model match:** which client business model(s) this directory serves
- **Directory URL:** canonical entry point (member directory, locator, etc.)
- **Search hint:** how the skill should query the directory (URL pattern, region codes, search params)
- **Auth required:** yes/no — does the directory gate behind a login?
- **Trade press:** industry-specific publications worth scanning for reputation
- **Notes:** anything peculiar about this industry's research surface
```

---

## Examples

The entries below are illustrative — replace, edit, or extend as you adopt the skill for your own industries.

### Example: Foodservice equipment (US)

- **Business model match:** Manufacturer's rep, rep-distributor hybrid, equipment dealer, foodservice equipment OEM
- **Directory URL (rep firms):** https://www.mafsi.org/ (public locator at `mafsi.memberclicks.net/rep_locator?servId=6783`)
- **Directory URL (dealers/distributors):** https://www.feda.com/
- **Directory URL (manufacturers):** https://www.nafem.org/
- **Search hint:** Rep firms are organized by MAFSI region (numbered). Map client territory → MAFSI region(s) → query directory by region.
- **Auth required:** MAFSI member directory is gated; the public locator returns enough firm-name signal to research from there. FEDA / NAFEM have public member lists.
- **Trade press:** FES Magazine, FoodService Equipment & Supplies (FE&S), FoodService Equipment Reports (FER)
- **Notes:** Industry has two parallel competitive lanes — rep firms compete on the manufacturer-spec side; dealers compete on the operator-fulfillment side. List both for hybrid clients.

### Example: SaaS / B2B software

- **Business model match:** SaaS vendor, B2B software platform
- **Directory URL:** https://www.g2.com/, https://www.capterra.com/, https://www.gartner.com/reviews/
- **Search hint:** Search by product category. G2's "Compare" pages list direct competitors by category.
- **Auth required:** No (public reviews); deeper data behind login.
- **Trade press:** TechCrunch, The Information, industry-vertical newsletters (for the buyer's industry, not the vendor's)
- **Notes:** SaaS reputation surfaces include Reddit (r/sysadmin, r/devops, vertical subreddits) more heavily than other industries. Glassdoor is also a strong signal because employee churn maps closely to product-quality churn.

### Example: Professional services (marketing, consulting, agencies)

- **Business model match:** Marketing agency, consulting firm, professional-services firm
- **Directory URL:** Clutch.co, Agency Spotter, region-specific chambers and trade associations
- **Search hint:** Search by service category + region.
- **Auth required:** No.
- **Trade press:** AdAge, Adweek, regional business journals
- **Notes:** Reputation often lives in client testimonials and case-study language as much as in third-party reviews. Pull case study language during the website crawl.

---

## Add your own

To add an industry directory, copy the format above and append to this file. The skill picks up new industries on the next run — no script changes required.

If you build out industry-specific search patterns that work well, consider opening a PR to share them.
