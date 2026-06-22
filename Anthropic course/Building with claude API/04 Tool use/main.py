def greeting():
    print("Hi there")


def calculate_pi(decimal_places=5):
    """
    Calculate pi to the specified number of decimal places.
    Uses the Leibniz formula: pi = 4 * (1 - 1/3 + 1/5 - 1/7 + 1/9 - ...)
    
    Args:
        decimal_places: Number of decimal places to calculate (default: 5)
    
    Returns:
        float: Approximation of pi rounded to the specified decimal places
    """
    pi_approx = 0.0
    iterations = 1000000  # Enough iterations for good precision
    
    for i in range(iterations):
        term = ((-1) ** i) / (2 * i + 1)
        pi_approx += term
    
    pi_approx *= 4
    
    # Round to the specified decimal places
    return round(pi_approx, decimal_places)
