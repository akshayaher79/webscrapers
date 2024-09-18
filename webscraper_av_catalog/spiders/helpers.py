import csv

with open('Antivirus/static_data/iso_country_codes.csv', newline='') as country_codes_f:
    country_codes = {
        code: country for code, country in csv.reader(country_codes_f)
    }
