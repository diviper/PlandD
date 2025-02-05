from setuptools import setup, find_packages

setup(
    name="pland",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'aiogram>=3.3.0',
        'python-dotenv>=1.0.0',
        'openai>=1.0.0',
        'sqlalchemy>=2.0.37',
        'alembic>=1.14.0',
        'apscheduler>=3.10.0',
        'tenacity>=8.2.0',
    ],
)
