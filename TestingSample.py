import sys
from typing import List


MAX_NAME_LENGTH = 50


class Person:
    """A class representing a person."""

    def __init__(self, name: str, age: int) -> None:
        """
        Initialize a new Person instance.

        Args:
            name (str): The person's name.
            age (int): The person's age.

        Raises:
            ValueError: If age is negative or name is too long.
        """
        if age < 0:
            raise ValueError("Age cannot be negative.")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(f"Name cannot exceed {MAX_NAME_LENGTH} characters.")

        self.name = name
        self.age = age

    def greet(self) -> str:
        """Return a greeting message."""
        return f"Hello, my name is {self.name} and I'm {self.age} years old."


def get_people_data() -> List[Person]:
    """Mock function to return sample data."""
    return [
        Person(name="Alice", age=30),
        Person(name="Bob", age=25),
        Person(name="Charlie", age=35)
    ]


def main() -> None:
    """Main entry point of the application."""
    try:
        people = get_people_data()
        for person in people:
            print(person.greet())

    except ValueError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
