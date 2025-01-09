from setuptools import setup, find_packages

# Specify install_requires for runtime dependencies
install_requires = [
    "ollama>=0.1.27",
    "pydantic>=2.0.0",
    "pytest>=7.0.0",
    "bandit>=1.7.5",
    "safety>=2.3.0",
    "docker>=6.1.0",
    "PyYAML>=6.0.1",
    "requests>=2.31.0",
    "PyGithub>=2.1.1",
    "python-gitlab>=3.15.0",
    "python-jenkins>=1.8.0",
    "semgrep>=1.38.0",
    "mypy>=1.7.0",
    "coverage>=7.3.2",
    "docstring-parser>=0.15",
    "psutil>=5.9.0",
    "black>=23.11.0",
    "pylint>=3.0.2",
    "radon>=6.0.1"
]

# Specify setup_requires for build-time dependencies
setup_requires = [
    "ollama>=0.1.27"
]

setup(
    name="ollama_tools",
    version="0.1.0",
    packages=find_packages(include=['ollama_tools', 'ollama_tools.*', 'lib', 'lib.*']),
    install_requires=install_requires,
    setup_requires=setup_requires,
    python_requires='>=3.8',
)
