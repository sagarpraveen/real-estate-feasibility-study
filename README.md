# Project: Mumbai Real Estate Feasibility Automation

real estate feasibility study with a focus on the MCGM byelaws, Mumbai

## Objective
To create a tool that calculates the core financial viability of a real estate project in Mumbai based on user-provided inputs.

## MVP v0.1: The Core Financial Engine

This first version will be a command-line tool that focuses on the core financial calculations, using hardcoded assumptions for market and regulatory data.

### Inputs (Hardcoded for MVP)

1.  **Land Details:**
    *   `land_area_sq_mtr`: 1000.0
2.  **Cost Assumptions:**
    *   `land_cost_per_sq_mtr`: 150000.0
    *   `construction_cost_per_sq_ft`: 4000.0
    *   `professional_fees_pct`: 0.05 (5% of construction cost)
    *   `marketing_contingency_pct`: 0.08 (8% of revenue)
3.  **Regulatory & Sale Assumptions (Simplified):**
    *   `permissible_fsi`: 2.0
    *   `efficiency_ratio`: 0.85 (Saleable Area / Built-up Area)
4.  **Market Assumptions:**
    *   `sale_price_per_sq_ft`: 25000.0
5.  **Timeline Assumptions:**
    *   `project_duration_years`: 3

### Outputs (Printed to Console)

1.  Total Built-up Area (BUP)
2.  Total Saleable Area
3.  Total Project Revenue
4.  Total Project Cost
5.  Total Profit
6.  Profit Margin (%)
7.  A simplified IRR (Internal Rate of Return)

## Action Plan

1.  **Setup Project Structure:** Create the main project directory (`mumbai_feasibility`) and the necessary sub-directories (`/src`, `/tests`) and files (`requirements.txt`, `main.py`).
2.  **Define Data Models:** In a new file `src/models.py`, use the `pydantic` library to create strict data classes for our `ProjectInputs`.
3.  **Build the Financial Core:** In a new file `src/financial_engine.py`, write the primary calculation functions.
4.  **Create the Main Runner:** In `main.py`, define the hardcoded inputs, call the engine functions, and print the results.
