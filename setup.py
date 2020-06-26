from setuptools import setup, find_packages

setup(
    name="CredRegParser",
    version="0.1.0",
    author="Phil Barker",
    url="https://github.com/philbarker/CredRegParser",
    description="Fetch and parse resource metadata from the Credential Registry.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "setuptools >= 47.3.0",
        "rdflib >= 5.0.0",
        "rdflib-jsonld>=0.5.0",
        "cache-requests >= 4.0.0"],
    python_requires=">=3.8",
    packages=find_packages()
)
