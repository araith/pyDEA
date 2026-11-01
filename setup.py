import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pyDEA",
    version="1.6",
    author="Andrea Raith, Olga Perederieieva",
    author_email="peredereeva@gmail.com",
    description=("Package for conducting data envelopment analysis"),
    license="MIT",
    keywords="data envelopment analysis",
    url="https://github.com/araith/pyDEA",
    packages=['pyDEA', 'pyDEA.core', 'pyDEA.core.data_processing',
              'pyDEA.core.gui_modules', 'pyDEA.core.models',
              'pyDEA.core.utils'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.12',
    install_requires=['pulp[cbc]>=4.2,<5', 'openpyxl>=3.1.5,<4'],
    extras_require={'test': ['pytest>=8,<10']},
    entry_points={
        'gui_scripts': [
            'pyDEA=pyDEA.main_gui:main',
        ],
    },
    include_package_data=True,
)
