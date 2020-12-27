# coding: utf-8

from setuptools import setup, find_packages
from os import path

import versioneer

thisdir = path.abspath(path.dirname(__file__))
with open(path.join(thisdir, "README.md")) as f:
    long_description = f.read()

setup(
    name="pykeyset",
    version=versioneer.get_version(),
    author="Lucas Jansen",
    description="Generate keyset layout and font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/staticintlucas/pykeyset",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'keyset=keyset.__main__:_start',
        ],
    },
    package_data={
        '': [
            'res/fonts/*.xml',
            'res/profiles/*.toml',
        ],
    },
    install_requires=[
        'colorama',
        'ansiwrap',
        'toml',
        'recordclass',
        'importlib_resources; python_version<"3.7"',
    ],
    cmdclass=versioneer.get_cmdclass(),
)
