# Functional Specification  
## Coffee Match – Washington Local Coffee Recommendation System

---

## 1. Background

### Problem Being Addressed

Consumers who want to purchase **local Washington coffee** face a fragmented and confusing marketplace. Coffee products differ by:

- Roaster
- Roast level (light, medium, dark)
- Origin
- Price
- Bag size
- Whole bean vs ground availability
- Popularity or review ratings

Although there does exist qualitative local coffee information aggregators such as [Seattle Coffee Scene](https://seattlecoffeescene.com/), currently, there is no structured system that:

- Aggregates Washington roaster offerings
- Connects user taste preferences to specific blends
- Compares price and quality in a transparent way
- Explains why a recommendation is provided

Consumers must rely on individual roaster websites, retailer listings, or in-store browsing, which makes it difficult to evaluate options systematically.

### Proposed Solution

The Coffee Match system will:

- Aggregate publicly available coffee product data
- Allow users to filter by:
  - Roast level
  - Budget
  - Ground vs whole bean
- Rank coffees based on quality and value
- Provide transparent reasoning for recommendations
- Optionally support availability or location-based enhancements

The system aims to simplify the local coffee discovery process using structured data and transparent ranking logic.

---

## 2. User Profile

### Primary Users – Coffee Buyers

**Who they are:**
- Residents of Washington state
- Students, professionals, and casual coffee drinkers
- Interested in buying local coffee

**Domain knowledge:**
- Basic familiarity with roast levels
- Limited understanding of origin differences or pricing comparisons

**Computing knowledge:**
- Can browse websites
- Comfortable using dropdown filters and buttons
- No programming knowledge required

---

### Secondary Users – Project Maintainers

**Who they are:**
- Data science students developing the project
- Individuals responsible for updating or maintaining the dataset

**Domain knowledge:**
- Understand the structure of the coffee dataset
- Familiar with coffee attributes such as roast level, origin, price, and grind type

**Computing knowledge:**
- Can edit and upload CSV files
- Can manage structured tabular data
- Can run the application locally and update data sources when needed

---

## 3. Data Sources

The Coffee Match system uses two primary scraped datasets derived from publicly available product pages.

### 3.1 Washington Coffee Product Dataset  
(Source: Filtered Bottomless product listings for Washington roasters)

Structure: One row per coffee product (bag).

#### Core Product Fields

| Field | Type | Description |
|-------|------|------------|
| roaster | string | Name of the coffee roastery |
| product_name | string | Name of the coffee blend |
| origin | string | Country/region of origin (if applicable) |
| roast_type | categorical | Roast level (light, medium, dark, etc.) |
| size | string | Listed bag size |
| size_oz | numeric | Bag size converted to ounces |
| price | string | Listed retail price |
| price_numeric | numeric | Cleaned numeric price value |
| price_per_oz | numeric (derived) | price_numeric ÷ size_oz |

#### Review & Popularity Fields

| Field | Type | Description |
|-------|------|------------|
| hearts | numeric | Number of users who “hearted” the product |
| total_reviews | numeric | Total number of reviews |
| heart_percentage | numeric | Percentage of positive reactions |
| has_reviews | boolean | Whether product has reviews |

#### Product Attributes

| Field | Type | Description |
|-------|------|------------|
| decaf | boolean | Indicates decaffeinated product |
| blend | boolean | Indicates if product is a blend |
| single_origin | boolean | Indicates if product is single origin |
| available_ground | boolean | Whether ground option is available |
| tags | string/list | Additional descriptive tags |
| url | string | Product page link |
| product_id | string | Internal identifier (not used in user-facing system) |

Internal identifiers such as `product_id` will not be exposed to end users.

---

### 3.2 Review Text Dataset  
(Source: Scraped review pages from Bottomless)

Structure: One row per individual review.

| Field | Type | Description |
|-------|------|------------|
| product_name | string | Coffee product reviewed |
| sentiment | numeric/string | Sentiment label or score |
| brewing_method | string | Brewing method used by reviewer |
| review_text | text | Full review content |
| reviewer_info | string | Reviewer metadata (if available) |
| date | string/date | Review submission date |
| tasting_notes | string | Flavor descriptors provided |

This dataset supports potential natural language processing (NLP) enhancements such as:
- Keyword extraction (e.g., “chocolate,” “fruity”)
- Sentiment validation
- Flavor profile clustering

### 3.3 Potential Expanded Datasets 

Data sources such as surveys and APIs (governmental websites or grocers) are being considered.

---


## 4. Use Cases
(For distinction between implicit and explicit system responses, refer to use-cases.md)

---

## Use Case 1A – Single Coffee Match

### Objective

User wants to receive one best coffee recommendation based on their preferences.

### Interaction Steps

1. User selects "Find My Coffee."
2. System presents first filtering question (e.g., roast level).
3. User selects preference.
4. System filters matching coffees.
5. System presents next filtering question (e.g., budget).
6. User selects preference.
7. System narrows results further.
8. Loop continues until:
   - One coffee remains, OR
   - Maximum number of questions reached, OR
   - User stops filtering.

### System Behavior

- If one coffee remains → display full details.
- If multiple coffees remain → rank using scoring algorithm and show top match.
- If zero coffees remain → notify user and allow relaxing constraints.
- User may step backward at any time.

---

## Use Case 1B – Multiple Coffee Matches

### Objective

User wants several recommended coffees instead of a single match.

### Interaction Steps

1. User selects "Show Multiple Matches."
2. System presents filtering question.
3. User selects preference.
4. System filters dataset.
5. If remaining coffees ≤ threshold (e.g., 5), show matches.
6. User may:
   - Continue filtering
   - Stop and view matches
   - Step backward

### System Behavior

- If many coffees remain → rank and display top N.
- If none remain → suggest relaxing filters.
- Filtering continues until user stops or attributes are exhausted.

---

## Use Case 2A – Add New Coffee (Admin)

### Objective

Administrator adds a new coffee entry to the system.

### Interaction Steps

1. Admin logs into system.
2. Admin selects "Add Coffee."
3. System displays required entry form:
   - Roaster name
   - Roast level
   - Price
   - Size
   - Origin
   - Ground availability
4. Admin fills required fields.
5. System validates entries.
6. Admin submits form.
7. System confirms successful addition.

### System Requirements

- Validate numeric fields.
- Validate roast category.
- Prevent duplicate entries.
- Display confirmation summary.

---

## Use Case 2B – Match History Review (Admin)

### Objective

Administrator reviews anonymized matching history.

### Interaction Steps

1. Admin selects "View Match History."
2. System retrieves stored interaction logs.
3. Admin views summary dashboard or downloads report.

### Notes

- Logs must remain anonymous.
- No personally identifiable information is stored.
- Used for aggregate trend analysis only.

---

## 5. System Constraints

- Maximum number of filtering questions equals number of attributes.
- Ranking must occur whenever multiple coffees remain.
- System must gracefully handle empty result sets.
- User must be able to step backward.
- Seasonal products may optionally be excluded.

---

## 6. Success Criteria

The system is successful if:

- Users receive recommendations within 3–5 interactions.
- Recommendations are transparent and explainable.
- Users can compare quality and value easily.
- Filtering feels intuitive.
- Data remains structured and maintainable.
