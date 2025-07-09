from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lob-simulation",
    version="1.0.0",
    author="Limit Order Book Simulation Team",
    author_email="contact@lob-simulation.com",
    description="A comprehensive market microstructure modeling framework for limit order book simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/lob-simulation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "viz": [
            "plotly>=5.0.0",
            "dash>=2.0.0",
            "flask>=2.0.0",
            "flask-socketio>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lob-sim=lob_simulation.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "lob_simulation": ["data/*", "static/*", "templates/*"],
    },
) 