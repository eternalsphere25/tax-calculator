## Overview
This repository contains code that calculates and compares taxes between the United States and Japan.

## File List
1. `calculator.py`: Used to calculate tax liability for United States and Japan
2. `calculate_table.py`: Used to calculate US tax liability based on a Japanese income source
3. `lookup_tables.py`: Shared functions used by other programs. This fucntion requires tax tables that can be downloaded from each respective country's tax agency website(s)

## Configuration Files

### Configuration for `resources\tax_rates.json`
```
{
    <YEAR>: {
        "Japan": {
            "rate_jpy": <FLOAT>,
            "cost_healthcare_jp": <INT>,
            "employment_type": <STR>,
            "income_jpy: <INT>,
            "rate_pension": <FLOAT>,
            "rate_employment_insurance": <FLOAT>,
            "rate_health": <FLOAT>,
            "rate_municipal": <FLOAT>,
            "rate_prefectural": <FLOAT>,
            "rate_reconstruction": <FLOAT>
        },
        "United States": {
            "deduction_standard": <INT>
            "filing": <STR>
        }
    }
}
```
### Configuration for `config.txt`
Configuration is stored as a dictionary in a plaintext file:
```
{"jp_pension": <FILENAME>,  
 "jp_health": <FILENAME>,  
 "us_tax": <FILENAME>}
```
## Reference Table Data Sources
### United States
* https://www.irs.gov/forms-pubs/about-form-1040
* https://fiscaldata.treasury.gov/datasets/treasury-reporting-rates-exchange/treasury-reporting-rates-of-exchange
### Japan
* https://www.nenkin.go.jp/service/kounen/hokenryo/ryogaku/ryogakuhyo/20200825.html
* https://www.kyoukaikenpo.or.jp/g7/cat330/sb3150/r05/r5ryougakuhyou3gatukara/