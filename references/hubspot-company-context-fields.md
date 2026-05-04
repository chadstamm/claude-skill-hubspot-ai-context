# HubSpot Company Context — Field Map

Canonical reference for HubSpot's Company Context page (Breeze Intelligence + Brand Voice + top-of-page positioning fields).

This is the ground-truth field list. If HubSpot's UI changes, edit this file rather than papering over the change inside the skill protocol.

---

## Section 1 — Top of page (positioning)

| Field | Type | Limit | Source strategy |
|---|---|---|---|
| Value Proposition | long-form text | none visible | Site-derivable (homepage hero, About, product pages) |
| What pain points does your company solve? | long-form text | none visible | Site-derivable + existing client context |
| Itemized products or services | table (Product / Description) | none visible | Site-derivable (products / shop pages) — requires deep per-product crawl, not just homepage list |

## Section 2 — Brand Voice

| Field | Type | Required | Limit | Source strategy |
|---|---|---|---|---|
| Personality | multi-tag (HubSpot **fixed picklist** — see below) | Yes | 4 max | Voice analysis. **Pick ONLY from the picklist.** |
| Default tone | multi-tag (HubSpot **fixed picklist** — see below) | Yes | 4 max | Voice analysis. **Pick ONLY from the picklist.** |
| Mission | text | No | **50 words** | Site (About, footer) + existing client context |
| Terms to avoid | multi-word | No | **20 words** | Voice analysis (avoid lists in any voice profile) |
| Replacement rules | case-sensitive word→word | No | none visible | Voice analysis (replacement rules in any voice profile) |
| Inclusivity | 3 toggles | No | n/a | Client preference (3 checkboxes: gender-neutral / cultural / global idioms) |

### Personality picklist (verified 2026-04-29)

Adventurous, Authentic, Bold, Charismatic, Compassionate, Curious, Diverse, Down-to-earth, Driven, Dynamic, Eccentric, Edgy, Elegant, Helpful, Human, Innovative, Irreverent, Kind, Nurturing, Professional, Quirky, Rebellious, Relatable, Sophisticated, Supportive, Thoughtful, Trustworthy

**27 options. NEVER suggest a Personality value outside this list.** Common LLM-generated picks that fail HubSpot validation: "Knowledgeable", "Practical", "Direct", "Confident" — none exist in HubSpot's Personality picklist (some live in the Default Tone picklist instead).

### Default Tone picklist (verified 2026-04-29)

Affectionate, Assertive, Authoritative, Businesslike, Casual, Cheerful, Colloquial, Commanding, Compassionate, Confident, Contemplative, Conversational, Corporate, Courteous, Cynical, Deferential, Doubtful, Earnest, Educational, Empathetic, Encouraging, Energetic, Enlightening, Enthusiastic, Excited, Fanciful, Formal, Friendly, Funny, Grave, Hopeful, Humorous, Immediate, Impartial, Incredulous, Informal, Informative, Insistent, Inspirational, Instructive, Introspective, Inviting, Ironical, Literal, Loving, Matter-of-fact, Mocking, Motivating, Neutral, Objective, Optimistic, Passionate, Playful, Polite, Positive, Precise, Pressing, Professional, Questioning, Quirky, Reflective, Relaxed, Respectful, Romantic, Sarcastic, Serious, Skeptical, Solemn, Straightforward, Sympathetic, Technical, Unbiased, Understanding, Unemotional, Uplifting, Urgent, Warm, Whimsical, Witty

**~80 options. NEVER suggest a Default Tone value outside this list.**

**Important:** "Direct" is NOT in the picklist. Closest analogues for direct/clear voices: **Straightforward, Matter-of-fact, Assertive, Commanding, Authoritative.**

## Section 3 — Additional Context

Header note from HubSpot: *"This data is gathered from your website crawl and is used to enhance your generated AI content across HubSpot. You can recrawl your website or manually update this data at anytime."*

### 3a. Industry Classification

| Field | Type | Source strategy |
|---|---|---|
| Industry | single value | **Manual entry: Title Case with spaces.** Breeze auto-populates `ALL_CAPS_UNDERSCORE`; override with human-readable Title Case (e.g., "Food & Beverage", not "FOOD_BEVERAGES"). |
| Sub-Industry | single value | **Manual entry: Title Case.** Breeze frequently miscategorizes. Override with the actual product category. |
| Industry Group | single value | **Manual entry: Title Case.** Reflect what the company DOES, not what their customers sell. |
| Business Sector | single value | **Manual entry: Title Case.** Common values: "Consumer Discretionary," "Consumer Staples," "Industrials," "Technology," etc. |
| Industry-Related Tags | multi-tag | Breeze auto + manual additions. Tags stay lowercase_with_underscores (these aren't displayed as fields). |

**Case convention rule:** All Industry Classification field VALUES use Title Case with spaces and ampersands (manual entry standard). Tags stay lowercase. Don't paste Breeze's underscore format into the field — HubSpot's UI displays it as-is, looks broken.

### 3b. Customer Sentiment

| Field | Type | Source strategy |
|---|---|---|
| Net Promoter Score (NPS) | number | **Client-required — not derivable from website** |
| Positive Brand Associations | bullet list | Site testimonials + reviews + existing client context |
| Negative Brand Associations | bullet list | **Off-site research — reviews, forums, Reddit, Glassdoor, BBB, Google Business** |

### 3c. Competitive Landscape

| Field | Type | Source strategy |
|---|---|---|
| Competitive Advantages | bullet list | Site (homepage USPs, About) + existing client context |
| Main Competitors | list w/ URLs | Off-site research (industry directory + web search) + existing client context |

### 3d. Content Themes

| Field | Type | Source strategy |
|---|---|---|
| Primary Content Topics | bullet list | Blog crawl + content calendar |
| Content Format Types | bullet list | Blog crawl + content history |

### 3e. Tech Stack

| Field | Type | Source strategy |
|---|---|---|
| Technologies | bullet list | Breeze auto (BuiltWith-style detection) |
| Technology Categories | bullet list | Breeze auto + manual |

### 3f. Social Responsibility

| Field | Type | Source strategy |
|---|---|---|
| Supported Social Causes | bullet list | Site (About, blog, social posts) + existing client context |
| Sustainability Initiatives | bullet list | Site + existing client context |

---

## Source-strategy summary

- **Site-derivable** (homepage crawl is enough): Value Prop, Pain Points, Products, Mission, Competitive Advantages, Sustainability, Primary Content Topics, Content Format Types
- **Voice-analysis required**: Personality, Default Tone, Terms to Avoid, Replacement Rules
- **Off-site research required**: Main Competitors, Negative Brand Associations
- **Breeze auto-populates, may need override**: Industry Classification (5 fields), Tech Stack, Industry-Related Tags
- **Client must provide**: NPS, Inclusivity preferences
