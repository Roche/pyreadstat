# 0.2.2 (github 18.01.2018)
* Implemented support for reading international characters in files.

# 0.2.1 (github 18.12.2018, release tag)
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