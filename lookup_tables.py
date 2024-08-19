import json
import math
import pandas as pd
import warnings
from pathlib import Path

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
config = json.load(open('config.txt'))
file_jp_pension_rate_table = Path(Path(__file__).parent, 'resources',
                                  config["jp_pension"])
file_jp_health_rate = Path(Path(__file__).parent, 'resources', 
                           config["jp_health"])
file_us_tax_chart = Path(Path(__file__).parent, 'resources', 
                         config["us_tax"])


def calc_jp_basic_deduction(input_income):
    if input_income <= 24000000:
        output_val = 480000
    elif (input_income > 24000000) and (input_income <= 24500000):
        output_val = 320000
    elif (input_income > 24500000) and (input_income <= 25000000):
        output_val = 160000
    elif input_income > 25000000:
        output_val = 0
    return output_val

def calc_jp_employment_income_deduction(input_income):
    if input_income <= 550999:
        output_val = 0
    elif (input_income >= 551000) and (input_income <= 1618999):
        output_val = input_income - 550000
    elif (input_income >= 1619000) and (input_income <= 1619999):
        output_val = 1069000
    elif (input_income >= 1620000) and (input_income <= 1621999):
        output_val = 1070000
    elif (input_income >= 1622000) and (input_income <= 1623999):
        output_val = 1072000
    elif (input_income >= 1624000) and (input_income <= 1627999):
        output_val = 1074000
    elif (input_income >= 1628000) and (input_income <= 1799999):
        output_val = (round_down(input_income/4,1000)*2.4) + 100000
    elif (input_income >= 1800000) and (input_income <= 3599999):
        output_val = (round_down(input_income/4,1000)*2.8) - 80000
    elif (input_income >= 3600000) and (input_income <= 6599999):
        output_val = (round_down(input_income/4,1000)*3.2) - 440000
    elif (input_income >= 6600000) and (input_income <= 8499999):
        output_val = (input_income*0.9) - 1100000
    elif input_income >= 8500000:
        output_val = input_income - 1950000
    return output_val

def calc_jp_health_cost_deduction(input_income, input_healthare_cost):
    income_5_pct = input_income*0.05
    if income_5_pct < 100000:
        medical_cost_deduction = input_healthare_cost - income_5_pct
    else:
        medical_cost_deduction = input_healthare_cost - 100000
    return medical_cost_deduction

def calc_jp_health_insurance_amt(input_income_monthly, employment_type):
    # Import health insurance rate table from file
    col_names = ["等級", "月額", "円以上", "円未満", "全額", "折半額"]
    df_health = pd.read_excel(file_jp_health_rate, sheet_name="東京", 
                              skiprows=10, skipfooter=24, usecols="A:I")
    df_health = df_health.iloc[:50, [0,1,2,4,5,6]]
    df_health.columns = col_names

    # Get rate based on monthly income
    if input_income_monthly < 63000:
        rates = df_health.loc[df_health["円未満"]==63000]
    elif input_income_monthly > 1355000:
        rates = df_health.loc[df_health["円以上"]==1355000]
    else:
        rates = df_health.loc[(df_health["円以上"]<=input_income_monthly) 
                              & (df_health["円未満"]>input_income_monthly)]

    # Get rate based on employment type (company employee vs not)
    if employment_type == 'seishain':
        output_val = rates["折半額"].values[0]
    else:
        output_val = rates["全額"].values[0]
    return output_val
    
def calc_jp_national_income_tax(input_taxable_inc):
    if input_taxable_inc < 1000:
        output_val = 0
    elif (input_taxable_inc >= 1000) and (input_taxable_inc <= 1949000):
        output_val = input_taxable_inc*0.05
    elif (input_taxable_inc >= 1950000) and (input_taxable_inc <= 3299000):
        output_val = (input_taxable_inc*0.1) - 97500
    elif (input_taxable_inc >= 3300000) and (input_taxable_inc <= 6949000):
        output_val = (input_taxable_inc*0.2) - 427500
    elif (input_taxable_inc >= 6950000) and (input_taxable_inc <= 8999000):
        output_val = (input_taxable_inc*0.23) - 636000
    elif (input_taxable_inc >= 9000000) and (input_taxable_inc <= 17999000):
        output_val = (input_taxable_inc*0.33) - 1536000
    elif (input_taxable_inc >= 18000000) and (input_taxable_inc <= 39999000):
        output_val = (input_taxable_inc*0.4) - 2796000
    elif input_taxable_inc >= 40000000:
        output_val = (input_taxable_inc*0.45)-4796000
    return output_val

def calc_jp_pension_amount(input_income_monthly, employment_type):
    # Import pension rate table from file
    col_names = ["等級", "月額", "円以上", "円未満", "全額", "折半額"]
    df_pension = pd.read_excel(file_jp_pension_rate_table, skiprows=8)
    df_pension = df_pension.iloc[:32, [1,2,3,5,6,7]]
    df_pension.columns = col_names

    # Get rate based on monthly income
    if input_income_monthly < 93000:
        rates = df_pension.loc[df_pension["円未満"]==93000]
    elif input_income_monthly > 635000:
        rates = df_pension.loc[df_pension["円以上"]==635000]
    else:
        rates = df_pension.loc[(df_pension["円以上"]<=input_income_monthly) 
                            & (df_pension["円未満"]>input_income_monthly)]

    # Get rate based on employment type (company employee vs not)
    if employment_type == 'seishain':
        output_val = rates["折半額"].values[0]
    else:
        output_val = rates["全額"].values[0]
    return output_val

def get_us_tax_amount(input_taxable_inc, filing_status):
    col_names = ["At least", "Less than", "Single", "Married Filing Jointly",
                "Married Filing Separately", "Head of Household"]
    us_tax_table = pd.read_excel(file_us_tax_chart, engine="odf", skiprows=2, 
                                names=col_names)

    us_tax_range = us_tax_table.loc[
        (us_tax_table["At least"]<=input_taxable_inc) 
        & (us_tax_table["Less than"]>input_taxable_inc)]

    if filing_status == "single":
        output_val = us_tax_range["Single"].values[0]
    elif filing_status == "married-joint":
        output_val = us_tax_range["Married Filing Jointly"].values[0]
    elif filing_status == "married-separate":
        output_val = us_tax_range["Married Filing Separately"].values[0]
    elif filing_status == "head-of-household":
        output_val = us_tax_range["Head of Household"].values[0]
    return output_val

def round_down(input_num, round_to):
    output_val = math.floor(input_num/round_to)*round_to
    return output_val