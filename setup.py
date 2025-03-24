from setuptools import setup, find_packages

setup(
    name="pages",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.0",  # Ensure Django is installed
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)