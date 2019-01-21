# pyreadstat

A python package to read sas (sas7bdat, sas7bcat, xport), spps (sav, zsav, por) and stata (dta) data files into 
pandas dataframes.
<br> 

This module is a wrapper around the excellent [Readstat](https://github.com/WizardMac/ReadStat) C library by 
[Evan Miller](https://www.evanmiller.org/). Readstat is the library used in the back of the R library 
[Haven](https://github.com/tidyverse/haven), 
meaning pyreadstat is a python equivalent to R Haven (but writing files is currently not supported.)

Detailed documentation on all available methods is in the 
[Module documentation](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html)

If you would like to read R RData and Rds files into python in an easy way,
take a look to [pyreadr](https://github.com/ofajardo/pyreadr), a wrapper
around the C library [librdata](https://github.com/WizardMac/librdata)


**DISCLAIMER** 

**Pyreadstat is not a validated package. The results may have inaccuracies deriving from the fact most of the data formats
are not open. Do not use it for critical tasks such as reporting to the authorities. Pyreadstat is not meant to replace
the original applications in this regard and for that reason writing is not supported.**  

## Table of Contents

* [Motivation](#motivation)
* [Dependencies](#dependencies)
* [Installation](#installation)
  + [Using pip](#using-pip)
  + [From the latest sources](#from-the-latest-sources)
  + [Compiling on Windows and Mac](#compiling-on-windows-and-mac)
* [Usage](#usage)
  + [Basic Usage](#basic-usage)
  + [Reading only the headers](#reading-only-the-headers)
  + [Reading selected columns](#reading-selected-columns)
  + [Reading value labels](#reading-value-labels)
  + [Missing Values](#missing-values)
    - [SPSS](#spss)
    - [SAS and STATA](#sas-and-stata)
+ [Other options](#other-options)
* [Roadmap](#roadmap)
* [Known limitations](#known-limitations)
* [Python 2.7 support.](#python-27-support)
* [Change log](#change-log)
* [License](#license)
* [Contributing](#contributing)
* [People](#people)


## Motivation

The original motivation came from reading sas7bdat files in python. That is already possible using either the (pure
python) package [sas7bdat](https://pypi.org/project/sas7bdat/) or the (cythonized) method 
[read_sas](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_sas.html)
from pandas. However, those methods are slow (important if you want to read several large files), do not give the 
possibility to recover value labels (stored in 
the file itself in the case of spss or stata, or in catalog files in sas), convert both dates and datetime variables to datetime,
and you have to specify the encoding otherwise in python 3 instead of strings you get bytes. 

This package corrects those problems. 

**1. Good Performance:** Here a comparison of reading a 190 Mb sas7dat file with different methods. As you can see
pyreadstat is the fastest for python and matches the speeds of R Haven.

| Method | time  | 
| :----- | :-----------------: | 
| Python 3 - sas7bdat | 6 min | 
| Python 3- pandas | 42 s | 
| Python 3- pyreadstat | 7 s  | 
| R - Haven | 7 s | 

**2. Reading Value Labels** Neither sas7bdat and pandas.read_sas gives the possibility to read sas7bcat catalog files.
Pyreadstat can do that and also extract value labels from SPSS and STATA files. 

**3. Reading dates and datetimes** sas7bdat and pandas.read_sas convert both date and datetime variables into datetime.
That means if you have a date such a '01-01-2018' it will be transformed to '01-01-2018 00:00:00' (it always inserts a 
time), making it impossible
to know looking only at the data if the variable was originally a datetime (if it had a time) or not. 
Pyreadstat transforms dates to dates and datetimes to datetimes, so that you have a better correspondence with the original
data. However, it is possible to keep the original pandas behavior and get always datetimes.

**4. Encoding** On python 3, pandas.read_sas reads all strings as bytes. If you want strings you have to specify the encoding manually.
pyreadstat read strings as str. Thas is possible because readstat extracts the original encoding and translates 
to utf-8, so that you don't have to care about that anymore. However it is still possible to manually set the encoding.

In addition pyreadstat exposes the variable labels in an easy way (see later). As pandas dataframes cannot handle value
labels, you as user will have to take the decision whether to use those values or not. Pandas read_sas reads those labels, 
but in order to recover them you have to work a bit harder. 

Compared to R Haven, pyreadstat offers the possibility to read only the headers: Sometimes you want to take a 
look to many (sas) files looking for the datasets that contain
some specific columns, and you want to do it quick. This package offers the possibility to read only the metadata making 
it possible a very fast metadata scraping (Pandas read_sas can also do it if you pass the value iterator=True). 
In addition it offers the capability to read sas7bcat files separately from the sas7bdat files.


## Dependencies

The module depends on pandas, which you normally have installed if you got Anaconda (highly recommended.) If creating
a new conda or virtual environment or if you don't have it in your base installation, you will have to install it 
manually before using pyreadstat. Pandas is not selected as a dependency in the pip package, as that would install 
pandas with pip and many people would prefer installing it with conda.

In order to compile from source you will need a C compiler (see installation). 
Only if you want to do changes to the cython source code, you will need cython (normally not necessary).
If you want to compile for python 2.7, you will need cython (see python 2.7 support
later).

Readstat depends on the C library iconv to handle character encodings. On mac, the library is found on the system, but
users have sometimes reported problems. In those cases it may help to install libiconv with conda (see later, compilation
on mac)

Readstat also depends on zlib; it was reported not to be installed on Lubuntu. If you face this problem intalling the 
library solves it.


## Installation

### Using pip

Probably the easiest way: from your conda, virtualenv or just base installation do:

```
pip install pyreadstat
```

If you are running on a machine without admin rights, and you want to install against your base installation you can do:

```
pip install pyreadstat --user
```

Notice that at the moment we offer pre-compiled wheels for windows, mac and 
linux for Python 2.7, 3.5, 3.6 and 3.7. Python 2.7 does not work for
widows (see later python 2.7 support). If there is no pre-compiled 
wheel available, pip will attempt to compile the package. 

### From the latest sources

Download or clone the repo, open a command window and type:

```
python3 setup.py install
```

If you don't have admin privileges to the machine (for example on Bee) do:

```
python3 setup.py install --user
```

You can also install from the github repo directly (without cloning). Use the flag --user if necessary.

```
pip install git+https://github.com/Roche/pyreadstat.git
```

You need a working C compiler. If working in python 2.7 you will need
cython version >= 0.28 installed (see later Python 2.7 support). For python 3, cython
is not necessary, but if installed it will be used.

### Compiling on Windows and Mac

Compiling on linux is very easy, but on windows is a bit more challenging. 
Some instructions are found [here](https://github.com/Roche/pyreadstat/blob/master/windows_compilation.md)

Compiling on mac is usually easy. Readstat depends however on the C library iconv to handle character encodings; while 
on linux is part of gclib, on mac it is a separated shared library found on the system (h file is in /usr/include and shared
library on /usr/lib). While compiling against this usually works fine, some users have reported problems (for example
missing symbol _iconv, or libiconv version too old). In those cases it helped to install libiconv with conda:

```
conda install libiconv
```

and then recompile again (be sure to delete any cache, if using pip do pip --no-cache-dir, if using setup.py remove
the folder build, otherwise you may be installing the old compilation again).

## Usage

### Basic Usage

Pass the path to a file to any of the functions provided by pyreadstat. It will return a pandas data frame and a metadata
object. <br>
The dataframe uses the column names. The metadata object contains the column names, column labels, number_rows, 
number_columns, file label
(if any), file encoding (if applicable), notes and objects about value labels (if present). Be aware that file_label and
file_encoding may be None, not all columns may have labels, notes may not be present and there may be no value labels.

For example, in order to read a sas7bdat file:

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat')

# done! let's see what we got
print(df.head())
print(meta.colum_names)
print(meta.column_labels)
print(meta.number_rows)
print(meta.number_columns)
print(meta.file_label)
print(meta.file_encoding)
# there are other metadata pieces extracted. See the documentation for more details.
```

You can replace the column names by column labels very easily (but check first that all columns have distinct labels!):

```python
# replace column names with column labels
df.columns = meta.column_labels
# to go back to column names
df.columns = meta.column_names
```

Here there is a relation of all functions available. 
You can also check the [Module documentation](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html).

| Function in this package | Purpose |
| ------------------- | ----------- |
| read_sas7dat        | read SAS sas7bdat files |
| read_xport          | read SAS Xport (XPT) files |
| read_sas7bcat       | read SAS catalog files |
| read_dta            | read STATA dta files |
| read_sav            | read SPSS sav and zsav files  |
| read_por            | read SPSS por files  |
| set_catalog_to_sas  | enrich sas dataframe with catalog formats |
| set_value_labels    | replace values by their labels |


### Reading only the headers

All functions accept a keyword argument "metadataonly" which by default is False. If True, then no data will be read, 
but still both the metadata and the dataframe will be returned. The metadata will contain all fields as usual, but
the dataframe will be emtpy, although with the correct columns names. Sometimes number_rows may be None if it was not
possible to determine the number of rows without reading the data.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', metadataonly=True)
```

### Reading selected columns

All functions accept a keyword "usecols" which should be a list of column names. Only the columns which names match those
in the list will be imported (case sensitive). This decreases memory consumption and speeds up the process. Usecols must
always be a list, even if there is only one member.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', usecols=["variable1", "variable2"])

```

### Reading value labels

For sas7bdat files, value labels are stored in separated sas7bcat files. You can use them in combination with the sas7bdat
or read them separately.

If you want to read them in combination with the sas7bdat files, pass the path to the sas7bcat files to the read_sas7bdat
function. The original values will be replaced by the values in the catalog.

```python
import pyreadstat

# formats_as_category is by default True, and it means the replaced values will be transformed to a pandas category column.
df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', catalog_file='/path/to/a/file.sas7bcat', formats_as_category=True)
```

If you prefer to read the sas7bcat file separately, you can apply the formats later with the function set_catalog_to_sas.
In this way you can have two copies of the dataframe, one with catalog and one without.

```python
import pyreadstat

# this df will have the original values
df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat')
# read_sas7bdat returns an emtpy data frame and the catalog
df_empty, catalog = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bcat')
# enrich the dataframe with the catalog
# formats_as_category is by default True, and it means the replaced values will be transformed to a pandas category column.
df_enriched, meta_enriched = pyreadstat.set_catalog_to_sas(df, meta, catalog, formats_as_category=True)
```

For SPSS and STATA files, the value labels are included in the files. You can choose to replace the values by the labels
when reading the file using the option apply_value_formats, ...

```python
import pyreadstat

# apply_value_formats is by default False, so you have to set it to True manually if you want the labels
# formats_as_category is by default True, and it means the replaced values will be transformed to a pandas category column.
df, meta = pyreadstat.read_sav("/path/to/sav/file.sav", apply_value_formats=True, formats_as_category=True)
```

... or to do it later with the function set_value_labels:

```python
import pyreadstat

# This time no value labels.
df, meta = pyreadstat.read_sav("/path/to/sav/file.sav", apply_value_formats=False)
# now let's add them to a second copy
df_enriched = pyreadstat.set_value_labels(df, meta, formats_as_category=True)
```

### Missing Values

There are two types of missing values: system and user defined. System are assigned by the program by default. User defined are 
valid values that the user decided to give the meaning of missing in order to differentiate between several situations.For
example if one has a categorical variable representing if the person passed a test, you could have 0 for did not pass, 
1 for pass, and as user defined missing variables 2 for did not show up for the test, 3 for unable to process the results, 
etc.

**By default both cases are represented by NaN when
read with pyreadstat**. Notice that the only possible missing value in pandas is NaN (Not a Number) for both string and numeric
variables, date, datetime and time variables have NaT (Not a Time).

#### SPSS 

In the case of SPSS sav files, the user can assign to a numeric variable either up to three discrete missing values or
one range plus one discrete missing value. As mentioned by default all of these possiblities are translated into NaN, 
but one can get those original values by passing the argument user_missing=True to the read_sav function:

```python
# user set with default missing values
import pypreadstat
df, meta = pyreadstat.read_sav("/path/to/file.sav")
print(df)
>> test_passed
   1
   0
   NaN
   NaN
```

Now, reading the user defined missing values:

```python
# user set with user defined missing values
import pypreadstat
df, meta = pyreadstat.read_sav("/path/to/file.sav", user_missing=True)
print(df)
>> test_passed
   1
   0
   2
   3
```

As you see now instead o NaN the values 2 and 3 appear. In case the dataset had value labels, we could bring those in
```python
# user set with user defined missing values and labels
import pypreadstat
df, meta = pyreadstat.read_sav("/path/to/file.sav", user_missing=True, apply_value_formats=True)
print(df)
>> test_passed
   "passed"
   "not passed"
   "not shown"
   "not processed"
```

Finally, the information about what values are user missing is stored in the meta object, in the variable missing_ranges.
This is a dicitonary with the key being the name of the variable, and as value a list of dictionaries, each dictionary
contains the elements "hi" and "lo" to represent the lower and upper bound of the range, however for discrete values
as in the example, both boundaries are also present although the value is the same in both cases.

```python
# user set with default missing values
import pypreadstat
df, meta = pyreadstat.read_sav("/path/to/file.sav", user_missing=True, apply_value_formats=True)
print(meta.missing_ranges)
>>> {'test_passed':[{'hi':2, 'lo':2}, {'hi':3, 'lo':3}]}
```

For SPSS sav files user defined missing values for non numeric (character) variables is not supported. In addition, if the value in
a character variable is an empty string (''), it will not be translated to NaN, but will stay as an empty string. This
is because the empty string is a valid character value in SPSS and pyreadstat preserves that property. You can convert
empty strings to nan very easily with pandas. 

For SPSS por files, 

#### SAS and STATA

In SAS the user can assign values from .A to .Z and ._ as user defined missing values. In Stata values from
.a to .z. As in SPSS, those are normally translated to
NaN. However, using user_missing=True with read_sas7bdat or read_dta
will produce values from A to Z and _ for SAS and a to z for dta. In addition a variable
missing_user_values will appear in the metadata object, being a list with those values that are user defined missing
values.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat("/path/to/file.sas7bdat", user_missing=True)

df, meta = pyreadstat.read_dta("/path/to/file.dta", user_missing=True)
```
 
The user may also assign a label to user defined missing values. In such 
case passing the corresponding sas7bcat file to read_sas7bdat or using 
the option apply_value_formats to read_dta will show those labels instead
of the user defined missing value. 

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat("/path/to/file.sas7bdat", catalog_file="/path/to/file.sas7bcat", user_missing=True)

df, meta = pyreadstat.read_dta("/path/to/file.dta", user_missing=True, apply_value_formats=True)

```

Empty strings are still transtaled as empty strings and not as NaN.

User defined missing values are currently not supported for file types other than sas7bdat,
sas7bcat and dta.


### Other options

You can set the encoding of the original file manually. The encoding must be a [iconv-compatible encoding](https://gist.github.com/hakre/4188459) 

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', encoding="LATIN1")
```

You can preserve the original pandas behavior regarding dates (meaning dates are converted to pandas datetime) with the
dates_as_pandas_datetime option

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', dates_as_pandas_datetime=True)
```

For more information, please check the [Module documentation](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html).


## Roadmap



## Known limitations

pyreadstat builds on top of Readstat and therefore inherits its limitations. Currently those include:

* Not able to read SAS compressed files. 
* Not able to skip rows.
* Not handling SPSS user defined missing values for character variables (numeric are fine).
* Dates, datetimes and times in SPSS POR files are not translated to python dates, datetimes and times, but stay as 
  timestamps.
  

## Python 2.7 support.

Python 2.7 is not actively supported. If it works, we are happy about that. But if it does not, and the
bug is specific for python 2.7 (cannot be reproduced in python 3), the issue is not going to be solved.

At the moment of writing this document Python 2.7 does not work for windows.
It does work for Mac and Linux. In Mac and Linux, files cannot be opened
if the path contains international (non-ascii) characters. As mentioned
before this bug is not going to be repaired (There is not such issue on
Python 3).


## Change log

A log with the changes for each version can be found [here](https://github.com/Roche/pyreadstat/blob/master/change_log.md)


## License

pyreadstat is distributed under Apache 2.0 license. Readstat is distributed under MIT license. See the License file for
more information.


## Contributing

Contributions are welcome! Those include corrections to the documentation, bugs reporting, testing, 
and of course code pull requests. For code pull requests please 
consider opening an issue explaining what you plan to do, so that we can get aligned before you start investing time on
it (this also avoids duplicated efforts).

The ReadStat code in this repo (under the subfolder src) is coming from the main Readstat trunk and should not be 
modified in order to
keep full compatibility with the original. In that way improvements in ReadStat can be taken here with almost
no effort. If you would like to propose new features involving changes in the ReadStat code, please submit a
pull request to ReadStat first. 

## People

Otto Fajardo - author, maintainer

[Matthew Brett](http://matthew.dynevor.org/) - contributor [python wheels](https://github.com/MacPython/pyreadstat-wheels)

[Jonathon Love](https://jona.thon.love/) - contributor

