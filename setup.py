import os
import re
from setuptools import setup, find_packages


requires = [
    "datacoco-core==0.1.1",
    "datacoco-batch==0.1.0",
    "datacoco-secretsmanager==0.1.3",
    "pyyaml==3.13",
    "boto==2.49.0",
    "schedule==0.5.0",
    "redis==3.0.1",
    "pytz==2018.7",
]


def get_version():
    version_file = open(os.path.join("robopager", "__version__.py"))
    version_contents = version_file.read()
    return re.search('__version__ = "(.*?)"', version_contents).group(1)


setup(
    name="robopager",
    packages=find_packages(exclude=["tests*"]),
    version=get_version(),
    license="MIT",
    description="Job monitor and alerting app by Equinox",
    long_description=open("README.rst").read(),
    author="Equinox Fitness",
    url="https://github.com/equinoxfitness/robopager",
    keywords=["job monitor", "daily email check", "intraday latency check"],
    install_requires=requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
)
