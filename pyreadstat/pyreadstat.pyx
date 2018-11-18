# cython: c_string_type=unicode, c_string_encoding=utf8

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

# TODO:
## if want to profile: # cython: profile=True


from readstat_api cimport readstat_parse_sas7bdat, readstat_parse_dta, readstat_parse_sav
from readstat_api cimport readstat_parse_por, readstat_parse_xport
from readstat_api cimport readstat_parse_sas7bcat
from _readstat_parser cimport py_file_format, run_conversion
cimport _readstat_parser
from copy import deepcopy


# Public interface

# Parsing functions

def read_sas7bdat(str filename_path="", metadataonly=False, dates_as_pandas_datetime=False, catalog_file=None,
                  formats_as_category=True, str encoding=None, list usecols=None, bytes data=b"", bytes catalog_data=b""):
    r"""
    Read a SAS sas7bdat file.
    It accepts the path to a sas7bcat.
    
    Parameters
    ----------
        filename_path : str, optional
            path to the file. The string is assumed to be utf-8 encoded. Optional if data is specified.
        metadataonly : bool, optional
            by default False. IF true, no data will be read but only metadata, so that you can get all elements in the
            metadata object. The data frame will be set with the correct column names but no data.
        dates_as_pandas_datetime : bool, optional
            by default False. If true dates will be transformed to pandas datetime64 instead of date.
        catalog_file : str, optional
            path to a sas7bcat file. By default is None. If not None, will parse the catalog file and replace the values
            by the formats in the catalog, if any appropiate is found. If this is not the behavior you are looking for,
            Use read_sas7bcat to parse the catalog independently
            of the sas7bdat and set_catalog_to_sas to apply the resulting format into sas7bdat files.
        formats_as_category : bool, optional
            Will take effect only if the catalog_file was specified. If True the variables whose values were replaced
            by the formats will be transformed into pandas categories.
        encoding : str, optional
            Defaults to None. If set, the system will use the defined encoding instead of guessing it. It has to be an
            iconv-compatible name
        usecols : list, optional
            a list with column names to read from the file. Only those columns will be imported. Case sensitive!
        data : bytes, optional
            raw data. Used to load the contents from memory rather than a file path.
        
    Returns
    -------
        data_frame : pandas dataframe
            a pandas data frame with the data
        metadata
            object with metadata. The members variables_value_labels will be empty unless a valid catalog file is
            supplied.
            Look at the documentation for more information.
    """

    cdef bint metaonly = 0
    if metadataonly:
        metaonly = 1

    cdef bint dates_as_pandas = 0
    if dates_as_pandas_datetime:
        dates_as_pandas = 1

    cdef bint usernan = 0
    
    cdef py_file_format file_format = _readstat_parser.FILE_FORMAT_SAS
    data_frame, metadata = run_conversion(filename_path, data, file_format, readstat_parse_sas7bdat, encoding, metaonly,
                                          dates_as_pandas, usecols, usernan)
    metadata.file_format = "sas7bdat"

    if catalog_file:
        _ , catalog = read_sas7bcat(catalog_file, encoding=encoding)
        data_frame, metadata = set_catalog_to_sas(data_frame, metadata, catalog, formats_as_category=formats_as_category)
    elif catalog_data:
        _ , catalog = read_sas7bcat(encoding=encoding, data=catalog_data)
        data_frame, metadata = set_catalog_to_sas(data_frame, metadata, catalog, formats_as_category=formats_as_category)

    return data_frame, metadata


