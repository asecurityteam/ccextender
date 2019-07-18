'''Setup script for pypi publication'''
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='ccextender',
    version='1.14',
    scripts=['ccextender'],
    author="aslape",
    author_email="aslape@atlassian.com",
    description="Cookiecutter Extended",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/aslape/ccextender",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
