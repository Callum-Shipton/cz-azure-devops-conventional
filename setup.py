from setuptools import setup

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cz-azure-devops-conventional",
    version="0.1.0",
    py_modules=["cz_azure_devops_conventional"],
    author="Callum Shipton",
    license="MIT",
    url="https://github.com/Callum-Shipton/cz-azure-devops-conventional",
    install_requires=["commitizen>=3.21.3"],
    description="Extend the commitizen tools to create conventional commits and CHANGELOG that link to Azure Devops.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "commitizen.plugin": [
            "cz_azure_devops_conventional = cz_azure_devops_conventional:AzureDevopsConventionalCz"
        ]
    },
)