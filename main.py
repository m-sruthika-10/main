def fibonacci(n):
    fib_series = [0, 1]
    while len(fib_series) < n:
        next_fib = fib_series[-1] + fib_series[-2]
        fib_series.append(next_fib)
    return fib_series[:n]

# Example usage
n = 10  # Change this value to generate more or fewer Fibonacci numbers
print(fibonacci(n))
