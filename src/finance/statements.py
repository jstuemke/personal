import re

from PyPDF2 import PdfFileReader
from src.finance.known_businesses import BUSINESS_NAMES, BUSINESSES_SHORTHAND


class SunTrustExpense(object):

    def __init__(self, transaction_details=None, year=None):

        self._amount = None
        self._transaction_date = None
        self._company = None

        if transaction_details is not None:
            self._get_props(transaction_details)

    def _get_props(self, detail_string):

        self.amount = float(re.findall(r"[-+]?\d*\.\d+|\d+", detail_string)[-1])
        self.transaction_date = re.search(r"TR DATE |\d{2} / \d{2}", detail_string).group(0).replace(" ", "")

        try:
            other_details = re.search(r"TR DATE \d{2} / \d{2} (.*?) \d*\.\d*", detail_string).group(1)
        except AttributeError:
            other_details = self._no_transaction_date(detail_string)

        other_details = other_details.upper().replace(" ", "")
        starts_with = other_details[0]

        for business in BUSINESSES_SHORTHAND.get(starts_with, []):
            if business in other_details:
                self.company = BUSINESS_NAMES[business]
                break

    def _no_transaction_date(self, detail_string):

        other_details = re.search(r"\d{2} / \d{2} (.*?) \d*\.\d*", detail_string).group(1)
        return other_details


    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    @property
    def transaction_date(self):
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value):
        self._transaction_date = value

    @property
    def company(self):
        return self._company

    @company.setter
    def company(self, value):
        self._company = value


if __name__ == '__main__':

    purchase_types = [
        "Check Card Purchase",
        "Point of Sale Debit",
        "Electronic/ACH Debit"
    ]

    income_types = [
        "Mobile Check Deposit",
        "Electronic/ACH Credit",
        "Check Card Credit",
        "Mobile App Transfer",
        "Point of Sale Credit"
    ]
    expenses = []

    with open("C:\\Users\\Luke\\Desktop\\statement_july2018.pdf", 'rb') as pdf:
        filereader = PdfFileReader(pdf)

        total_expenses = 0
        page = filereader.getPage(1)
        # for page in filereader.pages:
        page_text = page.extractText().replace("\n", " ")

        print("#" * 50)
        for purchase_type in purchase_types:
            for item in re.finditer(r"\d{2} / \d{2} %s (.*?) \d*\.\d*" % purchase_types[2], page_text):
                details = item.group(0)
                expense = SunTrustExpense(transaction_details=details)
                expenses.append(expense)
                print(details)
                # if expense.company is None:
                #     print(details)

                total_expenses += expense.amount
                print("%s: %f\n" % (expense.company, expense.amount))
        # print("Total Spent: $%.2f" % total_expenses)
        # print(len(expenses))






















