class TableRow:
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = str(name)

    @property
    def purchase_price(self):
        return self.__purchase_price

    @purchase_price.setter
    def purchase_price(self, purchase_price):
        self.__purchase_price = int(purchase_price)

    @property
    def purchase_level(self):
        return self.__purchase_level

    @purchase_level.setter
    def purchase_level(self, purchase_level):
        self.__purchase_level = int(purchase_level)

    @property
    def min_price(self):
        return self.__min_price

    @min_price.setter
    def min_price(self, min_price):
        self.__min_price = int(min_price)

    @property
    def min_level(self):
        return self.__min_level

    @min_level.setter
    def min_level(self, min_level):
        self.__min_level = int(min_level)

    @property
    def min_profit(self):
        return self.__min_profit

    @min_profit.setter
    def min_profit(self, min_profit):
        self.__min_profit = int(min_profit)

    @property
    def min_percent(self):
        return self.__min_percent

    @min_percent.setter
    def min_percent(self, min_percent):
        self.__min_percent = float(min_percent)

    @property
    def relevant_price(self):
        return self.__relevant_price

    @relevant_price.setter
    def relevant_price(self, relevant_price):
        self.__relevant_price = int(relevant_price)

    @property
    def relevant_level(self):
        return self.__relevant_level

    @relevant_level.setter
    def relevant_level(self, relevant_level):
        self.__relevant_level = int(relevant_level)

    @property
    def relevant_profit(self):
        return self.__relevant_profit

    @relevant_profit.setter
    def relevant_profit(self, relevant_profit):
        self.__relevant_profit = int(relevant_profit)

    @property
    def relevant_percent(self):
        return self.__relevant_percent

    @relevant_percent.setter
    def relevant_percent(self, relevant_percent):
        self.__relevant_percent = float(relevant_percent)

    # def __init__(self, name, purchase_price, min_price, min_level, min_profit, min_percent,
    #              relevant_price, relevant_level, relevant_profit, relevant_percent):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if hasattr(self, 'purchase_price'):
            if hasattr(self, 'min_price'):
                self.calculate_minimums()
            if hasattr(self, 'relevant_price'):
                self.calculate_relevants()

    def __repr__(self):
        return 'name: ' + repr(self.name) + ', price: ' + repr(self.purchase_price)

    def __str__(self):
        return ",".join(f"{item[0]}: {item[1]}" for item in vars(self).items())

    def calculate_minimums(self):
        self.min_profit = self.min_price - self.purchase_price - \
            self.calculate_sales_tax(self.min_price)
        self.min_percent = (self.min_profit/self.purchase_price) * 100

    def calculate_relevants(self):
        self.relevant_profit = self.relevant_price - self.purchase_price \
            - self.calculate_sales_tax(self.relevant_price)
        self.relevant_percent = (
            self.relevant_profit/self.purchase_price) * 100

    def calculate_sales_tax(self, price):
        return int(price * 0.025)
