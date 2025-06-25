import sys

MAX_NAME_LENGTH = 50

class person:
    def __init__(self, Name, Age):
        if Age < 0:
            print("Negative age! Setting to 0.")
            Age = 0
        if len(Name) > MAX_NAME_LENGTH:
            print("Name too long")
        self.Name = Name
        self.Age = Age

    def Greeting(self):
        print("Hi my name is " + self.Name + " and age is " + str(self.Age))

def GetPeople():
    return [
        person("Alice", 30),
        person("Bob", -5),
        person("ThisNameIsWayTooLongAndShouldDefinitelyTriggerTheCheckButWon't", 25)
    ]

def Main():
    try:
        p = GetPeople()
        for x in p:
            x.Greeting()
    except:
        print("Something went wrong")

Main()
