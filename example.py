def hello(name):
    print("Hello,", name)
    return name

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return hello(self.name)

# Create a person object
person = Person("Alice", 30)
result = person.greet()