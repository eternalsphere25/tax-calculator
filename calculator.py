import json
import lookup_tables as lookup
import numpy as np
import pandas as pd
import sys
from pathlib import Path


#------------------------------------------------------------------------------
# STEP 0: Define global variables
#------------------------------------------------------------------------------

# Import definitions
rate_file = Path(Path(__file__).parent, 'resources', 'tax_rates.json')
with open(rate_file) as input_json:
    rate_data_raw = json.load(input_json)

# Prompt user to select which year to calculate taxes for
selected_year = input('Input tax year: ')
try:
    rates_jp = rate_data_raw[selected_year]["Japan"]
    rates_us = rate_data_raw[selected_year]["United States"]
except KeyError:
    print(f'WARNING: Information for year {selected_year} '
          f'not found in database')
    print('Program terminating...')
    sys.exit()


#------------------------------------------------------------------------------
# STEP 1: Calculate tax liability for Japan
#------------------------------------------------------------------------------

#----------------------------------------
# STEP 1A: Determine gross income
#----------------------------------------

# Calculate income in JPY and USD
income_jpy = sum([rates_jp[key] for key in rates_jp if "income" in key])
income_usd = income_jpy/rates_jp["rate_jpy"]
print("\n2023 Income Summary:")
print(f"- 2023 Income (JPY): \u00a5{income_jpy:,d}")
print(f"- 2023 Income (USD): ${income_usd:,.2f}")

# Calculate JPY adjusted income after standard income deduction
income_jpy_adjusted = lookup.calc_jp_employment_income_deduction(income_jpy)
print(f"- 2023 Adjusted Income (JPY): \u00a5{income_jpy_adjusted:,.0f}")

#----------------------------------------
# STEP 1B: Determine deductions
#----------------------------------------

print(f"\n2023 Deduction Summary:")

# Calculate pension amount
income_jpy_monthly = income_jpy/12
pension_amt = int(lookup.calc_jp_pension_amount(
    income_jpy_monthly, rates_jp["employment_type"]))*12
print(f"- 2023 Pension Amount (JPY): \u00a5{pension_amt:,d}")

# Employment Insurance
employment_ins_amt = int(
    round(income_jpy*rates_jp["rate_employment_insurance"], 0))
print(f"- 2023 Employment Insurance Amount (JPY): "
      f"\u00a5{employment_ins_amt:,d}")

# Calculate health insurance
health_ins_amt = int(
    lookup.calc_jp_health_insurance_amt(
        income_jpy_monthly, rates_jp["employment_type"]))*12
print(f"- 2023 Health Insurance Amount (JPY): \u00a5{health_ins_amt:,d}")

# Calculate basic deductions
basic_deduction_jp_amt = lookup.calc_jp_basic_deduction(income_jpy_adjusted)
print(f"- 2023 Basic Deduction Amount (JPY): \u00a5{basic_deduction_jp_amt:,d}")

# Calculate healthcare cost deduction
medical_cost_deduction = lookup.calc_jp_health_cost_deduction(
    income_jpy_adjusted, rates_jp["cost_healthcare_jp"])
print(f"- 2023 Healthcare Cost Deduction (JP): "
      f"\u00a5{medical_cost_deduction:,.0f}")

# Calculate total deduction
deduction_total_jp = (pension_amt + employment_ins_amt + health_ins_amt + 
                      basic_deduction_jp_amt + medical_cost_deduction)
print(f"- 2023 Deduction Total Amount (JPY): \u00a5{deduction_total_jp:,d}")

#----------------------------------------
# STEP 1C: Determine all taxes
#----------------------------------------

print(f"\n2023 Tax (JP) Summary:")

# Calculate taxable income after deductions
taxable_income_jp = lookup.round_down(
    income_jpy_adjusted-deduction_total_jp,1000)
print(f"- 2023 Taxable Income (JP): \u00a5{taxable_income_jp:,d}")

# Calculate JP national income tax
income_tax_national_jp = lookup.calc_jp_national_income_tax(taxable_income_jp)
print(f"- 2023 National Income Tax (JP): \u00a5{income_tax_national_jp:,.0f}")

# Calculate JP prefectural and municipal (residence) tax
tax_prefectural = taxable_income_jp*rates_jp["rate_prefectural"]
tax_municipal = taxable_income_jp*rates_jp["rate_municipal"]
tax_resident = tax_prefectural + tax_municipal
print(f"- 2023 Residence Tax (JP): \u00a5{tax_resident:,.0f}")

# Calculate reconstruction tax
tax_reconsruction = income_tax_national_jp*rates_jp["rate_reconstruction"]
print(f"- 2023 Reconstruction Tax (JP): \u00a5{tax_reconsruction:,.0f}")

#----------------------------------------
# STEP 1D: Calculate total Japan tax
#----------------------------------------

print(f"\n2023 Total Tax (JP) Summary:")

# Calculate total tax (JP)
tax_jp_total = income_tax_national_jp + tax_resident + tax_reconsruction
print(f"- 2023 Total Tax (JP): \u00a5{tax_jp_total:,.0f}")
print(f"- 2023 Total Tax (JP) in USD: ${round(
    tax_jp_total/rates_jp["rate_jpy"],2):,.2f}")


#------------------------------------------------------------------------------
# STEP 3: Calculate tax liability for USA
#------------------------------------------------------------------------------

print(f"\n2023 Deduction Summary:")

# Calculate taxable income
taxable_income_usa = np.round(income_usd - rates_us["deduction_standard"])
print(f"- 2023 Taxable Income (USD): ${taxable_income_usa:,.2f}")

# Calculate tax
print(f"\n2023 Income Tax (US) Summary:")
tax_us = lookup.get_us_tax_amount(taxable_income_usa, rates_us["filing"])

print(f"- 2023 Income Tax (USD): ${tax_us:,.2f}")