def read_xport(str filename_path="", metadataonly=False, dates_as_pandas_datetime=False,
               str encoding=None, list usecols=None, bytes data=b""):
    r"""
    Read a SAS xport file.

    Parameters
    ----------
        filename_path : str, optional
            path to the file. The string is assumed to be utf-8 encoded. Optional if data is specified.
        metadataonly : bool, optional
            by default False. IF true, no data will be read but only metadata, so that you can get all elements in the
            metadata object. The data frame will be set with the correct column names but no data.
        dates_as_pandas_datetime : bool, optional
            by default False. If true dates will be transformed to pandas datetime64 instead of date.
        encoding : str, optional
            Defaults to None. If set, the system will use the defined encoding instead of guessing it. It has to be an
            iconv-compatible name
        usecols : list, optional
            a list with column names to read from the file. Only those columns will be imported. Case sensitive!
        data : bytes, optional
            raw data. Used to load the contents from memory rather than a file path.

    Returns
    -------
        data_frame : pandas dataframe
            a pandas data frame with the data
        metadata :
            object with metadata. Look at the documentation for more information.
    """

    cdef bint metaonly = 0
    if metadataonly:
        metaonly = 1

    cdef bint dates_as_pandas = 0
    if dates_as_pandas_datetime:
        dates_as_pandas = 1

    cdef bint usernan = 0
    
    cdef py_file_format file_format = _readstat_parser.FILE_FORMAT_SAS
    data_frame, metadata = run_conversion(filename_path, data, file_format, readstat_parse_xport, encoding, metaonly,
                                          dates_as_pandas, usecols, usernan)
    metadata.file_format = "xport"

    return data_frame, metadata


def read_dta(str filename_path="", metadataonly=False, dates_as_pandas_datetime=False, apply_value_formats=False,
             formats_as_category=True, str encoding=None, list usecols=None, bytes data=b""):
    r"""
    Read a STATA dta file

    Parameters
    ----------
        filename_path : str, optional
            path to the file. The string is assumed to be utf-8 encoded. Optional if data is specified.
        metadataonly : bool, optional
            by default False. IF true, no data will be read but only metadata, so that you can get all elements in the
            metadata object. The data frame will be set with the correct column names but no data.
        dates_as_pandas_datetime : bool, optional
            by default False. If true dates will be transformed to pandas datetime64 instead of date.
        apply_value_formats : bool, optional
            by default False. If true it will change values in the dataframe for they value labels in the metadata,
            if any appropiate are found.
        formats_as_category : bool, optional
            by default True. Takes effect only if apply_value_formtas is True. If True, variables with values changed
            for their formatted version will be transformed into pandas categories.
        encoding : str, optional
            Defaults to None. If set, the system will use the defined encoding instead of guessing it. It has to be an
            iconv-compatible name
        usecols : list, optional
            a list with column names to read from the file. Only those columns will be imported. Case sensitive!
        data : bytes, optional
            raw data. Used to load the contents from memory rather than a file path.

    Returns
    -------
        data_frame : pandas dataframe
            a pandas data frame with the data
        metadata :
            object with metadata. Look at the documentation for more information.
    """

    cdef bint metaonly = 0
    if metadataonly:
        metaonly = 1

    cdef bint dates_as_pandas = 0
    if dates_as_pandas_datetime:
        dates_as_pandas = 1

    cdef bint usernan = 0
    
    cdef py_file_format file_format = _readstat_parser.FILE_FORMAT_STATA
    data_frame, metadata = run_conversion(filename_path, data, file_format, readstat_parse_dta, encoding, metaonly,
                                          dates_as_pandas, usecols, usernan)
    metadata.file_format = "dta"

    if apply_value_formats:
        data_frame = set_value_labels(data_frame, metadata, formats_as_category=formats_as_category)

    return data_frame, metadata


