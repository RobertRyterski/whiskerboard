#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-whiskerboard',
    version='0.0.7',
    description='A status board for Django.',
    author='Robert Ryterski',
    author_email='robert@ryterski.net',
    url='http://github.com/RobertRyterski/whiskerboard/',
    long_description=open('README.md', 'r').read(),
    packages=find_packages(exclude=('tests', 'example')),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.4',
        'mongoengine>=0.5.2'
    ],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
