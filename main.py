def factorial(n):
    """
    Calculates the factorial of a non-negative integer.

    Args:
        n: The non-negative integer for which to calculate the factorial.

    Returns:
        The factorial of n.  Returns 1 if n is 0.
        Raises ValueError if n is negative or not an integer.
    """

    #Error Handling: Check for valid input
    if not isinstance(n, int):
        raise ValueError("Input must be an integer.")
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")

    #Base Case: Factorial of 0 is 1
    if n == 0:
        return 1

    #Recursive Calculation (can also be done iteratively)
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result


#Example Usage
try:
    number = 5
    result = factorial(number)
    print(f"The factorial of {number} is {result}")

    number = 0
    result = factorial(number)
    print(f"The factorial of {number} is {result}")

    number = -1
    result = factorial(number)
    print(f"The factorial of {number} is {result}")

except ValueError as e:
    print(f"Error: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
