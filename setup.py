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
    "License :: OSI Approved :: MIT",
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

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

# get the dependencies and installs
with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

INSTALL_REQUIRES = [x.strip() for x in all_reqs if "git+" not in x]
DEPENDENCY_LINKS = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

setup(
    name=DISTNAME,
    version=VERSION,
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",  # 🆕 ensures PyPI renders README.md
    classifiers=CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
    packages=find_packages("src", exclude=["docs", "tests", "tests.*"]),
    package_dir={"": "src"},
    py_modules=[
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join("src", "*.py"))
    ],
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    include_package_data=True,  # ensures MANIFEST.in is respected
    zip_safe=False,             # safer for packages that load data files at runtime
    entry_points={
        "console_scripts": [
            "kkplot=kkplot.kkplot:main",
        ],
    },
    project_urls={  # 🆕 Optional, improves PyPI page
        "Source": URL,
        "Tracker": f"{URL}/issues",
    },
)
