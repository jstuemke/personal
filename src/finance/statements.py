import re
import numpy as np
from typing import List

from PyPDF2 import PdfFileReader
from src.finance.known_businesses import BUSINESSES_SHORTHAND, BUSINESS_DETAILS
from matplotlib import pyplot as plt

PURCHASE_TYPES = [
    "ATM Cash Withdrawal",
    "Recurring Check Card Purchase",
    "Check Card Purchase",
    "Point of Sale Debit",
    "Electronic/ACH Debit"
]

INCOME_TYPES = [
    "Mobile Check Deposit",
    "Electronic/ACH Credit",
    "Check Card Credit",
    "Mobile App Transfer",
    "Point of Sale Credit"
]


class SunTrustExpense(object):

    def __init__(self, transaction_details=None, year=None):

        self._details = None
        self._amount = None
        self._transaction_date = None
        self._company = None
        self._purchase_type = None
        self._category = None

        if transaction_details is not None:
            self._get_props(transaction_details)

    def _get_props(self, trans_details):

        self.details = trans_details
        for ptype in PURCHASE_TYPES:
            if ptype.upper() in self.details.upper():
                self.purchase_type = ptype

        self.amount = float(re.findall(r"\d*\.\d*", self.details.replace(",", ""))[-1])
        self.transaction_date = re.search(r"TR DATE |\d{2} / \d{2}", self.details).group(0).replace(" ", "")

        try:
            other_details = re.search(r"TR DATE \d{2} / \d{2} (.*?) \d*\.\d*", self.details).group(1)
        except AttributeError:
            other_details = self._no_transaction_date()

        other_details = re.sub(r'[^\w\s]', '', other_details)
        other_details = other_details.upper().replace(" ", "")
        starts_with = other_details[0]

        for business in BUSINESSES_SHORTHAND.get(starts_with, []):
            if business in other_details:
                self.company = BUSINESS_DETAILS[business][0]
                self.category = BUSINESS_DETAILS[business][1]
                break

    def _no_transaction_date(self):

        other_details = re.search(r"%s (.*?)\.\d{2}" % self._purchase_type, self.details).group(1)
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

    @property
    def purchase_type(self):
        return self._purchase_type

    @purchase_type.setter
    def purchase_type(self, value):
        self._purchase_type = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value


class BankStatement(List):

    def __init__(self, path_to_pdf=None):
        super().__init__()

        self._period_start = None
        self._period_end = None
        self._account_number = None
        self._expense_total = None
        self._daily_mean = None
        self._expense_amounts = None
        self._dates = None
        self._categories = {}

        with open(path_to_pdf, 'rb') as pdf:
            filereader = PdfFileReader(pdf)

            self.expense_total = 0
            summary_page = filereader.getPage(0).extractText().replace("\n", " ")
            for item in re.finditer(r"\d{13} \d{2} / \d{2} / \d{4} - \d{2} / \d{2} / \d{4}", summary_page):
                group = item.group(0).split(" ")
                self.account_number = int(group[0])
                date_range = ''.join(group[1:]).split("-")
                self._period_start = date_range[0]
                self._period_end = date_range[1]

            for page in filereader.pages:
                page_text = page.extractText().replace("\n", " ")

                # print("#" * 50)

                for purchase_type in PURCHASE_TYPES:
                    for item in re.finditer(r"\d{2} / \d{2} %s (.*?)\.\d{2}" % purchase_type, page_text):

                        expense = SunTrustExpense(transaction_details=item.group(0))
                        self.append(expense)
                        if expense.category not in self._categories:
                            self._categories[expense.category] = expense.amount
                        else:
                            self._categories[expense.category] += expense.amount

                        # print("We spent $%.2f at %s on %s" % (expense.amount, expense.company, expense.transaction_date))

                        self.expense_total += expense.amount
                        # print("%s: %f\n" % (expense.company, expense.amount))

                if "Totals" in page_text:
                    if "Credit and Debit Totals" in page_text:
                        break
        self.dates = []
        self.expense_amounts = []
        for expense in self:
            current_date = expense.transaction_date
            current_amount = expense.amount
            if current_date in self.dates:
                self.expense_amounts[self.dates.index(current_date)] += current_amount
            else:
                self.dates.append(current_date)
                self.expense_amounts.append(current_amount)

        self.daily_mean = np.mean(self.expense_amounts)


    def plot_expenses(self):

        plt.figure()
        plt.plot(self.dates, self.expense_amounts)
        plt.plot([self.dates[0], self.dates[-1]], [self.daily_mean, self.daily_mean])
        plt.title("Expense Breakdown for %s - %s" % (self.period_start, self.period_end))
        plt.ylabel("Total Daily Expenses ($)")
        plt.xlabel("Date")
        plt.legend(["Daily Expenses", "Average Daily Expense: $%.2f" % self.daily_mean])


    @property
    def period_start(self):
        return self._period_start

    @period_start.setter
    def period_start(self, value):
        self._period_start = value

    @property
    def period_end(self):
        return self._period_end

    @period_end.setter
    def period_end(self, value):
        self._period_end = value

    @property
    def account_number(self):
        return self._account_number

    @account_number.setter
    def account_number(self, value):
        self._account_number = value

    @property
    def expense_total(self):
        return self._expense_total

    @expense_total.setter
    def expense_total(self, value):
        self._expense_total = value

    @property
    def daily_mean(self):
        return self._daily_mean

    @daily_mean.setter
    def daily_mean(self, value):
        self._daily_mean = value

    @property
    def expense_amounts(self):
        return self._expense_amounts

    @expense_amounts.setter
    def expense_amounts(self, value):
        self._expense_amounts = value

    @property
    def dates(self):
        return self._dates

    @dates.setter
    def dates(self, value):
        self._dates = value


if __name__ == '__main__':

    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
    ]
    totals = []
    paypal = 0
    for month in months:
        statement = BankStatement("C:\\Users\\Luke\\Documents\\Statements\\statement_%s2018.pdf" % month)

        # print("In %s, we spent $%.2f" % (month, statement.expense_total))

        for expense in statement:
            if expense.company == "Paypal":
                print(expense.details)
                paypal += expense.amount

        totals.append(statement.expense_total)
        # statement.plot_expenses()

    print("Christa spent $%.2f on Rae Dunn this year." % paypal)
    # plt.figure()
    # plt.plot(months, totals)
    # plt.ylim([0, 15000])
    # plt.show()

