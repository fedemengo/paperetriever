from setuptools import setup, find_packages

setup(
    name="paperetriever",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "paperetriever=paperetriever.cli:cli",
        ],
    },
)
