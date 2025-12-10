from setuptools import setup, find_packages

setup(
    name="life-os",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "pydantic",
        "typer[all]",
        "rich",
        "python-dotenv",
        "watchdog",
        "apscheduler"
    ],
    entry_points={
        "console_scripts": [
            "life=life_system.interfaces.cli:app",
        ],
    },
)
