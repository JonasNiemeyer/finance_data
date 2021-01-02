import sys
sys.path.append(r"D:\Investing; Statistics; Economics\Investing\_Libraries")

import requests
from finance_data.Parser import SECParser

class TestSECParser(object):
	def __init__(self):
		self.url = "https://www.sec.gov/Archives/edgar/data/1652044/000165204420000032/0001652044-20-000032.txt"
		file = requests.get(self.url)

	def test_company_information(self):
		data = SECParser(file).get_company_information()

		assert data['cik'] == 1652044
		assert data['sic'] == 7370