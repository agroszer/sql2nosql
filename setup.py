"""Setup
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'sql2nosql',
    version = '0.1.0dev',
    author = "Adam",
    author_email = "agroszer@gmail.com",
    description = "sql2nosql",
    long_description='WIP',
    license = "ZPL 2.1",
    keywords = "",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.testing',
                'zope.testbrowser',
                'z3c.coverage',
                'coverage',
                'refline.srccheck',
                ],
    ),
    install_requires = [
        'setuptools',
        'decorator',
        'odict',
        'rwproperty',
        'python-dateutil',

        'ply',
        'pyparsing',

        'pymongo',
        'komodo-python-dbgp',
    ],
    include_package_data = True,
    zip_safe = False,
    entry_points = '''
    '''
    )
