import json
import lookup_tables as lookup
import pandas as pd
import sys
from pathlib import Path
from tabulate import tabulate
from tqdm import tqdm


def print_df(input_df):
    print(tabulate(input_df, headers="keys", tablefmt="psql", stralign="right"))


#------------------------------------------------------------------------------
# STEP 0: Define global variables
#------------------------------------------------------------------------------

# Set income range to generate table for
calc_income_range = list(range(1500000, 24000000, 500000))

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

# Calculated table values
cat_df = {'Item': ["Income (JPY)",
                   "Income (USD)",
                   "Income, Adjusted (JP)",
                   "Pension Amount (JP)",
                   "Employment Insurance Amount (JP)",
                   "Health Insurance Amount (JP)",
                   "Basic Deduction Amount (JP)",
                   "Healthcare Cost Amount (JP)",
                   "Deduction Total Amount (JP)",
                   "Taxable Income (JP)",
                   "National Income Tax (JP)",
                   "Residence Tax (JP)",
                   "Reconstruction Tax (JP)",
                   "2023 Total Tax (JP)",
                   "2023 Total Tax (JP) in USD"]}

#------------------------------------------------------------------------------
# STEP 1: Calculate tax liability for Japan
#------------------------------------------------------------------------------

# Generate master dataframe for all calculated values
df_taxes = pd.DataFrame(data=cat_df)

# Iterate over income range specified earlier
print(f"\nCalculating tax liability for yearly incomes between "
      f"\u00a5{calc_income_range[0]:,} to \u00a5{calc_income_range[-1]:,}...")
for i in tqdm(calc_income_range):

    #----------------------------------------
    # STEP 1A: Determine gross income
    #----------------------------------------

    # Calculate income in JPY and USD
    income_jpy = i
    income_usd = income_jpy/rates_jp["rate_jpy"]

    # Calculate JPY adjusted income after standard income deduction
    income_jpy_adjusted = lookup.calc_jp_employment_income_deduction(income_jpy)

    #----------------------------------------
    # STEP 1B: Determine deductions
    #----------------------------------------

    # Calculate pension amount
    income_jpy_monthly = income_jpy/12
    pension_amt = int(lookup.calc_jp_pension_amount(
        income_jpy_monthly, rates_jp["employment_type"]))*12

    # Employment Insurance
    employment_ins_amt = int(
        round(income_jpy*rates_jp["rate_employment_insurance"], 0))

    # Calculate health insurance
    health_ins_amt = int(
        lookup.calc_jp_health_insurance_amt(
            income_jpy_monthly, rates_jp["employment_type"]))*12

    # Calculate basic deductions
    basic_deduction_jp_amt = lookup.calc_jp_basic_deduction(income_jpy_adjusted)

    # Calculate healthcare cost deduction
    medical_cost_deduction = lookup.calc_jp_health_cost_deduction(
        income_jpy_adjusted, rates_jp["cost_healthcare_jp"])

    # Calculate total deduction
    deduction_total_jp = (pension_amt + employment_ins_amt + health_ins_amt + 
                          basic_deduction_jp_amt + medical_cost_deduction)

    #----------------------------------------
    # STEP 1C: Determine all taxes
    #----------------------------------------

    # Calculate taxable income after deductions
    taxable_income_jp = lookup.round_down(
        income_jpy_adjusted-deduction_total_jp,1000)

    # Calculate JP national income tax
    income_tax_national_jp = lookup.calc_jp_national_income_tax(
        taxable_income_jp)

    # Calculate JP prefectural and municipal (residence) tax
    tax_prefectural = taxable_income_jp*rates_jp["rate_prefectural"]
    tax_municipal = taxable_income_jp*rates_jp["rate_municipal"]
    tax_resident = tax_prefectural + tax_municipal

    # Calculate reconstruction tax
    tax_reconsruction = income_tax_national_jp*rates_jp["rate_reconstruction"]

    #----------------------------------------
    # STEP 1D: Calculate total Japan tax
    #----------------------------------------

    # Calculate total tax (JP)
    tax_jp_total = income_tax_national_jp + tax_resident + tax_reconsruction

    #----------------------------------------
    # STEP 1E: Add values to to dataframe
    #----------------------------------------

    # Add values to to dataframe
    values_list = [f"\u00a5{income_jpy:,d}",
                   f"${income_usd:,.2f}",
                   f"\u00a5{income_jpy_adjusted:,.0f}",
                   f"\u00a5{pension_amt:,d}",
                   f"\u00a5{employment_ins_amt:,d}",
                   f"\u00a5{health_ins_amt:,d}",
                   f"\u00a5{basic_deduction_jp_amt:,d}",
                   f"\u00a5{medical_cost_deduction:,.0f}",                  
                   f"\u00a5{deduction_total_jp:,.0f}",
                   f"\u00a5{taxable_income_jp:,d}",
                   f"\u00a5{income_tax_national_jp:,.0f}",
                   f"\u00a5{tax_resident:,.0f}",
                   f"\u00a5{tax_reconsruction:,.0f}",
                   f"\u00a5{tax_jp_total:,.0f}",
                   f"${round(tax_jp_total/rates_jp["rate_jpy"],2):,.2f}"]
    df_taxes[f"{i/1000000} M JPY"] = values_list


# Print out results
indices = list(range(len(calc_income_range)+1))[1:]
subindices = [indices[x:x+5] for x in range(0, len(indices), 5)]
for x in subindices:
    cols = [0] + x
    df_out = df_taxes.iloc[:,cols]
    print_df(df_out)