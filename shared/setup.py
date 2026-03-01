from setuptools import setup, find_packages

setup(
    name="docmanager-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic[email]",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
    ],
)
