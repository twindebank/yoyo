
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='yoyo',
    version='0.0.1',
    description='Python microservices made easy.',
    python_requires='==3.*,>=3.9.0',
    project_urls={"documentation": "", "homepage": "", "repository": ""},
    author='Theo Windebank',
    author_email='theo@theowindebank.co.uk',
    license='MIT',
    entry_points={"console_scripts": ["yy = yoyo.cli:main", "yoyo = yoyo.cli:main"]},
    packages=[],
    package_dir={"": "."},
    package_data={},
    install_requires=['dephell==0.*,>=0.8.3', 'fire==0.*,>=0.3.1', 'gitpython==3.*,>=3.1.11', 'loguru==0.*,>=0.5.3', 'networkx==2.*,>=2.5.0', 'ruamel.yaml==0.*,>=0.16.0'],
    extras_require={"dev": ["pytest==6.*,>=6.1.0"]},
)
