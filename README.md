# Coffee Match

A coffee profile tool that connects people’s preferences to local Washington roasters.

---

## Project Information

**Project Title:**  
Coffee Match

**Project Type:**  
Tool

**Project Group Members:**  
- Julia Glasser  
- Johnny Liang  
- Jeremy Wise  
- Alvin Alias  

---

## Questions of Interest

- What is someone's coffee profile (preferred roast, grind type, etc.)?
- What product from Washington roasters best matches a user’s preferences?
- Are these coffees easy to purchase from a local QFC?
- Could a user travel to try these local cofees?

---

## Project Goals

The project will produce:

- A tool that asks users a series of questions to build a profile of their coffee preferences.
- A recommendation for a bag of coffee produced by Washington roasters that best matches those preferences.
- Potential integration of:
  - Prior user reviews of beans/brands
  - Roastery location information
  - Roastery mission statements
  - Information to support tasting or site visits to associated cafes

---

## Data Sources

### Primary Data Sources

1. Washington coffee roasters / bean producers dataset 
/data/raw/Product_Information.xlsx
   (Scraped and cleaned with potential manual additions)

2. Reviews of Washington coffees / tasting notes, brew method, etc.
/data/raw/Reviews_and_Tasting_Notes.xlsx
...(Scraped cleaned)

### Supporting Data Sources

1. Class survey of about 50 people.
/assets/survey
https://docs.google.com/forms/d/1an5dfDEH4OAza_Z0BzkKt5Qr7qmnjg3V2XM2tcnHINw/closedform

2. King County restaurant search safety rating API containing cafes and locations.
/data/processed/address_out.csv
https://kingcounty.gov/en/dept/dph/health-safety/food-safety/search-restaurant-safety-ratings#/

### Unused Data Sources

1. Kroger Product API (desktop QFC query suggested data for only 3 roasters present in primary data: Tony's, Vita, and Ladro).
   https://developer.kroger.com/api-products/api/product-api-public

2. Washington Department of Revenue API business address lookup, “. . . cannot be queried using the Socrata Open Data API” https://dev.socrata.com/foundry/data.wa.gov/4wur-kfnr.

---

### Badges for CI status and code coverage

[![CI](https://github.com/jsyliang/CoffeeMatch/actions/workflows/continuous_int.yml/badge.svg)](https://github.com/jsyliang/CoffeeMatch/actions/workflows/continuous_int.yml)
[![codecov](https://codecov.io/gh/jsyliang/CoffeeMatch/branch/main/graph/badge.svg)](https://codecov.io/gh/jsyliang/CoffeeMatch)
