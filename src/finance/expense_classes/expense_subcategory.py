from typing import List


class ExpenseSubCategory(List):

    def __init__(self, name, pay_perion_allocation, pay_period_income):
        # type: (str, float, float) -> None

        super().__init__()

        self.name = name
        self.allocated = pay_perion_allocation
        self.percent = 100.0 * pay_perion_allocation / pay_period_income

    @property
    def spent(self):
        return sum([expense.amount for expense in self])

    @property
    def remaining(self):
        return self.allocated - self.spent

