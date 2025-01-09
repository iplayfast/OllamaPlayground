from ollama_tools.tools_engine import TOOLSEngine
from python_executor_tool import (
    execute_python_code,
    CICDConfig,
    IntegrationTestConfig,
    SecurityScanResults,
    ReviewComment
)

def run_examples():
    """Run various examples demonstrating the code management system"""
    
    print("=== Python Code Management System Examples ===\n")
    
    # Basic configuration
    cicd_config = CICDConfig(
        provider="github",
        config={"token": "demo-token"},
        triggers=["push", "pull_request"],
        environments=["dev", "staging", "prod"],
        deployment_targets=["aws-lambda", "kubernetes"]
    )
    
    integration_config = IntegrationTestConfig(
        dependencies=["redis", "postgresql"],
        environment_vars={"DB_URL": "postgresql://localhost:5432"},
        docker_services=["redis:latest", "postgres:13"],
        test_data={"db": "test_data.sql"},
        cleanup_steps=["docker-compose down", "rm -rf test_data"]
    )

    # Example 1: Simple Function with Documentation Analysis
    print("\n=== Example 1: Simple Function with Documentation Analysis ===")
    simple_code = """
    def calculate_bmi(weight: float, height: float) -> float:
        '''
        Calculate Body Mass Index (BMI).
        
        Args:
            weight: Weight in kilograms
            height: Height in meters
            
        Returns:
            float: Calculated BMI value
            
        Example:
            >>> calculate_bmi(70, 1.75)
            22.86
        '''
        return weight / (height ** 2)

    # Test the function
    print(calculate_bmi(70, 1.75))
    """
    
    result1 = execute_python_code(
        code=simple_code,
        filename="bmi_calculator.py",
        author="John Doe",
        description="BMI Calculator with documentation",
        tags=["health", "calculator"],
        validate_final=True
    )
    
    print("Documentation Analysis:", result1["documentation"])
    print("Execution Output:", result1["output"])

    # Example 2: Class with Security Scanning
    print("\n=== Example 2: Class with Security Scanning ===")
    class_code = """
    import hashlib
    from typing import Optional, Dict

    class UserManager:
        def __init__(self):
            self.users: Dict[str, str] = {}
            
        def add_user(self, username: str, password: str) -> bool:
            '''Add a new user with hashed password'''
            if username in self.users:
                return False
            
            # Hash password (example of good practice)
            hashed = hashlib.sha256(password.encode()).hexdigest()
            self.users[username] = hashed
            return True
            
        def verify_user(self, username: str, password: str) -> bool:
            '''Verify user credentials'''
            if username not in self.users:
                return False
            
            hashed = hashlib.sha256(password.encode()).hexdigest()
            return self.users[username] == hashed

    # Test the class
    manager = UserManager()
    print(manager.add_user("alice", "secure123"))
    print(manager.verify_user("alice", "secure123"))
    """
    
    result2 = execute_python_code(
        code=class_code,
        filename="user_manager.py",
        author="Jane Smith",
        description="Secure user management system",
        tags=["security", "user-management"],
        enable_security_scan=True
    )
    
    print("Security Scan Results:", result2["security_scan"])
    print("Execution Output:", result2["output"])

    # Example 3: Data Processing with Performance Analysis
    print("\n=== Example 3: Data Processing with Performance Analysis ===")
    processing_code = """
    from typing import List
    import time

    def process_data(numbers: List[int]) -> List[int]:
        '''
        Process a list of numbers with various operations.
        
        Args:
            numbers: List of integers to process
            
        Returns:
            List[int]: Processed numbers
        '''
        # Simulate complex processing
        time.sleep(0.1)
        
        # Multiple operations for performance testing
        result = []
        for num in numbers:
            if num % 2 == 0:
                result.append(num * 2)
            else:
                result.append(num * 3)
                
        sorted_result = sorted(result)
        filtered_result = [x for x in sorted_result if x < 100]
        return filtered_result

    # Test with a large dataset
    data = list(range(50))
    print(process_data(data)[:5])  # Show first 5 results
    """
    
    result3 = execute_python_code(
        code=processing_code,
        filename="data_processor.py",
        author="Alex Johnson",
        description="Data processing with performance monitoring",
        tags=["data-processing", "performance"],
        measure_performance=True
    )
    
    print("Performance Metrics:", result3["performance"])
    print("Execution Output:", result3["output"])

    # Example 4: API Client with Integration Tests
    print("\n=== Example 4: API Client with Integration Tests ===")
    api_code = """
    from typing import Dict, Any
    import requests

    class WeatherAPI:
        def __init__(self, base_url: str):
            self.base_url = base_url
            
        def get_weather(self, city: str) -> Dict[str, Any]:
            '''Get weather information for a city'''
            response = requests.get(f"{self.base_url}/weather?city={city}")
            return response.json()
            
        def save_weather_data(self, city: str, temperature: float):
            '''Save weather data to database'''
            # Simulated database operation
            print(f"Saving weather data: {city} - {temperature}°C")

    # Integration test setup
    api = WeatherAPI("http://api.weather.test")
    print("API client initialized")
    """
    
    result4 = execute_python_code(
        code=api_code,
        filename="weather_api.py",
        author="Maria Garcia",
        description="Weather API client with integration tests",
        tags=["api", "weather", "integration"],
        integration_test_config=integration_config
    )
    
    print("Integration Test Results:", result4["integration_tests"])
    print("Execution Output:", result4["output"])

    # Example 5: Database Interface with CI/CD Pipeline
    print("\n=== Example 5: Database Interface with CI/CD Pipeline ===")
    db_code = """
    from typing import Optional, List
    from dataclasses import dataclass

    @dataclass
    class User:
        id: int
        name: str
        email: str
        active: bool = True

    class DatabaseInterface:
        def __init__(self):
            self.users: List[User] = []
            
        def add_user(self, name: str, email: str) -> User:
            '''Add a new user to the database'''
            user_id = len(self.users) + 1
            user = User(id=user_id, name=name, email=email)
            self.users.append(user)
            return user
            
        def get_user(self, user_id: int) -> Optional[User]:
            '''Get user by ID'''
            for user in self.users:
                if user.id == user_id:
                    return user
            return None
            
        def list_users(self) -> List[User]:
            '''List all active users'''
            return [user for user in self.users if user.active]

    # Test the interface
    db = DatabaseInterface()
    user = db.add_user("Test User", "test@example.com")
    print(f"Added user: {user}")
    print(f"Users list: {db.list_users()}")
    """
    
    result5 = execute_python_code(
        code=db_code,
        filename="database_interface.py",
        author="Chris Lee",
        description="Database interface with CI/CD setup",
        tags=["database", "ci-cd"],
        cicd_config=cicd_config
    )
    
    print("CI/CD Configuration:", result5["cicd"])
    print("Execution Output:", result5["output"])

    # Example 6: Data Validation with Code Review
    print("\n=== Example 6: Data Validation with Code Review ===")
    validation_code = """
    from typing import Dict, Any, List
    from dataclasses import dataclass
    from datetime import datetime

    @dataclass
    class ValidationError:
        field: str
        message: str

    class DataValidator:
        def validate_user_data(self, data: Dict[str, Any]) -> List[ValidationError]:
            '''Validate user data against rules'''
            errors = []
            
            # Required fields
            required = ['name', 'email', 'age']
            for field in required:
                if field not in data:
                    errors.append(ValidationError(field, f"{field} is required"))
                    
            # Age validation
            if 'age' in data:
                try:
                    age = int(data['age'])
                    if age < 0 or age > 150:
                        errors.append(ValidationError('age', "Invalid age"))
                except ValueError:
                    errors.append(ValidationError('age', "Age must be a number"))
                    
            # Email validation
            if 'email' in data:
                if '@' not in data['email']:
                    errors.append(ValidationError('email', "Invalid email format"))
                    
            return errors

    # Test the validator
    validator = DataValidator()
    test_data = {
        "name": "Test User",
        "email": "invalid-email",
        "age": "not-a-number"
    }
    print(f"Validation errors: {validator.validate_user_data(test_data)}")
    """
    
    result6 = execute_python_code(
        code=validation_code,
        filename="data_validator.py",
        author="Sarah Brown",
        description="Data validation with automated code review",
        tags=["validation", "code-review"],
        enable_code_review=True
    )
    
    print("Code Review Comments:", result6["code_review"])
    print("Execution Output:", result6["output"])

if __name__ == "__main__":
    run_examples()
