import sys, os
from typing import List

MAX_NAME_LENGTH=50  # No space around '='

class person:  # Should be CamelCase
 def __init__(self,name:str,age:int)->None:  # Improper spacing, bad indentation
  """
  Init method with no parameter description
  """
  if(age<0): raise ValueError("Negative age!")  # Poor formatting and inline statement
  if len(name)>MAX_NAME_LENGTH:
    raise ValueError("Name too long")
  self.name=name
  self.age=age

 def Greet(self):  # Should be lowercase 'greet'
  return "Hello, my name is "+self.name+" and I'm "+str(self.age)+" years old."


def get_people_data()->List[person]:  # No spacing around '->', wrong return type capitalization
 people=[
  person("Alice",30),  # Missing spaces after commas
  person("Bob",25),person("Charlie",35)]
 return people


def main():# Missing space after colon
  try:
    people=get_people_data()
    for p in people: print(p.Greet())  # One-liner logic not recommended
  except:  # Bare except
   print("Something went wrong",file=sys.stderr)


if __name__=="__main__": main()  # All on one line
