import re
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import pandas as pd
import requests

class SECFiling:
    def __init__(self, file: str):
        self._file = file
        self._name = self._parse_filer_name()
        self._filer_cik = self._parse_filer_cik()
        self._form = self._parse_form_type()
        self._date = self._parse_filing_date()

    def header_information(self) -> dict:
        self.company_information = {}
        self.company_information["name"] = self._name
        self.company_information["cik"] = self._filer_cik
        self.company_information["form"], self.company_information["amendment"] = self._form
        self.company_information["date"] = self._date
        return self.company_information

    def _parse_filer_name(self) -> str:
        name = re.findall("COMPANY CONFORMED NAME:\t{3}(.+)", self._file)[0]
        name = name.strip().lower().title()
        return name

    def _parse_filer_cik(self) -> int:
        # this method has to be overwritten in the 13DG Parser since there is a filer cik and a subject cik
        cik = int(re.findall("CENTRAL INDEX KEY:\t{3}([0-9]+)", self._file)[0])
        return cik

    def _parse_form_type(self) -> tuple:
        form = re.findall("FORM TYPE:\t{2}(.+)\n", self._file)[0]
        amendment = True if form.endswith("/A") else False
        return form, amendment

    def _parse_filing_date(self) -> str:
        date = re.findall("FILED AS OF DATE:\t{2}([0-9]+)", self._file)[0]
        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[6:])
        date = dt.date(year, month, day).isoformat()
        return date

    @classmethod
    def from_url(cls, url: str):
        txt = requests.get(url).text
        return cls(txt)

    @property
    def file(self) -> str:
        return self._file

    @property
    def name(self) -> str:
        return self._name

    @property
    def filer_cik(self) -> int:
        return self._filer_cik

    @property
    def form(self) -> str:
        return self._form

    @property
    def date(self) -> str:
        return self._date

    def __str__(self):
        return "{} Report({}, {})".format(self._form[0], self._name, self._date)


# -------------------------------------------------------------------------------------------------------------------------------------------


class Filing13F(SECFiling):
    def __init__(self, file):
        super(Filing13F, self).__init__(file)
        self.is_xml = False
        if "<XML>" in self._file:
            self.is_xml = True

    def parse(self) -> dict:
        return {**self._get_quarter, **self.get_holdings}

    def get_holdings(self, sort=False) -> dict:
        if self.is_xml is True:
            holdings = self._get_holdings_xml()
        else:
            holdings = self._get_holdings_text()
        if sort:
            holdings = dict(sorted(holdings.items(), key=lambda item: item[1][0], reverse=True))
        
        self.holdings = {'holdings': {}}
        for (name, cusip, option), (market_value, no_shares) in holdings.items():
            self.holdings['holdings'][cusip] = {}
            self.holdings['holdings'][cusip]['name'] = name
            self.holdings['holdings'][cusip]['market_value'] = market_value * 1000
            self.holdings['holdings'][cusip]['no_shares'] = int(no_shares)
            self.holdings['holdings'][cusip]['option'] = option
        
        self.holdings['no_holdings'] = len(self.holdings['holdings'])
        self.holdings['portfolio_value'] = sum([value[1]['market_value'] for value in self.holdings['holdings'].items()])

        return self.holdings

    def _get_holdings_xml(self) -> dict:
        holdings = {}
        soup = BeautifulSoup(self._file, "lxml")
        entries = soup.find_all("infotable")
        for entry in entries:
            name = entry.find_all("nameofissuer")[0].text
            cusip = entry.find_all("cusip")[0].text
            no_shares = entry.find_all("sshprnamt")[0].text
            market_value = entry.find_all("value")[0].text
            _type = entry.find_all("sshprnamttype")[0].text
            try:
                option = entry.find_all("putcall")[0].text
            except:
                option = None
            if any(item in ("0", "") for item in (no_shares, market_value, cusip)) or len(cusip) != 9:
                    pass
            no_shares = float(no_shares.replace(",",""))
            market_value = float(market_value.replace(",",""))
            holdings[(name, cusip, option)] = holdings.get((cusip, option), np.array([0, 0])) + np.array([market_value, no_shares])
        return holdings

    def _get_holdings_text(self) -> dict:
        items = re.findall("([0-9A-Za-z]{8,9})0{0,3}\s+\${0,1}\s*(\({0,1}[0-9.,]+\){0,1})\s+\${0,1}\s*([0-9.,\(\)]+)\s+(SH|PRN|CALL|PUT|)(\s+CALL|\s+PUT|\s+|\t)", self._file)
        for item in items:
            cusip, market_value, no_shares, _type, option = item
            no_shares = self._convert_number(no_shares)
            market_value = self._convert_number(market_value)
            if any(item in ("0", "") for item in (no_shares, market_value, cusip)) or len(cusip) not in (8,9):
                continue
            option = option.strip()
            if "CALL" in _type:
                option = "CALL"
            elif "PUT" in _type:
                option ="PUT"
            elif option not in ("CALL", "PUT"):
                option = None
            holdings[(cusip, option)] = holdings.get((cusip, option), np.array([0, 0])) + np.array([market_value, no_shares])
        return holdings

    def _convert_number(self, value: str) -> float:
        if "(" in value and ")" in value:
            value = float(value.replace(",","").replace("(", "").replace(")", "")) * (-1)
        else:
            value = float(value.replace(",",""))
        return value

    def _get_quarter(self) -> dict:
        date = re.findall("CONFORMED PERIOD OF REPORT:\t([0-9]{8})", self._file)[0]
        year, month = int(date[:4]), int(date[4:6])
        quarter = (month - 1) // 3 + 1
        return {"quarter" : (quarter, year)}

