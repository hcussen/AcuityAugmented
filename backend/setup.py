from setuptools import setup, find_packages

setup(
    name="acuity-augmented",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pytest",
        "freezegun",
    ],
)
