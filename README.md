# pyreadstat

A python package to read and write sas (sas7bdat, sas7bcat, xport), spps (sav, zsav, por) and stata (dta) data files
into/from pandas dataframes.
<br>

This module is a wrapper around the excellent [Readstat](https://github.com/WizardMac/ReadStat) C library by
[Evan Miller](https://www.evanmiller.org/). Readstat is the library used in the back of the R library
[Haven](https://github.com/tidyverse/haven),
meaning pyreadstat is a python equivalent to R Haven.

Detailed documentation on all available methods is in the
[Module documentation](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html)

If you would like to read R RData and Rds files into python in an easy way,
take a look to [pyreadr](https://github.com/ofajardo/pyreadr), a wrapper
around the C library [librdata](https://github.com/WizardMac/librdata)


**DISCLAIMER**

**Pyreadstat is not a validated package. The results may have inaccuracies deriving from the fact most of the data formats
are not open. Do not use it for critical tasks such as reporting to the authorities. Pyreadstat is not meant to replace
the original applications in this regard.**  

## Table of Contents

* [Motivation](#motivation)
* [Dependencies](#dependencies)
* [Installation](#installation)
  + [Using pip](#using-pip)
  + [Using conda](#using-conda)
  + [From the latest sources](#from-the-latest-sources)
  + [Compiling on Windows and Mac](#compiling-on-windows-and-mac)
* [Usage](#usage)
  + [Basic Usage](#basic-usage)
    - [Reading Files](#reading-files)
    - [Writing Files](#writing-files)
  + [More reading options](#more-reading-options)
    - [Reading only the headers](#reading-only-the-headers)
    - [Reading selected columns](#reading-selected-columns)
    - [Reading rows in chunks](#reading-rows-in-chunks)
    - [Reading value labels](#reading-value-labels)
    - [Missing Values](#missing-values)
      + [SPSS](#spss)
      + [SAS and STATA](#sas-and-stata)
    - [Other options](#other-options)
  + [More writing options](#more-writing-options)
    - [File specific options](#file-specific-options)
    - [Writing value labels](#writing-value-labels)
    - [Writing user defined missing values](writing-user-defined-missing-values)
    - [Variable type conversion](variable-type-conversion)
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

The module depends on pandas, which you normally have installed if you got Anaconda (highly recommended.)

In order to compile from source you will need a C compiler (see installation).
Only if you want to do changes to the cython source code, you will need cython (normally not necessary).
If you want to compile for python 2.7 or windows, you will need cython (see python 2.7 support
later).

Readstat depends on the C library iconv to handle character encodings. On mac, the library is found on the system, but
users have sometimes reported problems. In those cases it may help to install libiconv with conda (see later, compilation
on mac). Readstat also depends on zlib; it was reported not to be installed by default on Lubuntu. If you face this problem installing the
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
linux for Python 2.7, 3.5, 3.6, 3.7 and 3.8. Python 2.7 does not work for
windows (see later python 2.7 support). If there is no pre-compiled
wheel available, pip will attempt to compile the source code.

### Using conda

The package is also available in [conda-forge](https://anaconda.org/conda-forge/pyreadstat) for windows, mac and linux
64 bit, python 3.6, 3.7 and 3.8. only.

In order to install:

```
conda install -c conda-forge pyreadstat
```

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
is not necessary if compiling on unix, but if installed it will be used.

### Compiling on Windows and Mac

Compiling on linux is very easy, but on windows you need some extra preparation.
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

#### Reading files

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
print(meta.column_names)
print(meta.column_labels)
print(meta.column_names_to_labels)
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

#### Writing files

Pyreadstat can write STATA (dta), SPSS (sav and zsav, por currently nor supported) and SAS (Xport, sas7bdat and sas7bcat
currently not supported) files from pandas data frames.

write functions take as first argument a pandas data frame (other data structures are not supported), as a second argument
the path to the destination file. Optionally you can also pass a file label and a list with column labels.

```python
import pandas as pd
import pyreadstat

df = pd.DataFrame([[1,2.0,"a"],[3,4.0,"b"]], columns=["v1", "v2", "v3"])
column_labels = ["Variable 1", "Variable 2", "Variable 3"]
pyreadstat.write_sav(df, "path/to/destination.sav", file_label="test", column_labels=column_labels)
```

Some special arguments are available depending on the function. write_sav can take also notes as string, wheter to
compress or not as zsav, variable display widths and variable measures. write_dta can take a stata version.
write_xport a name for the dataset. User defined missing values and value labels are also supported. See the
[Module documentation](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html) for more details.

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
| read_file_in_chunks | generator to read files in chunks |
| write_sav           | write SPSS sav and zsav files |
| write_por           | write SPSS Portable (POR) files |
| write_dta           | write STATA dta files |
| write_xport         | write SAS Xport (XPT) files version 5 |


### More reading options

#### Reading only the headers

All functions accept a keyword argument "metadataonly" which by default is False. If True, then no data will be read,
but still both the metadata and the dataframe will be returned. The metadata will contain all fields as usual, but
the dataframe will be emtpy, although with the correct columns names. Sometimes number_rows may be None if it was not
possible to determine the number of rows without reading the data.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', metadataonly=True)
```

#### Reading selected columns

All functions accept a keyword "usecols" which should be a list of column names. Only the columns which names match those
in the list will be imported (case sensitive). This decreases memory consumption and speeds up the process. Usecols must
always be a list, even if there is only one member.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', usecols=["variable1", "variable2"])

```

#### Reading rows in chunks

Reading large files with hundred of thouseds of rows can be challenging due to memory restrictions. In such cases, it may be helpful
to read the files in chunks.

Every reading function has two arguments row_limit and row_offset that help achieving this. row_offset makes to skip a number of rows before
start reading. row_limit makes to stop after a number of rows are read. Combining both you can read the file in chunks inside or outside a loop.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat("/path/to/file.sas7bdat", row_offset=1, row_limit=1)
# df will contain only the second row of the file
```

Pyreadstat also has a convienence function read_file_in_chunks, which returns a generator that helps you to iterate through the file in
chunks. This function takes as first argument a pyreadstat reading function and a second argument a path to a file. Optionally you can
change the size of the chunks with chunksize (default to 100000), and also add an offset and limit. You can use any keyword argument
you wish to pass to the pyreadstat reading function.

```python
import pyreadstat
fpath = "path/to/file.sas7bdat"
reader = pyreadstat.read_file_in_chunks(pyreadstat.read_sas7bdat, fpath, chunksize= 10, offset=2, limit=100, disable_datetime_conversion=True)

for df, meta in reader:
    print(df) # df will contain 10 rows except for the last one
    # do some cool calculations here for the chunk
```

#### Reading value labels

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

Internally each variable is associated with a label set. This information is stored in meta.variable_to_label. Each
label set contains a map of the actual value in the variable to the label, this informtion is stored in
meta.variable_value_labels. By combining both you can get a dictionary of variable names to a dictionary of actual
values to labels.

For SPSS and STATA:

```python
import pyreadstat

df, meta = pyreadstat.read_sav("test_data/basic/sample.sav")
# the variables mylabl and myord are associated to the label sets labels0 and labels1 respectively
print(meta.variable_to_label)
#{'mylabl': 'labels0', 'myord': 'labels1'}

# labels0 and labels1 contain a dictionary of actual value to label
print(meta.value_labels)
#{'labels0': {1.0: 'Male', 2.0: 'Female'}, 'labels1': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}

# both things have been joined by pyreadstat for convienent use
print(meta.variable_value_labels)
#{'mylabl': {1.0: 'Male', 2.0: 'Female'}, 'myord': {1.0: 'low', 2.0: 'medium', 3.0: 'high'}}

```

SAS is very similar except that meta.variable_to_label comes from the sas7bdat file and meta.value_labels comes from the
sas7bcat file. That means if you read a sas7bdat file and a sas7bcat file togheter meta.variable_value_labels will be
filled in. If you read only the sas7bdat file only meta.variable_to_label will be available and if you read the
sas7bcat file only meta.value_labels will be available. If you read a sas7bdat file and there are no associated label
sets, SAS will assign by default the variable format as label sets.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat("test_data/sas_catalog/test_data_linux.sas7bdat")
meta.variable_to_label
{'SEXA': '$A', 'SEXB': '$B'}

df2, meta2 = pyreadstat.read_sas7bcat("test_data/sas_catalog/test_formats_linux.sas7bcat")
meta2.value_labels
{'$A': {'1': 'Male', '2': 'Female'}, '$B': {'2': 'Female', '1': 'Male'}}

```


#### Missing Values

There are two types of missing values: system and user defined. System are assigned by the program by default. User defined are
valid values that the user decided to give the meaning of missing in order to differentiate between several situations.For
example if one has a categorical variable representing if the person passed a test, you could have 0 for did not pass,
1 for pass, and as user defined missing variables 2 for did not show up for the test, 3 for unable to process the results,
etc.

**By default both cases are represented by NaN when
read with pyreadstat**. Notice that the only possible missing value in pandas is NaN (Not a Number) for both string and numeric
variables, date, datetime and time variables have NaT (Not a Time).

##### SPSS

In the case of SPSS sav files, the user can assign to a numeric variable either up to three discrete missing values or
one range plus one discrete missing value. As mentioned by default all of these possiblities are translated into NaN,
but one can get those original values by passing the argument user_missing=True to the read_sav function:

```python
# user set with default missing values
import pyreadstat
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
import pyreadstat
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
import pyreadstat
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
import pyreadstat
df, meta = pyreadstat.read_sav("/path/to/file.sav", user_missing=True, apply_value_formats=True)
print(meta.missing_ranges)
>>> {'test_passed':[{'hi':2, 'lo':2}, {'hi':3, 'lo':3}]}
```

SPSS sav files also support up to 3 discrete user defined missing values for non numeric (character) variables.
Pyreadstat is able to read those and the behavior is the same as for discrete
numerical user defined missing values. That means those values will be
translated as NaN by default and to the correspoding string value if
user_missing is set to True. meta.missing_ranges will show the string
value as well.

If the value in
a character variable is an empty string (''), it will not be translated to NaN, but will stay as an empty string. This
is because the empty string is a valid character value in SPSS and pyreadstat preserves that property. You can convert
empty strings to nan very easily with pandas if you think it is appropiate
for your dataset.


##### SAS and STATA

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

print(meta.missing_user_values)

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


The information about what values are user missing is stored in the meta object, in the variable missing_user_values.
This is a list listing all user defined missing values.

User defined missing values are currently not supported for file types other than sas7bdat,
sas7bcat and dta.

#### Other options

You can set the encoding of the original file manually. The encoding must be a [iconv-compatible encoding](https://gist.github.com/hakre/4188459).
This is absolutely necessary if you are handling old xport files with
non-ascii characters. Those files do not have stamped the encoding in the
file itself, therefore the encoding must be set manually.


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

### More writing options

#### File specific options

Some special arguments are available depending on the function. write_sav can take also notes as string, wheter to
compress or not as zsav, variable display widths and variable measures. write_dta can take a stata version.
write_xport a name for the dataset. See the
[Module documentation](https://ofajardo.github.io/pyreadstat_documentation/_build/html/index.html) for more details.

#### Writing value labels

The argument variable_value_labels can be passed to write_sav and write_dta to write value labels. This argument must be a
dictionary where keys are variable names (names must match column names in the pandas data frame). Values are another dictionary where
keys are the value present in the dataframe and values are the labels (strings).

```python
import pandas as pd
import pyreadstat
df = pd.DataFrame([[1,1],[2,2],[1,3]], columns=['mylabl', 'myord'])
variable_value_labels = {'mylabl': {1: 'Male', 2: 'Female'}, 'myord': {1: 'low', 2: 'medium', 3: 'high'}}
path = "/path/to/somefile.sav"
pyreadstat.write_sav(df, path, variable_value_labels=variable_value_labels)
```

#### Writing user defined missing values

##### SPSS

The argument missing_ranges can be passed to write_sav to write user defined missing values.
This argument be a dictionary with keys as variable names matching variable
names in the dataframe. The values must be a list. Each element in that list can either be
either a discrete numeric or string value (max 3 per variable) or a dictionary with keys 'hi' and 'lo' to
indicate the upper and lower range for numeric values (max 1 range value + 1 discrete value per
variable). hi and lo may also be the same value in which case it will be interpreted as a discrete
missing value. For this to be effective, values in the dataframe must be the same as reported here and not NaN.

```python
import pandas as pd
import pyreadstat
df = pd.DataFrame([["a",1],["c",2],["c",3]], columns=['mychar', 'myord'])
missing_ranges = {'mychar':['a'], 'myord': [{'hi':2, 'lo':1}]}
path = "/path/to/somefile.sav"
pyreadstat.write_sav(df, path, missing_ranges=missing_ranges)
```

##### STATA

The argument missing_user_values can be passed to write_dta to write user defined missing values only for numeric variables.
This argument be a dictionary with keys as variable names matching variable
names in the dataframe. The values must be a list of missing values, valid values are single character strings
between a and z. Optionally a value label can also be attached to those missing values using variable_value_labels.

```python
import pandas as pd
import pyreadstat
df = pd.DataFrame([["a", 1],[2.2, 2],[3.3, "b"]], columns=['Var1', 'Var2'])
variable_value_labels = {'Var1':{'a':'a missing value'}
missing_ranges = {'Var1':['a'], 'Var2': ['b']}
path = "/path/to/somefile.sav"
pyreadstat.write_sav(df, path, missing_ranges=missing_ranges, variable_value_labels=variable_value_labels)
```

#### Variable type conversion

The following rules are used in order to convert from pandas/numpy/python types to the target file types:

| Python Type         | Converted Type    |
| ------------------- | --------- |
| np.int32 or lower   | integer (stata), numeric (spss, sas) |
| int, np.int64, np.float  | double (stata), numeric (spss, sas)   |
| str                 | character |
| bool                | integer (stata), numeric (spss, sas) |
| datetime, date, time | numeric with datetime/date/time formatting |
| category            | depends on the original dtype |
| any other object    | character |
| column all missing  | integer (stata), numeric (spss, sas)   |
| column with mixed types | character |

Columns with mixed types are translated to character. This does not apply to column
cotaining np.nan, where the missing values are correctly translated. It also does not apply to columns with
user defined missing values in stata/sas where characters (a to z, A to Z, _) will be recorded as numeric.

## Roadmap

* Include latest releases from Readstat as they come out.

## Known limitations

pyreadstat builds on top of Readstat and therefore inherits its limitations. Currently those include:

* Not able to read SAS compressed files.
* Dates, datetimes and times in SPSS POR files are not translated to python dates, datetimes and times, but stay as
  timestamps.
* Cannot write SAS sas7bdat and xport version 8 (version 5 is supported). Those files can be written but not read in
SAS and therefore are not supported in pyreadstat.

Converting data types from foreign applications into python some times also bring some limitations:

* Pyreadstat transforms date, datetime and time like variables which are internally represented in the original application as
 numbers to python datetime objects. Python datetime objects are however limited in the range of dates they can represent
 (for example the max year is 10,000), while in other applications it is possible (although probably an error in the data)
 to have very high or very low dates. In this cases pyreadstat would raise an error:

 ```
 OverflowError: date value out of range
 ```

  The workarounds to deal with this include using the keyword argument disable_datetime_conversion so that you will
  get numbers instead of datetime objects or skipping reading such columns with the argument usecols.

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

[Otto Fajardo](https://github.com/ofajardo) - author, maintainer

[Matthew Brett](http://matthew.dynevor.org/) - contributor [python wheels](https://github.com/MacPython/pyreadstat-wheels)

[Jonathon Love](https://jona.thon.love/) - contributor: open files with international characters.

[Clemens Brunner](https://github.com/cbrnr) - integration with pandas.read_spss

[benjello](https://github.com/benjello), [maxwell8888](https://github.com/maxwell8888), [drcjar](https://github.com/drcjar): improvements to documentation

[bmwiedemann](https://github.com/bmwiedemann), [toddrme2178 ](https://github.com/toddrme2178): improvements to source code