# -------------------------------------------------------------------------------------------------------------------------------------------

class Filing13D(SECFiling):
    def __init__(self, file):
        super(Filing13D, self).__init__(file)

    def parse(self):
        pass
    
    def _get_cusip(self, row) -> str:
        pass

    def _get_percentage_acquired(self, row) -> float:
        pass

    def _get_amount_shares_acquired(self, row) -> int:
        pass


class Filing13G(Filing13D):
    pass

# -------------------------------------------------------------------------------------------------------------------------------------------

class Filing4(SECFiling):
    def __init__(self, file):
        super(Filing4, self).__init__(file)


class Filing5(Filing4):
    pass


class Filing6(Filing4):
    pass


# -------------------------------------------------------------------------------------------------------------------------------------------

class Filing10K(SECFiling):
    income_variables = (
        "Revenues",
        "Cost of Revenues",
        # ------------------
        "Research and Development Expenses"
        "General and Administrative Expenses",
        "Depreciation and Amortization",
        "Total Operating Expenses"
        # ------------------
        "Operating Income",
        # ------------------
        "Interest Income",
        "Interest Expenses",
        "Pretax Income",
        # ------------------
        "Tax Expenses"
        "Net Income",
        # ------------------
        "EPS basic",
        "EPS diluted",
        "No. of basic Shares outstanding",
        "No. of diluted Shares outstanding",
        "Dividends per Share"
)

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

    def __init__(self, file):
        super(Filing10A, self).__init__(file)
        self._quarter = self._parse_quarter()

    def parse(self) -> dict:
        return {**self.get_company_information, **self.get_fundamental_data}


    def header_information(self):
        super().header_information()
        self.company_information["quarter"] = self._quarter
        return self.company_information

    def _parse_quarter(self) -> tuple:
        date = re.findall("CONFORMED PERIOD OF REPORT:\t([0-9]+)", self._file)[0]
        year = int(date[:4])
        month = int(date[4:6])
        quarter = (month-1) // 3 + 1
        return quarter, year


    def get_fundamental_data(self) -> dict:
        self.fundamental_data = {}
        self.fundamental_data["income statement"] = self.income_statement()
        self.fundamental_data["balance sheet"] = self.balance_sheet()
        self.fundamental_data["cashflow statement"] = self.cashflow_statement()

        return self.fundamental_data

    def income_statement(self) -> pd.DataFrame:
        pass

    def balance_sheet(self) -> pd.DataFrame:
        pass

    def cashflow_statement(self) -> pd.DataFrame:
        pass

    def _parse_income_statement(self, variables = None) -> dict:
        if isinstance(variables, str):
            variables = (variables,)

    def _parse_balance_sheet_statement(self, variables = None) -> dict:
        if isinstance(variables, str):
            variables = (variables,)

    def _parse_cashflow_statement(self, variables = None) -> dict:
        if isinstance(variables, str):
            variables = (variables,)

    def _get_income_statement(self) -> pd.DataFrame:
        #tables = pd.read_html(self.file)
        
        tables = []
        delimiter = "</table>"
        for table in self._file.split(delimiter):
            table = table + delimiter
            try:
                table = pd.read_html(table)[0]
            except:
                continue
            if any(all([any(var.lower() in str(row).lower() for row in col) for var in self.income_variables]) for col in table.to_numpy().T):
                break
        return table

    def _get_balance_sheet_statement(self) -> pd.DataFrame:
        pass

    def _get_cashflow_stetement(self) -> pd.DataFrame:
        pass

    @property
    def quarter(self):
        return self._quarter


class Filing10Q(Filing10K):
    pass

