from tools_ollama.tools_engine import TOOLSEngine
from typing import List, Dict, Optional
import math
from datetime import datetime, timedelta

# Example tool functions
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

def calculate_investment_growth(monthly_investment: float, rate: float, years: float) -> Dict[str, float]:
    """
    Calculate growth of regular monthly investments
    
    Args:
        monthly_investment: Amount invested each month
        rate: Annual interest rate (as a decimal or percentage)
        years: Investment period in years
    
    Returns:
        Dict containing future value and total contributions
    """
    # Convert percentage to decimal if needed
    if rate > 1:
        rate = rate / 100
        
    # Convert to monthly rate
    monthly_rate = rate / 12
    num_payments = years * 12
    
    # Calculate future value of regular payments
    future_value = monthly_investment * ((1 + monthly_rate)**(num_payments) - 1) / monthly_rate
    total_contributions = monthly_investment * num_payments
    
    return {
        "future_value": round(future_value, 2),
        "total_contributions": round(total_contributions, 2),
        "total_interest_earned": round(future_value - total_contributions, 2),
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
def analyze_text(text: str) -> Dict[str, any]:
    """Analyze text and return statistics"""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "sentence_count": text.count('.') + text.count('!') + text.count('?')
    }

def calculate_mortgage(principal: float, annual_rate: float, years: int) -> Dict[str, float]:
    """Calculate mortgage payment details"""
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return {
        "monthly_payment": round(payment, 2),
        "total_payment": round(payment * num_payments, 2),
        "total_interest": round((payment * num_payments) - principal, 2)
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

    # Example 6: Combined Tools
    print("Example 6: Combined Tools Usage")
    response, calls = engine.chat("""I need to:
    1. Convert 30°C to Fahrenheit
    2. Calculate compound interest on $5000 at 4% for 3 years
    Can you help with both?""")
    print(f"Response: {response}\n")

    # Example 7: Password Analysis with Custom Requirements
    print("Example 7: Custom Password Validation")
    response, calls = engine.chat("Check if 'SimplePass123' is valid with a minimum length of 12 characters")
    print(f"Response: {response}\n")

    # Example 8: Multiple Temperature Conversions
    print("Example 8: Multiple Conversions")
    response, calls = engine.chat("Convert 100°F to both Celsius and Kelvin")
    print(f"Response: {response}\n")

    # Example 9: Complex Text Analysis
    print("Example 9: Complex Text Analysis")
    response, calls = engine.chat("""Analyze the following text:
    'This is a sample paragraph. It contains multiple sentences! How many are there? Let's find out.'""")
    print(f"Response: {response}\n")

    # Example 10: Investment Comparison
    print("Example 10: Investment Comparison")
    response, calls = engine.chat("""Compare the compound interest for these scenarios:
    1. $10000 at 3% for 5 years
    2. $8000 at 4% for 6 years""")
    print(f"Response: {response}\n")

    # Example 11: Password Strength Comparison
    print("Example 11: Password Comparison")
    response, calls = engine.chat("""Compare the strength of these passwords:
    1. 'SecurePass123!'
    2. 'SimplePassword'""")
    print(f"Response: {response}\n")

    # Example 12: Temperature Conversion Chain
    print("Example 12: Temperature Chain")
    response, calls = engine.chat("If it's 50°F outside, what is that in Celsius? And what would that Celsius temperature be in Kelvin?")
    print(f"Response: {response}\n")

    # Example 13: Mortgage Comparison
    print("Example 13: Mortgage Comparison")
    response, calls = engine.chat("""Compare monthly payments for these mortgages:
    1. $250000 at 3% for 30 years
    2. $250000 at 3% for 15 years""")
    print(f"Response: {response}\n")

    # Example 14: Text Statistics Comparison
    print("Example 14: Text Comparison")
    response, calls = engine.chat("""Compare these texts:
    Text 1: 'The quick brown fox.'
    Text 2: 'The lazy dog sleeps soundly beneath the warm sun.'""")
    print(f"Response: {response}\n")

    # Example 15: Investment Planning
    print("Example 15: Investment Planning")
    response, calls = engine.chat("""If I invest $1000 today at 5% interest, calculate:
    1. Value after 1 year
    2. Value after 5 years
    3. Value after 10 years""")
    print(f"Response: {response}\n")

    # Example 16: Password Policy Check
    print("Example 16: Password Policy")
    response, calls = engine.chat("""Check these passwords against a strict policy (min length 12, special chars required):
    1. 'SimplePass123'
    2. 'ComplexPass123!@'""")
    print(f"Response: {response}\n")

    # Example 17: Temperature Analysis
    print("Example 17: Temperature Analysis")
    response, calls = engine.chat("""A weather station recorded 25°C. Convert this to:
    1. Fahrenheit for US readers
    2. Kelvin for scientific records""")
    print(f"Response: {response}\n")

    # Example 18: Mortgage Refinancing
    print("Example 18: Mortgage Refinancing")
    response, calls = engine.chat("""Compare current mortgage ($300000, 4%, 30 years) with refinancing options:
    1. Same amount at 3% for 30 years
    2. Same amount at 3.5% for 20 years""")
    print(f"Response: {response}\n")

    # Example 19: Content Analysis
    print("Example 19: Content Analysis")
    response, calls = engine.chat("""Analyze these product descriptions:
    1. 'Premium leather wallet with RFID protection.'
    2. 'Handcrafted leather wallet featuring 8 card slots and premium stitching.'""")
    print(f"Response: {response}\n")

    # Example 20: Combined Financial Analysis
    print("Example 20: Combined Financial Analysis")
    response, calls = engine.chat("""Help me with this financial planning:
    1. Calculate mortgage for $200000 at 3.5% for 30 years
    2. Calculate how much $500 monthly investment will grow at 6% interest for 10 years""")
    print(f"Response: {response}\n")

if __name__ == "__main__":
    main()