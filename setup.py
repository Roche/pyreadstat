# #############################################################################
# Copyright 2018 Hoffmann-La Roche
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# #############################################################################

import setuptools
from distutils.core import setup, Extension
import os
import sys
import Cython
from Cython.Build import cythonize

PY_MAJOR_VERSION = sys.version_info[0]

if PY_MAJOR_VERSION < 3 and os.name == 'nt':
    raise Exception("Python 2 is not supported on Windows.")

cyver = int(Cython.__version__.split(".")[0])
if cyver < 3:
    msg = "Cython version 3 or newer required"
    raise Exception(msg)

ext = '.pyx'


dir_path = os.path.dirname(os.path.realpath(__file__))
source_dir_root = "src"
python_dir = sys.exec_prefix

# Get a list of C source files and C source directories but omitting certain things
omitted_sources = [
    "mod_xlsx.c",
    "mod_csv_reader.c",
    "readstat.c"]
omitted_source_dirs = ["src/test", "src/bin", "src/fuzz"]

sources = list()
for dirname, _ , filenames in os.walk(source_dir_root):
    if dirname not in omitted_source_dirs:
        for filename in filenames:
            if filename.endswith("c") and filename not in omitted_sources:
                cursource = os.path.join(".", dirname, filename)
                sources.append(cursource)

source_dirs = [dirname for dirname, _, _ in os.walk(source_dir_root) if dirname not in omitted_source_dirs]


data_files = []
libraries = []
include_dirs = [source_dir_root] + source_dirs + ["pyreadstat", "."]
library_dirs = []
# Windows
# On Windows we have two possible setups: the user has included the static libraries in win_libs/64bit
# Or the user is going to use the Conda forge versions of those. See the windows compilation document
# for more details
if os.name == 'nt':
    is64bit = sys.maxsize > 2 ** 32
    # The user included the compiled static libraries
    if os.path.isfile("win_libs/64bit/libiconv-static.lib") and os.path.isfile("win_libs/64bit/libz-static.lib"):
        libraries.extend(["libiconv-static", "libz-static"])
        include_dirs.append("win_libs/64bit")
        library_dirs.append("win_libs/64bit")
    # conda forge libraries
    else:
        libraries.extend(["iconv", "zlib"])
        include_dirs.append(os.path.join(python_dir, "Library", "include"))
        library_dirs.append(os.path.join(python_dir, "Library", "bin"))
        library_dirs.append(os.path.join(python_dir, "Library", "lib"))
else:
    libraries.extend(["m", "z"])
    _platform = sys.platform
    # Mac: iconv needs to be linked statically
    if _platform.lower().startswith("darwin"):
        libraries.append("iconv")

# Extensions
sources.sort()
extensions = [Extension("pyreadstat.pyreadstat",
                    sources=["pyreadstat/pyreadstat" + ext] + sources,
                    # this dot here is important for cython to find the pxd files
                    include_dirs =include_dirs,
                    libraries=libraries,
                    library_dirs=library_dirs,
                    extra_compile_args=["-Ireadstat", "-DHAVE_ZLIB=1"] ),
                Extension("pyreadstat._readstat_parser",
                    sources=["pyreadstat/_readstat_parser" + ext] + sources,
                    include_dirs = include_dirs,
                    library_dirs=library_dirs,
                    libraries=libraries,
                    extra_compile_args=["-Ireadstat", "-DHAVE_ZLIB=1"]),
                Extension("pyreadstat._readstat_writer",
                        sources=["pyreadstat/_readstat_writer" + ext] + sources,
                        include_dirs=include_dirs,# + [numpy.get_include()],
                        library_dirs=library_dirs,
                        libraries=libraries,
                        extra_compile_args=["-Ireadstat", "-DHAVE_ZLIB=1"])
              ]

# By setting this compiler directive, cython will
# embed signature information in docstrings. Sphinx then knows how to extract
# and use those signatures.
for e in extensions:
    e.cython_directives = {"embedsignature": True}

# let's use cython with force so that it always recompiles in case 
# somebody is switching between python 2 and 3
extensions = cythonize(extensions, compile_time_env={'PY_MAJOR_VERSION':PY_MAJOR_VERSION}, force=True)

long_description = """ A Python package to read and write SAS
(sas7bdat, sas7bcat, xport/xpt), SPSS (sav, zsav, por) and Stata (dta) files into/from pandas data frames. It is a wrapper
around the C library readstat.<br>
Please visit out project home page for more information:<br>
https://github.com/Roche/pyreadstat"""

short_description = "Reads and Writes SAS, SPSS and Stata files into/from pandas data frames."

setup(
    name='pyreadstat',
    version='1.3.0',
    description=short_description,
    author="Otto Fajardo",
    author_email="pleasecontactviagithub@notvalid.com",
    url="https://github.com/Roche/pyreadstat",
    download_url="https://github.com/Roche/pyreadstat/dist",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Cython",
        "Programming Language :: C",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Environment :: Console",
    ],
    ext_modules=extensions,
    packages=["pyreadstat"],
    data_files=data_files,
    install_requires=['pandas>=1.2.0'],
    license="Apache License Version 2.0",
)
