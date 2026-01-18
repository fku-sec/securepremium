from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="securepremium",
    version="0.1.0",
    author="Security Team",
    author_email="security@example.com",
    description="SecurePremium - Quantify device compromise risk as insurance premiums",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/securepremium",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
    install_requires=[
        "device-fingerprinting-pro>=2.2.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "requests>=2.28.0",
        "cryptography>=41.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)