def read_sav(str filename_path="", metadataonly=False, dates_as_pandas_datetime=False, apply_value_formats=False,
             formats_as_category=True, str encoding=None, list usecols=None, user_missing=False, bytes data=b""):
    r"""
    Read a SPSS sav or zsav (compressed) files

    Parameters
    ----------
        filename_path : str, optional
            path to the file. The string is assumed to be utf-8 encoded. Optional if data is specified.
        metadataonly : bool, optional
            by default False. IF true, no data will be read but only metadata, so that you can get all elements in the
            metadata object. The data frame will be set with the correct column names but no data.
        dates_as_pandas_datetime : bool, optional
            by default False. If true dates will be transformed to pandas datetime64 instead of date.
        apply_value_formats : bool, optional
            by default False. If true it will change values in the dataframe for they value labels in the metadata,
            if any appropiate are found.
        formats_as_category : bool, optional
            by default True. Takes effect only if apply_value_formtas is True. If True, variables with values changed
            for their formatted version will be transformed into pandas categories.
        encoding : str, optional
            Defaults to None. If set, the system will use the defined encoding instead of guessing it. It has to be an
            iconv-compatible name
        usecols : list, optional
            a list with column names to read from the file. Only those columns will be imported. Case sensitive!
        user_missing : bool, optional
            by default False, in this case user defined missing values are delivered as nan. If true, the missing values
            will be deliver as is, and an extra piece of information will be set in the metadata (missing_ranges)
            to be able to interpret those values as missing
        data : bytes, optional
            raw data. Used to load the contents from memory rather than a file path.

    Returns
    -------
        data_frame : pandas dataframe
            a pandas data frame with the data
        metadata :
            object with metadata. Look at the documentation for more information.
    """

    cdef bint metaonly = 0
    if metadataonly:
        metaonly = 1

    cdef bint dates_as_pandas = 0
    if dates_as_pandas_datetime:
        dates_as_pandas = 1

    cdef bint usernan = 0
    if user_missing:
        usernan = 1
    
    cdef py_file_format file_format = _readstat_parser.FILE_FORMAT_SPSS
    data_frame, metadata = run_conversion(filename_path, data, file_format, readstat_parse_sav, encoding, metaonly,
                                          dates_as_pandas, usecols, usernan)
    metadata.file_format = "sav/zsav"

    if apply_value_formats:
        data_frame = set_value_labels(data_frame, metadata, formats_as_category=formats_as_category)

    return data_frame, metadata


def read_por(str filename_path="", metadataonly=False, dates_as_pandas_datetime=False, apply_value_formats=False,
             formats_as_category=True, str encoding=None, list usecols=None, bytes data=b""):
    r"""
    Read a SPSS por file

    Parameters
    ----------
        filename_path : str, optional
            path to the file. The string is assumed to be utf-8 encoded. Optional if data is specified.
        metadataonly : bool, optional
            by default False. IF true, no data will be read but only metadata, so that you can get all elements in the
            metadata object. The data frame will be set with the correct column names but no data.
        dates_as_pandas_datetime : bool, optional
            by default False. If true dates will be transformed to pandas datetime64 instead of date.
        apply_value_formats : bool, optional
            by default False. If true it will change values in the dataframe for they value labels in the metadata,
            if any appropiate are found.
        formats_as_category : bool, optional
            by default True. Takes effect only if apply_value_formtas is True. If True, variables with values changed
            for their formatted version will be transformed into pandas categories.
        encoding : str, optional
            Defaults to None. If set, the system will use the defined encoding instead of guessing it. It has to be an
            iconv-compatible name
        usecols : list, optional
            a list with column names to read from the file. Only those columns will be imported. Case sensitive!
        data : bytes, optional
            raw data. Used to load the contents from memory rather than a file path.

    Returns
    -------
        data_frame : pandas dataframe
            a pandas data frame with the data
        metadata :
            object with metadata. Look at the documentation for more information.
    """

    cdef bint metaonly = 0
    if metadataonly:
        metaonly = 1

    cdef bint dates_as_pandas = 0
    if dates_as_pandas_datetime:
        dates_as_pandas = 1

    cdef bint usernan = 0
    
    cdef py_file_format file_format = _readstat_parser.FILE_FORMAT_SPSS
    data_frame, metadata = run_conversion(filename_path, data, file_format, readstat_parse_por, encoding, metaonly,
                                          dates_as_pandas, usecols, usernan)
    metadata.file_format = "por"
    if apply_value_formats:
        data_frame = set_value_labels(data_frame, metadata, formats_as_category=formats_as_category)

    return data_frame, metadata
    


