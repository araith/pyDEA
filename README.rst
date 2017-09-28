~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *pyDEA* - READ ME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Developers: Andrea Raith, Olga Perederieieva, Fariza Fauzi
:License: MIT license
:Web-site: 
:Documentation: 
:Platforms: Windows, Linux
:Date: 

Copyright (c) 2017 Andrea Raith, Olga Perederieieva, Fariza Fauzi.

*pyDEA* is a software package developed in Python for conducting data envelopment analysis (DEA). 

==============================
Installing and Running Package
==============================

Installation
------------

The *pyDEA* package can be installed via pip, easy_install or from source. In order to install it via pip open terminal and use the following command:

*>> pip install pyDEA*

In order to install a specific version use the following command:

*>> pip install pyDEA==version_number*

In order to install *pyDEA* via easy_install use the following command:

*>> easy_install pyDEA*

Or for specific version:

*>> easy_install pyDEA==version_number*

In order to install from source, download and unzip source files, open terminal and navigate to *pyDEA* main folder and run the following command:

*>> python setup.py install --record files.txt*

This command will create distribution files in *pyDEA* folder and write paths to all other installed files to files.txt.

How to Run
----------

The *pyDEA* package supports several interfaces. It has a Graphical User Interface (GUI), Command Line Interface (CLI) and it can be imported and used directly in python scripts. After package installation, in order to run GUI, open terminal and type:

*>> pyDEA*

Or use command:

*>> python -m pyDEA.main_gui*

In order to run CLI, use the following command:

*>>  python -m pyDEA.main file_with_params output_file_format output_dir sheet_name*

where

  - *file_with_params* is path to file with parameters.
  
  - *output_file_format*, possible values: xls, xlsx and csv, default value is xlsx. This value is optional and is used only if OUTPUT_FILE in parameters file is empty or set to auto. Otherwise, the value in OUTPUT_FILE is used instead.

  - *output_dir* is output directory. It is optional, if it is not specified, solution will be written to current directory. This value is used only if OUTPUT_FILE in parameters file is empty or set to auto. Otherwise, the value in OUTPUT_FILE is used instead.

  - *sheet_name* is sheet name from which data should be read. It is optional, if it is not specified, data will be read from the first sheet.

If you want to specify sheet name, but not output directory use empty string as the third argument, as shown below:

*>> python -m pyDEA.main .file_with_params "" "" sheet_name*

If file path contains spaces use quotes.

The *pyDEA* package can be imported in a python script as any other package. However, in order to access its methods and classes you need explicitly import them, for example, *from pyDEA import main_gui*. Then you can execute GUI by calling *main_gui.main()*. 

Another example: 

*>> from pyDEA.core.utils import dea_utils*

*>> dea_utils.change_to_unique_name_if_needed("test")*

This example imports all methods and classes defined in *dea_utils*.

Uninstalling
------------

If *pyDEA* was installed via pip or easy_install, it can be uninstalled by using the following command:

*>> pip uninstall pyDEA*

If *pyDEA* was installed from source, it must be manually uninstalled. Simply remove all files listed in files.txt and all *pyDEA* package files.

========
 License
========

*pyDEA* is distributed under the MIT License
::https://opensource.org/licenses/MIT

Copyright (c) 2016 Andrea Raith, Olga Perederieieva, Fariza Fauzi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

================
Acknowledgements
================

*pyDEA* has been financially supported by the Department of Engineering Science at the University of Auckland and the Auckland Medical Research Foundation (AMRF).

The *pyDEA* solver was first developed during a summer project in 2009 / 2010 at the University of Auckland, Department of Engineering Science by Kane Harton. Development was continued by Harriet Priddey during her Part IV project at the Department of Engineering Science in 2010. The code was further modified and enhanced with a GUI by Andrea Raith in 2010 / 2011. Alan Lee, Matt Rouse and Andrea Raith continued work on the GUI and the underlying DEA solver continued between November 2011 and February 2012. From 2014, pyDEA was re-implemented by Olga Perederieieva with input from Fariza Fauzi.

Thank you to Paul Rouse for guidance on DEA and help with the revamped version of *pyDEA*. Also, thank you to Oliver Weide for help with python.