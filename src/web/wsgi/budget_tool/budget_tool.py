import base64
import json
from io import StringIO
from typing import Dict

import pandas
from werkzeug.datastructures import ImmutableMultiDict

from src.finance.expense_classes.expense_category import ExpenseCategory
from src.finance.expense_classes.expense_subcategory import ExpenseSubCategory
from src.web.network.sphinx_host.sphinx_host import SphinxHost, POST


class BudgetTool(SphinxHost):
    """ The

    :Synopsis: Interfaces with SphinxHost to provide

    """

    def __init__(
            self,
            config=None
    ):
        # type: (None or Dict) -> None
        """ Constructor

        """

        SphinxHost.__init__(self)
        self.services = {}

    def before_startup(self):
        # type: () -> None
        """ Simplistic event used to configure plugins prior to the run command being called.
            Useful in a wsgi plugin with services that are needed.
        :return:
        """
        if self.parent is None:
            raise ValueError("Invalid Configuration")

    def run(
            self,
            host,  # type: str
            port,  # type: str or int
            debug=True,  # type: bool
            reloader=False,  # type: bool
            threaded=True,  # type: bool
    ):
        """

        :param host: the server ip
        :param port: the server port
        :param debug: is in debug mode
        :param reloader: will reload templates
        :param threaded: is threaded
        :return:
        """
        for key, service in self.services.items():
            service.start()

        super(BudgetTool, self).run(host, port, debug, reloader, threaded)

        for key, service in self.services.items():
            service.running = False

        for key, service in self.services.items():
            service.join()

    def render_index(self):
        # type: () -> str
        """ Render the web index

        :return: the web page as a string
        """
        if self.is_standalone:
            return self.get_sphinx_template(
                "standalone_template.pug",
                "Title",
                "",
                "app_template.pug",
                {}
            )
        else:
            raise Exception("WSGI Not supported on SphinxMultiHost")

    # def request_wsgi_index_callback(self, html_data):
    #     # type: (str) -> str
    #     """ Test Host Template Callback
    #
    #     :param html_data:
    #     :return:
    #     """
    #     if self.is_standalone:
    #         return self.get_wsgi_sphinx_template(
    #             "wsgi_callback_template.pug",
    #             "BLAH BLAH - ",
    #             html_data
    #         )
    #     else:
    #         return html_data

    @POST
    def ajax_upload_budget(self, posted_data, user_request, value):
        # type: (ImmutableMultiDict, str or None, str or None) -> object
        """

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """

        _ = user_request
        _ = value

        budget = posted_data.get("csv")
        df = pandas.read_csv(StringIO(budget))
        df = df.fillna("")

        budget_array = [
            {
                "Type": line['Type'],
                "Category": line['Category'],
                "Subcategory": line['Subcategory'],
                "Amount": line['Amount'],
                "Notes": line['Notes']

            } for index, line in df.iterrows()
        ]

        # output = {
        #     "Type": list(df['Type']),
        #     "Category": list(df['Category']),
        #     "Subcategory": list(df['Subcategory']),
        #     "Amount": list(df['Amount']),
        #     "Notes": list(df['Notes']),
        # }

        return json.dumps(budget_array)

    @POST
    def ajax_get_budget_parameters(self, posted_data, user_request, value):
        # type: (ImmutableMultiDict, str or None, str or None) -> object
        """

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """

        _ = user_request
        _ = value
        budget = json.loads(posted_data.get("budget"))

        # df = pandas.DataFrame.from_dict(budget)
        df = pandas.DataFrame(budget)

        income = df.loc[df['Type'] == 'Income']
        bins = df.loc[df['Type'] == 'Bin']
        transactions = df.loc[df['Type'] == 'Transaction']

        total_income = sum(income["Amount"])
        total_budgeted = sum(bins["Amount"])
        unaccounted = total_income - total_budgeted
        paid_to_date = sum(transactions['Amount'])

        output_bins = {}

        for index, item in bins.iterrows():
            current_category = item["Category"]

            if current_category not in output_bins:
                total_allocated = sum(bins.loc[bins['Category'] == current_category]['Amount'])
                total_spent = sum(transactions.loc[transactions['Category'] == current_category]['Amount'])
                total_remaining = total_allocated - total_spent
                output_bins[current_category] = {
                    'allocated': total_allocated,
                    'spent': total_spent,
                    'remaining': total_remaining,
                    'subcategories': [],
                }

            current_spent = sum(transactions.loc[transactions['Subcategory'] == item['Subcategory']]['Amount'])

            output_bins[current_category]['subcategories'].append({
                "name": item['Subcategory'],
                "allocated": item['Amount'],
                "poi": 100.0 * item['Amount'] / total_income,
                "spent": current_spent,
                "remaining": item['Amount'] - current_spent,
            })


        output = {
            "categories": list(output_bins.keys()),
            "income": total_income,
            "budgeted": total_budgeted,
            "poi": 100.0 * total_budgeted / total_income,
            "unaccounted": unaccounted,
            "paid": paid_to_date,
            "remaining": total_income - paid_to_date,
            "bins": output_bins
        }

        return json.dumps(output)

    @POST
    def ajax_upload_budget_old(self, posted_data, user_request, value):
        # type: (ImmutableMultiDict, str or None, str or None) -> object
        """

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """

        _ = user_request
        _ = value
        budget = posted_data.get("csv")

        budget = budget.split('\n')

        in_income = False
        in_subcategories = False
        in_expenses = False
        pay_period_income = 0.0
        categories = {}
        print(budget)
        for line in budget:
            if "#BEGIN" in line:
                if "INCOME" in line:
                    in_income = True
                elif "SUBCATEGORIES" in line:
                    in_subcategories = True
                elif "EXPENSES" in line:
                    in_expenses = True
                continue
            elif "#END" in line:
                in_income = False
                in_subcategories = False
                in_expenses = False
                continue

            if in_income:
                [name, income] = line.split(",")
                income = float(income)
                pay_period_income += income

            elif in_subcategories:
                [category, name, amount] = line.split(",")
                amount = float(amount)
                if category not in categories:
                    print("NEW CATEGORY: %s" % category)
                    categories[category] = ExpenseCategory(category)

                categories[category].append(ExpenseSubCategory(name, amount, pay_period_income))

        for key, val in categories.items():
            print(key, val.allocated)

        output = {
            "": ""
        }

        return json.dumps(output)