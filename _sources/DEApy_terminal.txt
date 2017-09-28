Running *pyDEA* from Terminal
===============================

How to run *pyDEA* from terminal depends on whether you have Python 3
and all necessary packages installed, see [sec:packages]. If all
packages are installed, the following should work: Go to main folder
containing your *pyDEA* files and run the following:

::

    python3 source\refactored\main.py param_file output_file_format 
      output_dir sheet_name

Alternatively, ensure to use the Python 3 executable in the SupportFiles
folder:

::

    SupportFiles\python\windows\Python33\python.exe source\refactored\main.py 
      param_file output_file_format output_dir sheet_name

where

#. ``param_file`` is path to file with parameters (an example of
   parameter files can be found in ``Data/Params/``, but you can also
   generate your own by saving it from the *pyDEA* gui.)

#. ``output_file_format`` possible values: xls, xlsx and csv. The
   default value is xls (optional, this value is used only if auto was
   set for OUTPUT\_FILE in parameters file)

#. ``output_dir`` is output directory (optional, if not specified,
   output is written to current directory)

#. ``sheet_name`` is sheet name from which data should be read
   (optional, if not specified, data is read from the first sheet)

Note: if you want to specify the sheet name, but not the output
directory use an empty string as the third argument, for example:

::

    python3 source/refactored/main.py param_file "" "" sheet_name

Note:

-  If the file path contains spaces use quotes

-  | Note operating-system specific standards for file locations, etc.
   | Eg ``source\refactored\main.py`` in windows but
     ``source/refactored/main.py`` in linux.

Sample parameter file
---------------------

File ``DEA_example_data_params.txt``:

::

    <ABS_WEIGHT_RESTRICTIONS> {}
    <DATA_FILE> {Data\DEA_example_data.xls}
    <USE_SUPER_EFFICIENCY> {}
    <OUTPUT_CATEGORIES> {O1;O2}
    <NON_DISCRETIONARY_CATEGORIES> {ND1}
    <OUTPUT_FILE> {auto}
    <CATEGORICAL_CATEGORY> {}
    <VIRTUAL_WEIGHT_RESTRICTIONS> {}
    <PRICE_RATIO_RESTRICTIONS> {}
    <WEAKLY_DISPOSAL_CATEGORIES> {}
    <MULTIPLIER_MODEL_TOLERANCE> {0}
    <MAXIMIZE_SLACKS> {}
    <INPUT_CATEGORIES> {ND1;I2;I1}
    <PEEL_THE_ONION> {}
    <RETURN_TO_SCALE> {both}
    <DEA_FORM> {env}
    <ORIENTATION> {input}

packages to be installed
------------------------

Required packages for *pyDEA*

-  python 3

-  pulp package

-  xlrd package: python3-xlrd

-  xlwt package: xlwt-future

-  tkinter package: python3-tk

There are other packages for unit tests and documentation, but they are
not required packages for running *pyDEA*. See also document
PackageInstallation.docx, which has exact linux install commands.
