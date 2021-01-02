# -*- coding: utf-8 -*-

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
    author_email="7199136+staticintlucas@users.noreply.github.com",
    description="Generate keyset layout and font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/staticintlucas/pykeyset",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        # TODO no PyPy support because recordclass fails to compile
        # 'Programming Language :: Python :: Implementation :: PyPy',
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "keyset=keyset.__main__:_start",
        ],
    },
    package_data={
        "": [
            "res/fonts/*.xml",
            "res/icons/*.xml",
            "res/profiles/*.toml",
        ],
    },
    install_requires=[
        "colorama~=0.4.3",
        "ansiwrap~=0.8.2",
        "toml~=0.10.1",
        "recordclass~=0.14.0",
        "importlib_resources~=4.0.0; python_version<'3.7'",
    ],
    cmdclass=versioneer.get_cmdclass(),
)
