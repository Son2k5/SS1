class Animal:
    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return f"Animal[{self.__name}]"


class Mammal(Animal):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return f"Mammal[{super().__str__()}]"


class Cat(Mammal):
    def __init__(self, name):
        super().__init__(name)

    def greets(self):
        print("Meow")

    def __str__(self):
        return f"Cat[{super().__str__()}]"


class Dog(Mammal):
    def __init__(self, name):
        super().__init__(name)

    def greets(self, name = None):
        if name is None:
            print("Woof")
        else:
            print("Woooof")

    def __str__(self):
        return f"Dog[{super().__str__()}]"
   
if __name__ == "__main__":
    # Test Dog's greets() method
    d1 = Dog("Akita")
    d2 = Dog("Bern")
    d1.greets()
    d1.greets(d2)
