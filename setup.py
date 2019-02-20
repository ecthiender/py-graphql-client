# -*- coding: utf-8 -*-
import os
import re
from setuptools import find_packages, setup

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('graphql_client')

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'websocket-client==0.54.0'
]
test_requirements = []

setup(
    name='py-graphql-client',
    version=version,
    description="A dead-simple graphql client that supports subscriptions.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Anon Ray",
    author_email='rayanon004@gmail.com',
    url='https://github.com/ecthiender/py-graphql-client',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'': ['LICENSE']},
    package_dir={'graphql_client': 'graphql_client'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD3",
    zip_safe=False,
    keywords=['graphql', 'websocket'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD3 License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Environment :: Web Environment',
        'Environment :: Mobile Applications',
        'Topic :: Applications:: GraphQL',
        'Topic :: Applications:: Realtime',
        'Topic :: Applications:: Subscriptions',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
