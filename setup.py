'''Setup script for pypi publication'''
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='ccextender',
    version='1.28',
    scripts=['ccextender'],
    author="aslape",
    author_email="aslape@atlassian.com",
    description="Cookiecutter Extended",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/asecurityteam/ccextender",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
