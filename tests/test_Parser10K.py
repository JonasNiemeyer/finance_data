import sys
sys.path.append(r"D:\Investing; Statistics; Economics\Investing\_Libraries")

import requests
from finance_data.Parser import Parser10K

class TestParser10K(object):
	def __init__(self):
		self.url = "https://www.sec.gov/Archives/edgar/data/320193/000032019320000096/0000320193-20-000096.txt"
		self.site = requests.get(self.url)
	def test_income(self):
		data = Parser10K(self.site).parse_income_statement()

		assert data["cik"] == 320193
		assert data["cik"] == 3571

		assert data["Revenues"] == 274_515_000_000
		assert data["Cost of Revenues"] == 169_559_000_000
		assert data["Gross Profit"] == 104_956_000_000

		assert data["Research and Development Expenses"] == 18_752_000_000
		assert data["General and Administrative Expenses"] == 19_916_000_000
		assert data["Depreciation and Amortization"] == None
		assert data["Total Operating Expenses"] == 38_668_000_000
		assert data["Operating Income"] == 66_288_000_000

		assert data["Interest Income"] == None
		assert data["Interst Expenses"] == None
		assert data["Pretax Income"] == 67_091_000_000

		assert data["Tax Expenses"] == -9_680_000_000
		assert data["Net Income"] == 57_411_000_000

		assert data["EPS basic"] == 3.31
		assert data["EPS diluted"] == 3.28

		assert data["No. of basic Shares outstanding"] == 17_352_119_000
		assert data["No. of diluted Shares outstanding"] == 17_528_214_000

		assert data["Dividends per Share"] == None


	def test_balance(self):
		data = Parser10K(site).parse_balance_sheet_statement()

		assert data["Cash and Cash Equivalents"] == 38_016_000_000
		assert data["Short Term Marketable Securities"] == 52_927_000_000
		assert data["Accounts Receivable"] == 16_120_000_000
		assert data["Inventories"] == 4_061_000_000
		assert data["Total Current Assets"] == 143_713_000_000

		assert data["Long Term Marketable Securities"] == 100_887_000_000
		assert data["Property, Plant and Equipment"] == 36_766_000_000
		assert data["Goodwill"] == None
		assert data["Other Intangibles"] == None
		assert data["Fixed Assets"] == 187_175_000_000

		assert data["Total Assets"] == 323_888_000_000

		assert data["Accounts Payable"] == 42_296_000_000
		assert data["Deferred Revenue"] == 6_643_000_000
		assert data["Short Term Debt"] == (4_996 + 8_773) * 1_000_000
		assert data["Income Taxes Payable"] == None
		assert data["Total Current Liabilities"] == 105_392_000_000

		assert data["Long Term Debt"] == 98_667_000_000
		assert data["Deferred Tax Liabilities"] == None
		assert data["Total Long Term Liabilities"] == 153_157_000_000

		assert data["Total Liabilities"] == 258_549_000_000

		assert data["Common Stock and Additional Paid-In Capital"] == 50_779_000_000
		assert data["Retained Earnings"] == 14_966_000_000
		assert data["Total Shareholders Equity"] == 65_339_000_000

		assert data['Total Shareholders Equity'] + data['Total Liabilities'] == data['Total Assets']

	
if __name__ == '__main__':
	TestParser10K().test_income()

balance_sheet_variables = (
    "Cash and Cash Equivalents",
    "Marketable Securities",
    "Accounts Receivable",
    "Inventories",
    "Total Current Assets"
    # ------------------
    "Property, Plant and Equipment",
    "Goodwill",
    "Other Intangibles",
    "Fixed Assets",
    # ------------------
    "Total Assets",
    # ------------------
    "Accounts Payable",
    "Short Term Debt",
    "Income Taxes Payable",
    "Total Current Liabilities",
    # ------------------
    "Long Term Debt",
    "Deferred Tax Liabilities",
    "Total Long Term Liabilities",
    # ------------------
    "Total Liabilities",
    # ------------------
    "Common Stock",
    "Additional Paid-In Capital",
    "Retained Earnings",
    "Total Shareholders Equity",
    )

cashflow_variables = (
    "Depreciation and Amortization",
    "Changes in Inventories",
    "Changes in Accounts Receivable",
    "Changes in Accounts Payable",
    "Changes in Unearned Revenues",
    "Operating Cashflow",
    # ------------------
    "Purchases of Property, Plant and Equipment",
    "Sales of Property, Plant and Equipment",
    "Acquisitions",
    "Purchases of Marketable Securities",
    "Sales of Marketable Securities",
    "Investing Cashflow",
    # ------------------
    "Repayment of Long Term Debt",
    "Dividends Paid",
    "Repurchases of Common Stock",
    "Financing Cashflow"
    )