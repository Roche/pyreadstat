# 0.3.1 (github, pypi and conda 20200406
* Updated Readstat to commit a71b4e80dae729e236d63d42066e79ca646cd23b (on dev)
* Updated Readstat update fixes #3

# 0.3.0 (github, pypi and conda 20200406)
* Updated Readstat to Release 1.1.2, this did not fix #3
* added capacity to read and write files with paths starting with tilde
* added pandas as dependency > 0.24.0
* copying windows dlls inside pyreadstat folder in site-packages 

# 0.2.9 (github 26.08.2019, pypi and conda 27.08.2019)
* implemented ability to read files in chunks
* implemented write_por
* Readstat sources updated to release 1.1.0

# 0.2.8 (github, pypi, conda 30.07.2019)
* write user defined missing values, value labels for spss and stata
* write variable_display_width and variable_measure for spss
* breaking change: missing_user_values is now dict instead of set both for reading and writing.
* windows wheels build with appveyor + m2w64-toolchain. Wheels for python 2.7 not produced 
  anymore, instead setup.py raises an error if trying to compile with 2.7 on windows so that
  pip will raise this error when trying to install from source distribution.
* column_names_to_labels: new member in metadata object, a dict of column names to labels
* setup.py: ordering source files to make the compilation reproducible

# 0.2.7 (github, pypi, conda 27.06.2019)
* added writing capability.

# 0.2.6 (github, pypi, conda 15.06.2019)
* MANIFEST.in changed so that windows dlls get into the source distribution, setup.py
changed so that those get installed only on windows but not unix.
* Implemented option disable_datetime_conversion for all reading functions in order
to skip date/datetime and time object conversion.
* Updated Readstat Sources to Release Version 1.0.1

# 0.2.5 (github, pypi and conda 09.05.2019)
* Same as 0.2.4, just fixed issues in source distribution so that conda build 
  succeeds.

# 0.2.4 (github and pypi 08.05.2019)
* encoding support for xpt files.
* support for user defined missing character values in sav.
* Updated Readstat Sources to Release 1.0

# 0.2.3 (github 04.02.2019)
* User defined values fixed for sas7bdat, implemented for sas7bcat and dta.
* Readstat sources updated.

# 0.2.2 (github 18.01.2019)
* Implemented support for reading international characters in files.

# 0.2.1 (github 18.12.2018, release tag, conda-forge 04.02.2019)
* Implemented user defined missing values for read_sas7bdat. Currently not working for 64 bit files.
* Corrected datetime transformations for stata dta files, sample.dta updated
* cython updated from 26.1 to 29.1
* Readstat source update, latest version as 17.12.2018 (latest commit: b52b77447d293f0fd530aabdab3330909a61bb8d)
* The latest readstat brings: POR files support improved (sample.por updated), sas7bcat support improved, improvements
  for sav files. 

# 0.2.0 (github 19.10.2018, Pypi 19.10.2018)
* Implemented usecols to be able to read only selected columns.
* Readstat source updated to fix a [bug](https://github.com/WizardMac/ReadStat/issues/153) in usecols, latest version
as 17.10.2018 (latest commit: 727bfb87aa332da0df96b77d86694c0e9c464723)
* Implemented user defined missing values (user_missing keyword) for read_sav (only for SPSS files)

# 0.1.9 (github 12.10.2018, Pypi 15.10.2018)

* Bug when reading sas7bcat files [#4](https://github.com/Roche/pyreadstat/issues/4) fixed in 
readstat [#152](https://github.com/WizardMac/ReadStat/issues/152). Readstat src files updated with latest version
as of 12.10.2018 (latest commit: 4c798478ed1eff35ed16c067a3b0b3fd0a9a0561)

# 0.1.8
* Installation on mac fixed (static linking iconv, [#2](https://github.com/Roche/pyreadstat/issues/2))

# 0.1.7
* same as 0.1.8, had to bump the version in order to fix the description in pypi.

# 0.1.6
* First public release
