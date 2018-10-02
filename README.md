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


**DISCLAIMER** 

**Pyreadstat is not a validated package. The results may have inaccuracies deriving from the fact most of the data formats
are not open. Do not use it for critical tasks such as reporting to the authorities. Pyreadstat is not meant to replace
the original applications in this regard and for that reason writing is not supported.**  


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

The module depends on pandas, which you normally have installed if you got Anaconda (highly recommended.) Otherwise you
will have to install it manually before using pyreadstat.

In order to compile from source, you will need a C compiler (see installation). If you want to do changes to the
cython source code, you will need cython.

Readstat depends on the C library iconv to handle character encodings. On mac, the library is found on the system, but
users have sometimes reported problems. In those cases it may help to install libiconv with conda (see later, compilation
on mac)

## Installation

### Using pip

Probably the easiest way: from your conda, virtualenv or just base installation do:

```python
pip install pyreadstat
```

If you are running on a machine without admin rights, and you want to install against your base installation you can do:

```python
pip install pyreadstat --user
```

Notice that at the moment we offer pre-compiled wheels for windows 64 bit and Python 3.5, 3.6 and 3.7. If not one of 
these versions, or running on linux or mac, pip will attempt to compile the package. 

### From a pre-compiled python wheel

In this repository, look in the folder dist, we offer wheels for windows. If there is a wheel (.whl file) compatible 
for your python version and operating system, download it and do:

```
pip install pyreadstat-0.1.7-cp36-cp36m-win_amd64.whl
```

the example file pyreadstat-0.1.7-cp36-cp36m-win_amd64.whl can be a different one depending on your python version and system.

cp36-cp36m-win_amd64.whl means (C) Python 3.6 windows 64 bits and it has been tested both on win 7 and win 10 standard
roche computers, with Anaconda Python installed (it has not been tested with plain python). We also provide wheels for
python 3.5 and 3.7 on windows.

If there is not a suitable wheel for your system, you have to compile the package from source (distribution).

### From source distribution

From this repository, in the folder dist, download the file pyreadstat-x.x.x.tar.gz where x.x.x is the version and do:

```python
pip install pyreadstat-x.x.x.tar.gz
```

If you don't have admin privileges on the machine (for example on BEE) do:

```python
pip install pyreadstat-x.x.x.tar.gz --user
```

You need a working C compiler.

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

You need a working C compiler.

### Compiling on Windows

Compiling on linux is very easy, but on windows is a bit more challenging. 
Some instructions are found [here](https://github.com/Roche/pyreadstat/blob/master/windows_compilation.md)

### Compiling on Mac

Compiling on mac is usually easy. Readstat depends however on the C library iconv to handle character encodings; while 
on linux is part of gclib, on mac it is a separated shared library found on the system (h file is in /usr/include and shared
library on /usr/lib). While compiling against this usually works fine, some users have reported problems (for example
missing symbol _iconv, or libiconv version too old). In those cases it helped to install libiconv with conda:

```
conda install libiconv
```

and then recompile again (be sure to delete any cache, if using pip do pip --no-cache-dir, if using setup.py remove
the folder build, otherwise you may be installing the old compilation again).

## Basic Usage

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

## Reading only the headers

All functions accept a keyword argument "metadataonly" which by default is False. If True, then no data will be read, 
but still both the metadata and the dataframe will be returned. The metadata will contain all fields as usual, but
the dataframe will be emtpy, although with the correct columns names. Sometimes number_rows may be None if it was not
possible to determine the number of rows without reading the data.

```python
import pyreadstat

df, meta = pyreadstat.read_sas7bdat('/path/to/a/file.sas7bdat', metadataonly=True)
```

## Reading value labels

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


## Other options

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

* Conda recipe.
* Support for skipping columns.
* Support for tagged missing values.

## Known limitations

pyreadstat builds on top of Readstat and therefore inherits its limitations. Currently those include:

* Not able to read SAS compressed files. 
* Not reading sas7bcat files produced on linux (windows are fine).
* Not able to skip rows.

## Changelog

A log with the changes for each version can be found [here](https://github.com/Roche/pyreadstat/blob/master/change_log.md)

## License

pyreadstat is distributed under Apache 2.0 license. Readstat is distributed under MIT license. See the License file for
more information.

## Contributing

Contributions are welcome! Those include corrections to the documentation, bugs reporting, testing, 
providing compiled wheels (if you managed to compile
in a OS-python version combination not reported yet) and of course code pull requests. For code pull requests please 
consider opening an issue explaining what you plan to do, so that we can get aligned before you start investing time on
it (this also avoids duplicated efforts).

## People

Otto Fajardo - author

