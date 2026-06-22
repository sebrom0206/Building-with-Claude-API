import math
from main import calculate_pi


def test_calculate_pi():
    """Test the calculate_pi function"""
    
    # Test 1: Calculate pi to 5 decimal places
    result = calculate_pi(5)
    expected = 3.14159
    print(f"Test 1 - Pi to 5 decimal places:")
    print(f"  Result: {result}")
    print(f"  Expected: {expected}")
    print(f"  Match: {result == expected}")
    print()
    
    # Test 2: Compare with math.pi
    result_5 = calculate_pi(5)
    math_pi_5 = round(math.pi, 5)
    print(f"Test 2 - Compare with math.pi (5 decimals):")
    print(f"  Our result: {result_5}")
    print(f"  math.pi:    {math_pi_5}")
    print(f"  Match: {result_5 == math_pi_5}")
    print()
    
    # Test 3: Different decimal places
    for decimals in [1, 2, 3, 4, 5]:
        result = calculate_pi(decimals)
        expected = round(math.pi, decimals)
        match = result == expected
        print(f"Test 3.{decimals} - Pi to {decimals} decimal(s): {result} (Expected: {expected}) - {'PASS' if match else 'FAIL'}")
    print()
    
    # Test 4: Verify it's close to actual pi
    result = calculate_pi(5)
    difference = abs(result - math.pi)
    print(f"Test 4 - Accuracy check:")
    print(f"  Calculated pi: {result}")
    print(f"  Actual pi:     {math.pi}")
    print(f"  Difference:    {difference}")
    print(f"  Within 0.00001: {difference < 0.00001}")
    print()
    
    print("=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    test_calculate_pi()
