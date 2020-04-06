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
#import numpy

PY_MAJOR_VERSION = sys.version_info[0]

if PY_MAJOR_VERSION < 3 and os.name == 'nt':
    raise Exception("Python 2 is not supported on Windows.")

# If cython is there and version is good, use it.
try:
    import Cython
    from Cython.Build import cythonize
    cyver = int(Cython.__version__.split(".")[1])
    if cyver < 28:
        msg = "Cython version 0.28 or newer required"
        raise Exception(msg)
    USE_CYTHON = True
except:
    USE_CYTHON = False
    if PY_MAJOR_VERSION < 3:
        msg = "In order to compile with Python 2.7, please install Cython version > 0.28"
        raise Exception(msg)
    if '--use-cython' in sys.argv:
        raise

# To re-compile the pyx sources use the option --use-cython
if '--use-cython' in sys.argv:
    if not USE_CYTHON:
        raise Exception("--use-cython failed to set cython to be used!")
    sys.argv.remove('--use-cython')

ext = '.pyx' if USE_CYTHON else '.c'


dir_path = os.path.dirname(os.path.realpath(__file__))
source_dir_root = "src"

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

# libraries and data (in this case data are windows dlls)
# altough these are win specific we want them to be in the source distribution
# therefore we will always include them.
data_files = []
libraries=["m", "z"]
# Windows
if os.name == 'nt':
    is64bit = sys.maxsize > 2 ** 32
    win_install_dir = "Lib/site-packages/pyreadstat"
    if is64bit:
        data_folder = "win_libs/64bit/"
        data_files = [(win_install_dir, [data_folder + "zlib1.dll", data_folder + "libiconv-2.dll"])]
    else:
        data_folder = "win_libs/32bit/"
        data_files = [(win_install_dir, [data_folder + "zlib1.dll", data_folder + "libiconv-2.dll", data_folder +"libwinpthread-1.dll", data_folder + "libgcc_s_dw2-1.dll"])]
    #data_files = [("", [data_folder + "zlib1.dll", data_folder + "libiconv-2.dll"])]
    libraries.append("iconv")
else:
    _platform = sys.platform
    # Mac: iconv needs to be linked statically
    if _platform.lower().startswith("darwin"):
        libraries.append("iconv")

# Extensions
sources.sort()
extensions = [Extension("pyreadstat.pyreadstat",
                    sources=["pyreadstat/pyreadstat" + ext] + sources,
                    # this dot here is important for cython to find the pxd files
                    include_dirs = [source_dir_root] + source_dirs + ["pyreadstat", "."],
                    libraries=libraries,
                    extra_compile_args=["-Ireadstat", "-DHAVE_ZLIB=1"] ),
                Extension("pyreadstat._readstat_parser",
                    sources=["pyreadstat/_readstat_parser" + ext] + sources,
                    include_dirs = [source_dir_root] + source_dirs + ["pyreadstat", "."],
                    libraries=libraries,
                    extra_compile_args=["-Ireadstat", "-DHAVE_ZLIB=1"]),
                Extension("pyreadstat._readstat_writer",
                        sources=["pyreadstat/_readstat_writer" + ext] + sources,
                        include_dirs=[source_dir_root] + source_dirs + ["pyreadstat", "."],# + [numpy.get_include()],
                        libraries=libraries,
                        extra_compile_args=["-Ireadstat", "-DHAVE_ZLIB=1"])
              ]

# By setting this compiler directive, cython will
# embed signature information in docstrings. Sphinx then knows how to extract
# and use those signatures.
for e in extensions:
    e.cython_directives = {"embedsignature": True}

if USE_CYTHON:
    #from Cython.Build import cythonize
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
    version='0.3.0',
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
    install_requires=['pandas>0.24.0'],
)
