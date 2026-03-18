from setuptools import setup, find_packages


setup(
    name="obdb",
    version="0.1.2",
    description="Generated OBDb commands for python-OBD",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "obd",
    ],
    python_requires=">=3.9",
)