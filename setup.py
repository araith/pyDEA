import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name = "pyDEA",
    version = "0.33",
    author = "Andrea Raith, Olga Perederieieva",
    author_email = "peredereeva@gmail.com",
    description = ("Package for conducting data envelopment analysis"),
    license = "MIT",
    keywords = "data envelopment analysis",
    url = "http://packages.python.org/pydea",
    packages=['pyDEA', 'pyDEA.core', 'pyDEA.core.data_processing',
    'pyDEA.core.gui_modules', 'pyDEA.core.models', 'pyDEA.core.utils'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux"
    ],
    install_requires=['pulp>=1.6.1', 'xlrd', 'xlwt-future', 'openpyxl'],
    entry_points={
        'gui_scripts': [
            'pyDEA=pyDEA.main_gui:main',
        ],
    },
    include_package_data=True,
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
    test_suite='tests',
)