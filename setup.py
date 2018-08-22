# -*- encoding: utf-8 -*-

from setuptools import (
    setup,
    find_packages
)

with open('README.md') as f :
    readme = f.read()

with open('LICENSE') as f :
    license = f.read()

setup(
    name='pk.services',
    version='0.1.0',
    description='Various services for python',
    long_description=readme,
    author='Tulare Regnus',
    author_email='tulare.paxgalactica@gmail.com',
    url='https://github.com/tulare/pk.services',
    license=license,
    packages=find_packages(exclude=('tests',))
)
