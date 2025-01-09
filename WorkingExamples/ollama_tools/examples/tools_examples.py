from ollama_tools.tools_engine import TOOLSEngine
from typing import List, Dict, Optional, Any
import math
from datetime import datetime, timedelta

def calculate_compound_interest(principal: float, rate: float, time: float, compounds_per_year: int = 12) -> Dict[str, float]:
    """
    Calculate compound interest for an investment
    
    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as a decimal, e.g., 0.05 for 5%)
        time: Investment period in years
        compounds_per_year: Number of times interest is compounded per year
    
    Returns:
        Dict containing final amount and interest earned
    """
    # Convert percentage to decimal if needed
    if rate > 1:
        rate = rate / 100
        
    final_amount = principal * (1 + rate/compounds_per_year)**(compounds_per_year*time)
    interest_earned = final_amount - principal
    
    return {
        "final_amount": round(final_amount, 2),
        "interest_earned": round(interest_earned, 2),
        "input_rate_percent": rate * 100
    }

def validate_password(password: str, min_length: int = 8, require_special: bool = True) -> Dict[str, bool]:
    """Check if a password meets security requirements"""
    return {
        "length_ok": len(password) >= min_length,
        "has_upper": any(c.isupper() for c in password),
        "has_lower": any(c.islower() for c in password),
        "has_number": any(c.isdigit() for c in password),
        "has_special": any(not c.isalnum() for c in password) if require_special else True
    }

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin
    Accepts both full unit names and abbreviations (e.g., 'Celsius'/'C', 'Fahrenheit'/'F', 'Kelvin'/'K')
    """
    # Normalize units to single letter
    unit_map = {
        'CELSIUS': 'C',
        'FAHRENHEIT': 'F',
        'KELVIN': 'K',
        'C': 'C',
        'F': 'F',
        'K': 'K'
    }
    
    from_unit = unit_map.get(from_unit.upper())
    to_unit = unit_map.get(to_unit.upper())
    
    if not from_unit or not to_unit:
        raise ValueError(f"Invalid temperature unit. Valid units are: Celsius/C, Fahrenheit/F, Kelvin/K")

    conversions = {
        "C_to_F": lambda x: x * 9/5 + 32,
        "F_to_C": lambda x: (x - 32) * 5/9,
        "C_to_K": lambda x: x + 273.15,
        "K_to_C": lambda x: x - 273.15,
        "F_to_K": lambda x: (x - 32) * 5/9 + 273.15,
        "K_to_F": lambda x: (x - 273.15) * 9/5 + 32
    }
    
    key = f"{from_unit}_to_{to_unit}"
    if key not in conversions:
        if from_unit == to_unit:
            return round(value, 2)
        raise ValueError(f"Unsupported conversion: {from_unit} to {to_unit}")
        
    return round(conversions[key](value), 2)

def analyze_text(text: str) -> Dict[str, Any]:
    """Analyze text and return statistics"""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "avg_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
        "sentence_count": text.count('.') + text.count('!') + text.count('?')
    }

def calculate_mortgage(principal: float, annual_rate: float, years: int) -> Dict[str, float]:
    """
    Calculate mortgage payment details
    
    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate (as a percentage, e.g., 3.5 for 3.5%)
        years: Loan term in years
    
    Returns:
        Dict containing monthly payment, total payment, and total interest
    """
    # Convert annual rate from percentage to decimal
    annual_rate = annual_rate / 100  # Convert from percentage
    
    # Convert to monthly rate
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    # Handle edge case when rate is 0
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        # Standard mortgage payment formula
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }

def main():
    # Initialize the engine
    engine = TOOLSEngine("llama3.2")
    
    # Add all tools
    tools = [
        calculate_compound_interest,
        validate_password,
        convert_temperature,
        analyze_text,
        calculate_mortgage
    ]
    for tool in tools:
        engine.add_tool(tool)
    
    # Example 1: Compound Interest
    print("Example 1: Compound Interest")
    response, calls = engine.chat("Calculate the compound interest for $1000 invested at 5% for 2 years")
    print(f"Response: {response}\n")

    # Example 2: Password Validation
    print("Example 2: Password Validation")
    response, calls = engine.chat("Is the password 'SecurePass123!' valid?")
    print(f"Response: {response}\n")

    # Example 3: Temperature Conversion
    print("Example 3: Temperature Conversion")
    response, calls = engine.chat("Convert 25 degrees Celsius to Fahrenheit")
    print(f"Response: {response}\n")

    # Example 4: Text Analysis
    print("Example 4: Text Analysis")
    response, calls = engine.chat("Analyze this text: 'The quick brown fox jumps over the lazy dog. It was amazing!'")
    print(f"Response: {response}\n")

    # Example 5: Mortgage Calculation
    print("Example 5: Mortgage Calculation")
    response, calls = engine.chat("Calculate mortgage payments for a $300,000 loan at 3.5% interest for 30 years")
    print(f"Response: {response}\n")

    # Example 6: Combined Tools Usage
    print("Example 6: Combined Tools Usage")
    response, calls = engine.chat("""I need to:
    1. Convert 30°C to Fahrenheit
    2. Calculate compound interest on $5000 at 4% for 3 years
    Can you help with both?""")
    print(f"Response: {response}\n")

if __name__ == "__main__":
    main()
