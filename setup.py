import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="JonasNiemeyer",
    version="0.0.1",
    author="Jonas Niemeyer",
    author_email="jonasniemeyer@gmx.net",
    description="Tools for scraping and retrieving financial and economic data from various sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=None,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)