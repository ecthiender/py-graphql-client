# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


__version__ = "0.1.1-beta.2"
__desc__ = "A dead-simple GraphQL client that supports subscriptions over websockets"

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'websocket-client==0.54.0'
]

test_requirements = []

setup(
    name='py-graphql-client',
    version=__version__,
    description=__desc__,
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Anon Ray",
    author_email='rayanon004@gmail.com',
    url='https://github.com/ecthiender/py-graphql-client',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'': ['LICENSE']},
    package_dir={'graphql_client': 'graphql_client'},
    python_requires=">=3.4",
    include_package_data=True,
    install_requires=requirements,
    license="BSD3",
    zip_safe=False,
    keywords=['graphql', 'websocket', 'subscriptions', 'graphql-client'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Other Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
