# -*- coding: utf-8 -*-
import glob
import os
from setuptools import find_packages, setup

DISTNAME = "kkplot"
VERSION = "0.2.1"
LICENSE = "MIT"
AUTHOR = "Steffen Klatt, David Kraus"
AUTHOR_EMAIL = "david.kraus@gmx.de"
URL = "https://github.com/deekaey/kkplot"
DESCRIPTION = "A scientific plotting tool for environmental data."
PYTHON_REQUIRES = ">=3.7"

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Scientific/Engineering",
]

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

INSTALL_REQUIRES = [
    "bokeh",
    "holoviews",
    "pylatexenc",
    "matplotlib",
    "numexpr>=2.7.0",
    "numpy",
    "pandas",
    "pillow",
    "pyyaml",
    "scipy",
    "python-dotenv",
]

setup(
    name=DISTNAME,
    version=VERSION,
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
    packages=find_packages("src", exclude=["docs", "tests", "tests.*"]),
    package_dir={"": "src"},
    py_modules=[
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join("src", "*.py"))
    ],
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "kkplot=kkplot.kkplot:main",
        ],
    },
    project_urls={
        "Source": URL,
        "Tracker": f"{URL}/issues",
    },
)
