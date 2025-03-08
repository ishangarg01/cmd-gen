# setup.py - Updated version
from setuptools import setup, find_packages

# Don't import from cmd_gen to avoid the import error
__version__ = "1.0.0"

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "Command Generator - Generate CLI commands from natural language"

setup(
    name="cmd-gen",
    version=__version__,
    author="Your Name",
    author_email="your.email@example.com",
    description="Generate CLI commands from natural language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cmd-gen",
    packages=["cmd_gen"],  # Explicitly specify package instead of find_packages()
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "google-genai",
        "python-dotenv",
        "colorama",
        "pyperclip",
    ],
    entry_points={
        "console_scripts": [
            "cmd-gen=cmd_gen.cli:main",
        ],
    },
)