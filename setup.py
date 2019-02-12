#!/usr/bin/env python

from setuptools import setup

setup(name='provdebug',
    version='0.3',
    description='Multilingual Provenance Debugger',
    url='http://github.com/jwons/MultilingualProvenanceDebugger', 
    author='Joseph Wonsil',
    author_email='jwonsil@carthage.edu',
    license='GPL 3.0',
    packages=['provdebug'],
    install_requires=[
        'pandas',
        'networkx',
        'numpy'      
    ],
    entry_points = {
     'console_scripts': [
         'pvdebug = provdebug.pvdebug:run'
     ],
    },
    zip_safe=False)