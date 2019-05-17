from typing import List


class ExpenseCategory(List):

    def __init__(self, name, allocated):

        super().__init__()

        self.name = name
        self.allocated = allocated
        self._spent = None

    @property
    def spent(self):
        if self._spent is None:
            self._spent = sum([p.spent for p in self])
        return self._spent

    @property
    def remaining(self):
        return self.allocated - self._spent

