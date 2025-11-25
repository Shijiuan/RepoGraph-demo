from utils import compute_sum

class Calculator:
    def __init__(self, data):
        self.data = data

    def total(self):
        return compute_sum(self.data)

if __name__ == "__main__":
    calc = Calculator([1, 2, 3, 4])
    print("Result:", calc.total())
