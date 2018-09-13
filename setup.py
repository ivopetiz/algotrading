# coding=utf-8
import os
from setuptools import setup, find_packages

# RELEASE STEPS
# $ python setup.py bdist_wheel
# $ python twine upload dist/VX.Y.Z.whl
# $ git tag -a VX.Y.Z -m "release version VX.Y.Z"
# $ git push origin VX.Y.Z


__title__ = "cryptoalgotrading"
__description__ = "Algotrading framework for crypto currencies"
__url__ = "https://github.com/ivopetiz/crypto-algotrading"
__author_email__ = "ivopetiz@gmail.com"
__license__ = "MIT"

__requires__ = [
#    "backports.functools-lru-cache==1.5",
#    "backports.shutil-get-terminal-size==1.0.0",
#    "certifi==2018.4.16",
#    "chardet==3.0.4",
#    "cycler==0.10.0",
#    "decorator==4.3.0",
#    "enum34==1.1.6",
#    "idna==2.7",
#    "influxdb==5.2.0",
#    "ipython==5.7.0",
#    "ipython-genutils==0.2.0",
#    "kiwisolver==1.0.1",
#    "matplotlib==2.2.0",
#    "numpy==1.15.0",
#    "pandas==0.23.4",
#    "pathlib2==2.3.2",
#    "pexpect==4.6.0",
#    "pickleshare==0.7.4",
#    "prompt-toolkit==1.0.15",
#    "ptyprocess==0.6.0",
#    "Pygments==2.2.0",
#    "pyparsing==2.2.0",
#    "python-dateutil==2.7.3",
#    "pytz==2018.5",
#    "requests==2.19.1",
#    "scandir==1.8",
#    "simplegeneric==0.8.1",
#    "six==1.11.0",
#    "subprocess32==3.2.7",
#    "traitlets==4.3.2",
#    "urllib3==1.23",
#    "wcwidth==0.1.7"
]

__keywords__ = ["algotrading", "trading", "cryptocurrencies", "finance"]
# Load the package's _version.py module as a dictionary.
about = {}
with open("_version.py") as f:
    exec(f.read(), about)


setup(
    name=__title__,
    version=about["__version__"],
    description=__description__,
    url=__url__,
    author=about["__author__"],
    author_email=__author_email__,
    license=__license__,
    packages=find_packages(),
    keywords=__keywords__,
    #install_requires=__requires__,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
    ],
)