def read_sas7bcat(str filename_path="", str encoding=None, bytes data=b""):
    r"""
    Read a SAS sas7bcat file. The returning dataframe will be empty. The metadata object will contain a dictionary
    value_labels that contains the formats. When parsing the sas7bdat file, in the metadata, the dictionary
    variable_to_label contains a map from variable name to the formats.
    In order to apply the catalog to the sas7bdat file use set_catalog_to_sas or pass the catalog file as an argument
    to read_sas7bdat directly.
    SAS catalog files are difficult ones, some of them can be read only in specific SAS version, may contain strange
    encodings etc. Therefore it may be that many catalog files are not readable from this application.

    Parameters
    ----------
        filename_path : str, optional
            path to the file. The string is assumed to be utf-8 encoded. Optional if data is specified.
        encoding : str, optional
            Defaults to None. If set, the system will use the defined encoding instead of guessing it. It has to be an
            iconv-compatible name
        data : bytes, optional
            raw data. Used to load the contents from memory rather than a file path.

    Returns
    -------
        data_frame : pandas dataframe
            a pandas data frame with the data (no data in this case, so will be empty)
        metadata :
            object with metadata. The member value_labels is the one that contains the formats.
            Look at the documentation for more information.
    """
    cdef bint metaonly = 1
    cdef bint dates_as_pandas = 0
    cdef list usecols = None
    cdef bint usernan = 0

    cdef py_file_format file_format = _readstat_parser.FILE_FORMAT_SAS
    data_frame, metadata = run_conversion(filename_path, data, file_format, readstat_parse_sas7bcat, encoding, metaonly,
                                          dates_as_pandas, usecols, usernan)
    metadata.file_format = "sas7bcat"

    return data_frame, metadata

# Functions to deal with value labels


def set_value_labels(dataframe, metadata, formats_as_category=True):
    """
    Changes the values in the dataframe according to the value formats in the metadata.
    It will return a copy of the dataframe. If no appropiate formats were found, the result will be an unchanged copy
    of the original dataframe.

    Parameters
    ----------
        dataframe : pandas dataframe
            resulting from parsing a file
        metadata : dictionary
            resulting from parsing a file
        formats_as_category : bool, optional
            defaults to True. If True the variables having formats will be transformed into pandas categories.

    Returns
    -------
        df_copy : pandas dataframe
            a copy of the original dataframe with the values changed, if appropiate formats were found, unaltered
            otherwise
    """

    df_copy = dataframe.copy()

    if metadata.value_labels and metadata.variable_to_label:
        for var_name, label_name in metadata.variable_to_label.items():
            labels = metadata.value_labels.get(label_name)
            if labels:
                df_copy[var_name] = df_copy[var_name].apply(lambda x: labels.get(x, x))
                if formats_as_category:
                    df_copy[var_name] = df_copy[var_name].astype("category")

    return df_copy

def set_catalog_to_sas(sas_dataframe, sas_metadata, catalog_metadata, formats_as_category=True):
    """
    Changes the values in the dataframe and sas_metadata according to the formats in the catalog.
    It will return a copy of the dataframe and metadata. If no appropriate formats were found, the result will
    be an unchanged copy of the original dataframe.

    Parameters
    ----------
        sas_dataframe : pandas dataframe
            resulting from parsing a sas file
        sas_metadata : dictionary
            resulting from parsing a sas file
        catalog_metadata : dictionary
            resulting from parsing a sas7bcat (catalog) file
        formats_as_category : bool, optional
            defaults to True. If True the variables having formats will be transformed into pandas categories.

    Returns
    -------
        df_copy : pandas dataframe
            a copy of the original dataframe with the values changed, if appropriate formats were found, unaltered
            otherwise
        metadata : dict
            a copy of the original sas_metadata enriched with catalog information if found, otherwise unaltered
    """

    if catalog_metadata.value_labels and sas_metadata.variable_to_label:
        catalog_metadata_copy = deepcopy(catalog_metadata)
        metadata = deepcopy(sas_metadata)
        metadata.value_labels = catalog_metadata_copy.value_labels
        df_copy = set_value_labels(sas_dataframe, metadata, formats_as_category=formats_as_category)

        variable_value_labels = dict()
        for var_name, var_label in metadata.variable_to_label.items():
            current_labels = catalog_metadata_copy.value_labels.get(var_label)
            if current_labels:
                variable_value_labels[var_name] = current_labels
        metadata.variable_value_labels = variable_value_labels

    else:
        df_copy = sas_dataframe.copy()
        metadata = deepcopy(sas_metadata)

    return df_copy, metadata


    
    