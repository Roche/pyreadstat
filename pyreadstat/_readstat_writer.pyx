# cython: c_string_type=unicode, c_string_encoding=utf8, language_level=2
# ###cython: profile=True
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
import os
from readstat_api cimport *
from _readstat_parser import ReadstatError, PyreadstatError
from _readstat_parser cimport check_exit_status

import numpy as np
#cimport numpy as np
import pandas as pd
import datetime
import calendar
IF PY_MAJOR_VERSION >2:
    from datetime import timezone as _timezone
ELSE: # not available on python 2
    import pytz as _timezone
from libc.math cimport round, NAN


cdef set int_types = {int, np.dtype('int32'), np.dtype('int16'), np.dtype('int8'), np.dtype('uint8'), np.dtype('uint16'),
             np.int32, np.int16, np.int8, np.uint8, np.uint16}
cdef set int_mixed_types = {pd.Int8Dtype(), pd.Int16Dtype(), pd.Int32Dtype(), pd.UInt8Dtype(), pd.UInt16Dtype()}
cdef set float_types = {float, np.dtype('int64'), np.dtype('uint64'), np.dtype('uint32'), np.dtype('float'),
               np.int64, np.uint64, np.uint32, np.float, pd.Int64Dtype(), pd.UInt32Dtype(), pd.UInt64Dtype()}
cdef set numeric_types = int_types.union(float_types).union(int_mixed_types)
cdef set datetime_types = {datetime.datetime, np.datetime64, pd._libs.tslibs.timestamps.Timestamp}
cdef set nat_types = {datetime.datetime, np.datetime64, pd._libs.tslibs.timestamps.Timestamp, datetime.time, datetime.date}
cdef set pyrwriter_datetimelike_types = {PYWRITER_DATE, PYWRITER_DATETIME, PYWRITER_TIME}
cdef set pywriter_numeric_types = {PYWRITER_DOUBLE, PYWRITER_INTEGER, PYWRITER_LOGICAL, PYWRITER_DATE, PYWRITER_DATETIME, PYWRITER_TIME}
cdef dict pandas_to_readstat_types = {PYWRITER_DOUBLE: READSTAT_TYPE_DOUBLE, PYWRITER_INTEGER: READSTAT_TYPE_INT32,
                                      PYWRITER_CHARACTER: READSTAT_TYPE_STRING, PYWRITER_LOGICAL: READSTAT_TYPE_INT32,
                                      PYWRITER_OBJECT: READSTAT_TYPE_STRING, PYWRITER_DATE: READSTAT_TYPE_DOUBLE,
                                      PYWRITER_DATETIME: READSTAT_TYPE_DOUBLE, PYWRITER_TIME: READSTAT_TYPE_DOUBLE}

cdef double spss_offset_secs = 12219379200
cdef double sas_offset_secs = 315619200
cdef double spss_offset_days = 141428
cdef double sas_offset_days = 3653
cdef object date_0 = datetime.datetime(1970,1,1).date()

cdef valid_user_missing_sas = [chr(x) for x in range(ord("A"), ord("Z")+1)] + ["_"]
cdef valid_user_missing_stata = [chr(x) for x in range(ord("a"), ord("z")+1)]


cdef double convert_datetimelike_to_number(dst_file_format file_format, pywriter_variable_type curtype, object curval) except *:
    """
    converts a datime like python/pandas object to a float
    """

    cdef double offset_days, tstamp

    if file_format == FILE_FORMAT_SAV or file_format == FILE_FORMAT_POR:
        offset_days = spss_offset_days
        offset_secs = spss_offset_secs
    else:
        offset_days = sas_offset_days
        offset_secs = sas_offset_secs

    if curtype == PYWRITER_DATETIME:
        # get timestamp in seconds
        if type(curval) == pd._libs.tslibs.timestamps.Timestamp:
            curval = curval.asm8

        if type(curval) == datetime.datetime:
            #tstamp = curval.replace(tzinfo=timezone.utc).timestamp() # works only in python 3
            tstamp = calendar.timegm(curval.replace(tzinfo=_timezone.utc).timetuple())
        elif type(curval) == np.datetime64:
            if curval.dtype.name == "datetime64[ns]":
                tstamp = round(<double>curval.astype(float)/1e9)
            elif curval.dtype.name == "datetime64[us]":
                tstamp = round(<double>curval.astype(float)/1e6)
            elif curval.dtype.name == "datetime64[ms]":
                tstamp = round(<double>curval.astype(float)/1e3)

        tstamp += offset_secs
        if file_format == FILE_FORMAT_DTA:
            # stata stores in milliseconds
            tstamp *= 1000

    elif curtype == PYWRITER_DATE:
        if type(curval) == datetime.date:
            days = curval - date_0
            tstamp = days.days
            tstamp += offset_days
            if file_format == FILE_FORMAT_SAV or file_format == FILE_FORMAT_POR:
                # spss stores in seconds
                tstamp *= 86400

    elif curtype == PYWRITER_TIME:
        if type(curval) == datetime.time:
            tdelta = datetime.datetime.combine(datetime.date.min, curval) - datetime.datetime.min
            tstamp = tdelta.total_seconds()
            #tstamp += offset * 86400
            if file_format == FILE_FORMAT_DTA:
                # stata stores in milliseconds
                tstamp *= 1000

    return tstamp

cdef char * get_datetimelike_format_for_readstat(dst_file_format file_format, pywriter_variable_type curtype):
    """
    gives back a string with the format of the variable (according to the final application) to be used by readstat 
    """

    if curtype == PYWRITER_DATE:
        if file_format == FILE_FORMAT_DTA:
            return "%td"
        else:
            return "DATE"
    elif curtype == PYWRITER_DATETIME:
        if file_format == FILE_FORMAT_DTA:
            return "%tc"
        else:
            return "DATETIME"
    elif curtype == PYWRITER_TIME:
        if file_format == FILE_FORMAT_DTA:
            return "%tcHH:MM:SS"
        else:
            return "TIME"
    else:
        raise PyreadstatError("Unknown pywriter variable format")


cdef int get_pandas_str_series_max_length(object series):
    """ For a pandas string series get the max length of the strings. Assumes there is no NaN among the elements. 
    """
    values = series.values
    cdef str val
    cdef bytes temp
    cdef int max_length = 0
    cdef int curlen
    for val in values:
        temp = val.encode("utf-8")
        curlen = len(temp)
        if curlen > max_length:
            max_length = curlen

    return max_length

    #return int(series.str.encode(encoding="utf-8").str.len().max())

cdef int check_series_all_same_types(object series, object type_to_check):
    """
    1 if all elements in a series are of type type_to_check, 0 otherwise
    """

    values = series.values
    for val in values:
        if type(val) != type_to_check:
            return 0
    return 1


cdef list get_pandas_column_types(object df, dict missing_user_values):
    """
    From a pandas data frame, get a list with tuples column types as first element, max_length as second and is_missing
    as third.
    max_lenght is the max length of a string or string representation of an object, 0 for numeric types. is_missing flags
    wether the series has missing values (1) or not (0)
    """

    cdef int max_length

    cdef list types = df.dtypes.values.tolist()
    cdef list columns = df.columns.values.tolist()

    cdef list result = list()
    cdef int equal, is_missing

    for indx, (col_name, col_type) in enumerate(zip(columns, types)):

        max_length = 0
        curseries = df.iloc[:, indx]
        curuser_missing = None
        if missing_user_values:
            curuser_missing = missing_user_values.get(col_name)

        # recover original type for categories
        if type(col_type) is pd.core.dtypes.dtypes.CategoricalDtype:
            col_type = np.asarray(curseries).dtype

        if col_type in int_types:
            result.append((PYWRITER_INTEGER, 0,0))
        elif col_type in float_types:
            # if there is a NaN, that's a valid double value, no need to handle specially as missing
            result.append((PYWRITER_DOUBLE, 0,0))
        elif col_type == np.bool:
            result.append((PYWRITER_LOGICAL, 0,0))
        # np.datetime64[ns]
        elif col_type == np.dtype('<M8[ns]') or col_type in datetime_types:
            result.append((PYWRITER_DATETIME, 0,0))
        elif col_type == np.object or col_type in int_mixed_types:
            is_missing = 0
            if curuser_missing:
                curseries = curseries[~curseries.isin(curuser_missing)].reset_index(drop=True)
            if np.any(pd.isna(curseries)):
                if col_type in int_mixed_types:
                    result.append((PYWRITER_INTEGER, 0, 1))
                    continue
                col = curseries.dropna().reset_index(drop=True)
                is_missing = 1
                if len(col):
                    curtype = type(col[0])
                    equal = check_series_all_same_types(col, curtype)
                    #equal = col.apply(lambda x: type(x) == curtype)
                    #if not np.all(equal):
                    if not equal:
                        max_length = get_pandas_str_series_max_length(col.astype(str))
                        result.append((PYWRITER_OBJECT, max_length, 1))
                        continue
                else:
                    result.append((PYWRITER_LOGICAL, 0, 1))
                    continue
            else:
                if col_type in int_mixed_types:
                    result.append((PYWRITER_INTEGER, 0, 0))
                    continue
                curtype = type(curseries[0])
                equal = check_series_all_same_types(curseries, curtype)
                #equal = curseries.apply(lambda x: type(x) == curtype)
                #if not np.all(equal):
                if not equal:
                    max_length = get_pandas_str_series_max_length(curseries.astype(str))
                    result.append((PYWRITER_OBJECT, max_length, 0))
                    continue

            if curtype in int_types:
                result.append((PYWRITER_INTEGER, 0, is_missing))
            elif curtype in float_types:
                result.append((PYWRITER_DOUBLE, 0, is_missing))
            elif curtype == np.bool:
                result.append((PYWRITER_LOGICAL, 0, is_missing))
            elif curtype == str:
                max_length = get_pandas_str_series_max_length(curseries)
                result.append((PYWRITER_CHARACTER, max_length, is_missing))
            elif curtype == datetime.date:
                result.append((PYWRITER_DATE, 0, is_missing))
            elif curtype == datetime.datetime:
                result.append((PYWRITER_DATETIME, 0, is_missing))
            elif curtype == datetime.time:
                result.append((PYWRITER_TIME, 0, is_missing))
            else:
                max_length = get_pandas_str_series_max_length(curseries.astype(str))
                result.append((PYWRITER_OBJECT, max_length, is_missing))

        else:
            # generic object
            max_length = get_pandas_str_series_max_length(curseries.astype(str))
            is_missing = 0
            if np.any(pd.isna(curseries)):
                is_missing = 1
            result.append((PYWRITER_OBJECT, max_length, is_missing))
    return result

cdef readstat_label_set_t *set_value_label(readstat_writer_t *writer, dict value_labels, str labelset_name,
                        pywriter_variable_type curpytype, dst_file_format file_format, str variable_name, 
                        list user_missing_tags) except *:
    """
    Sets value labels for normal values and also tagged missing values (user defined missing for stata and sas)
    """

    cdef readstat_label_set_t *label_set
    cdef readstat_type_t curtype
    cdef double double_val
    
    curtype = pandas_to_readstat_types[curpytype]
    label_set = readstat_add_label_set(writer, curtype, labelset_name.encode("utf-8"))

    for value, label in value_labels.items():

        if type(label) != str:
            msg = "variable_value_labels: type of Label %s in variable %s must be string" % (str(label), variable_name)
            raise PyreadstatError(msg)

        if user_missing_tags and value in user_missing_tags:
            if curpytype == PYWRITER_CHARACTER or curpytype == PYWRITER_OBJECT:
                msg = "missing_user_values not allowed for character variable %s" % variable_name
                raise PyreadstatError(msg)
            
            readstat_label_tagged_value(label_set, ord(value), label.encode("utf-8"))
            continue


        if curpytype == PYWRITER_DOUBLE:
            if type(value) not in numeric_types:
                msg = "variable_value_labels: type of Value %s in variable %s must be numeric" % (str(value), variable_name)
                raise PyreadstatError(msg)
            readstat_label_double_value(label_set, value, label.encode("utf-8"))

        elif curpytype == PYWRITER_INTEGER:
            if type(value) not in int_types:
                msg = "variable_value_labels: type of Value %s in variable %s must be int" % (str(value), variable_name)
                raise PyreadstatError(msg)
            readstat_label_int32_value(label_set, value, label.encode("utf-8"))

        elif curpytype == PYWRITER_LOGICAL:
            if type(value) != bool and (value != 0 and value != 1):
                msg = "variable_value_labels: type of Value %s in variable %s must be boolean or be 1 or 0" % (str(value), variable_name)
                raise PyreadstatError(msg)
            readstat_label_int32_value(label_set, int(value), label.encode("utf-8"))

        elif curpytype == PYWRITER_CHARACTER or curpytype == PYWRITER_OBJECT:
            value = str(value)
            readstat_label_string_value(label_set, value.encode("utf-8"), label.encode("utf-8"))

        elif curpytype in (PYWRITER_DATE, PYWRITER_DATETIME, PYWRITER_TIME):
            if type(value) not in nat_types:
                msg = "variable_value_labels: type of Value %s in variable %s must match the type of the column in pandas and be of type date, datetime or time" % (str(value), variable_name)
                raise PyreadstatError(msg)
            double_val = convert_datetimelike_to_number(file_format, curpytype, value) 
            readstat_label_double_value(label_set, double_val, label.encode("utf-8"))

    return label_set

cdef void add_missing_ranges(list cur_ranges, readstat_variable_t *variable) except *:
    """
    Adding missing ranges, user defined missing discrete values both numeric and character,
     this happens for SPSS
    """

    cdef int range_values = 0
    cdef int discrete_values = 0
    cdef int discrete_strings = 0

    for cur_range in cur_ranges:
        if isinstance(cur_range, dict):
            hi = cur_range.get("hi")
            lo = cur_range.get("lo")
            if hi is None or lo is None:
                msg = "dictionaries in missing_ranges must have the keys hi and lo"
                raise PyreadstatError(msg)
            if type(hi) in numeric_types  and type(lo) in numeric_types:
                if hi == lo:
                    check_exit_status(readstat_variable_add_missing_double_value(variable, hi))
                    discrete_values += 1
                else:
                    check_exit_status(readstat_variable_add_missing_double_range(variable, lo, hi))
                    range_values += 1
            elif type(hi) == str and type(lo) == str:
                if hi == lo:
                    if len(hi) > 8:
                        msg = "missing_ranges: string values length must not be larger than 8"
                        raise PyreadstatError(msg)
                    check_exit_status(readstat_variable_add_missing_string_value(variable, hi.encode("utf-8")))
                    discrete_strings += 1
                else:
                    #check_exit_status(readstat_variable_add_missing_string_range(variable, lo, hi))
                    msg = "missing_ranges: hi and lo values must be both the same for string type"
                    raise PyreadstatError(msg)
            else:
                msg = "missing_ranges: hi and lo values must be both either of numeric or string type"
                raise PyreadstatError(msg)
        else:
            if type(cur_range) in numeric_types:
                check_exit_status(readstat_variable_add_missing_double_value(variable, cur_range))
                discrete_values += 1
            elif type(cur_range) == str:
                if len(cur_range) > 8:
                        msg = "missing_ranges: string values length must not be larger than 8"
                        raise PyreadstatError(msg)
                check_exit_status(readstat_variable_add_missing_string_value(variable, cur_range.encode("utf-8")))
                discrete_strings += 1
            else:
                msg = "missing_ranges: values must be both either of numeric or string type"
                raise PyreadstatError(msg)
               
        if discrete_strings > 3:
            msg = "missing_ranges: max 3 string values per variable allowed"
            raise PyreadstatError(msg)
        if range_values:
            if range_values > 1:
                msg = "missing_ranges: max 1 range value per variable allowed"
                raise PyreadstatError(msg)
            if discrete_values > 1:
                msg = "missing_ranges: max 1 discrete numeric value if combined with 1 range value per variable allowed"
                raise PyreadstatError(msg)
        if discrete_values >3:
            msg = "missing_ranges: max 3 discrete numeric values per variable allowed"
            raise PyreadstatError(msg)

cdef void set_variable_alignment(readstat_variable_t *variable, str alignment_str, str var_name) except *:
    """
    Sets the variable alignment, ineffective on SPSS, STATA and XPORT (what about SAS7bdat?)
    """

    cdef readstat_alignment_t alignment

    if alignment_str == "right":
        alignment = READSTAT_ALIGNMENT_RIGHT
    elif alignment_str == "left":
        alignment = READSTAT_ALIGNMENT_LEFT
    elif alignment_str == "center":
        alignment = READSTAT_ALIGNMENT_CENTER
    elif alignment_str == "unknown":
        alignment = READSTAT_ALIGNMENT_UNKNOWN
    else:
        msg = "alignment for variable %s must be either right, center, left or unknown got %s instead" % (var_name, alignment_str)
        raise PyreadstatError(msg)

    readstat_variable_set_alignment(variable, alignment)

cdef void set_variable_display_width(readstat_variable_t *variable, int display_width, str var_name) except *:
    """
    Sets the variable display width (SPSS). Not effective on STATA. (what about SAS7BDAT?)
    """

    readstat_variable_set_display_width(variable, display_width)

cdef void set_variable_measure(readstat_variable_t *variable, str measure_str, str var_name) except *:
    """
    sets the variable measure type (SPSS). Not effective on STATA.
    """

    cdef readstat_measure_t measure

    if measure_str == "nominal":
        measure = READSTAT_MEASURE_NOMINAL
    elif measure_str == "ordinal":
        measure = READSTAT_MEASURE_ORDINAL
    elif measure_str == "scale":
        measure = READSTAT_MEASURE_SCALE
    elif measure_str == "unknown":
        measure = READSTAT_MEASURE_UNKNOWN
    else:
        msg = "measure for variable %s must be either nominal, ordinal, scale or unknown got %s instead" % (var_name, measure_str)
        raise PyreadstatError(msg)

    readstat_variable_set_measure(variable, measure);


cdef ssize_t write_bytes(const void *data, size_t _len, void *ctx):
    """
    for the writer an explicit function to write must be defined 
    """
    cdef int fd
    fd = (<int *>ctx)[0]
    return write(fd, data, _len)

cdef void _check_exit_status(readstat_error_t retcode) except *:
    """
    transforms a readstat exit status to a python error if status is not READSTAT OK
    """

    cdef char * err_readstat
    cdef str err_message
    if retcode != READSTAT_OK:
        err_readstat = readstat_error_message(retcode)
        err_message = <str> err_readstat
        raise ReadstatError(err_message)

cdef int open_file(str filename_path):

    cdef int fd
    cdef int flags
    cdef Py_ssize_t length

    cdef bytes filename_bytes
    cdef char *path

    IF PY_MAJOR_VERSION >2:

        if os.name == "nt":
            u16_path = PyUnicode_AsWideCharString(filename_path, &length)
            flags = _O_WRONLY | _O_CREAT | _O_BINARY
            fd = _wsopen(u16_path, flags, _SH_DENYRD, 0)
        else:
            filename_bytes = filename_path.encode("utf-8")
            path = <char *> filename_bytes
            flags = O_WRONLY | O_CREAT | O_TRUNC
            fd = open(path, flags, 0644)

    ELSE:
        if os.name == "nt":
            return -1
        else:
            filename_bytes = filename_path.encode("utf-8")
            path = <char *> filename_bytes
            flags = O_WRONLY | O_CREAT | O_TRUNC
            fd = open(path, flags, 0644)

    return fd

cdef int close_file(int fd):
    if os.name == "nt":
        return _close(fd)
    else:
        return close(fd)

cdef int run_write(df, str filename_path, dst_file_format file_format, str file_label, list column_labels,
                   int file_format_version, str note, str table_name, dict variable_value_labels, 
                   dict missing_ranges, dict missing_user_values, dict variable_alignment,
                   dict variable_display_width, dict variable_measure) except *:
    """
    main entry point for writing all formats. Some parameters are specific for certain file type
    and are even incompatible between them. This function relies on the caller to select the right
    combination of parameters, not checking them otherwise.
    """

    IF PY_MAJOR_VERSION <3:
        if os.name == "nt":
            raise PyreadstatError("Writing API not supported on python 2 on windows")

    if not isinstance(df, pd.DataFrame):
        raise PyreadstatError("first argument must be a pandas data frame")

    if variable_value_labels:
        for k,v in variable_value_labels.items():
            if type(v) != dict:
                msg = "variable_value_labels: value for key %s must be dict, got %s" % (k, str(type(v)))
                raise PyreadstatError(msg)

    if missing_user_values:
        if file_format == FILE_FORMAT_DTA:
            valid_user_missing = valid_user_missing_stata
        elif file_format == FILE_FORMAT_SAS7BDAT or file_format == FILE_FORMAT_SAS7BCAT:
            valid_user_missing = valid_user_missing_sas
        for key, missing_values in missing_user_values.items():
            if not isinstance(missing_values, list):
                msg = "missing_user_values: values in dictionary must be list"
                raise PyreadstatError(msg)
            for val in missing_values:
                if val not in valid_user_missing:
                    msg = "missing_user_values supports values a to z for Stata and A to Z and _ for SAS, got %s instead" % str(val)
                    raise PyreadstatError(msg)

    cdef readstat_error_t retcode
    cdef char *err_readstat
    cdef str err_message

    cdef readstat_writer_t *writer

    cdef bytes file_label_bytes
    cdef char *file_labl

    cdef list col_names = df.columns.values.tolist()
    if file_format == FILE_FORMAT_POR:
        col_names = [x.upper() for x in col_names]
    cdef list col_types = get_pandas_column_types(df, missing_user_values)
    cdef int row_count = len(df)
    cdef int col_count = len(col_names)
    cdef dict col_names_to_types = {k:v[0] for k,v in zip(col_names, col_types)}

    cdef readstat_variable_t *variable
    cdef pywriter_variable_type curtype
    cdef int max_length
    cdef char *curformat
    cdef int col_indx
    cdef bytes cur_col_label
    cdef int col_label_count = 0

    cdef readstat_variable_t *tempvar
    cdef int row_indx
    cdef str curvalstr
    cdef double dtimelikeval
    #cdef np.ndarray values
    cdef object values
    cdef dict value_labels
    cdef int lblset_cnt = 0
    cdef readstat_label_set_t *label_set

    filename_path = os.path.expanduser(filename_path)
    cdef int fd = open_file(filename_path)
    writer = readstat_writer_init()

    try:

        check_exit_status(readstat_set_data_writer(writer, write_bytes))

        if file_label:
            file_label_bytes = file_label.encode("utf-8")
            file_labl = <char *> file_label_bytes
            check_exit_status(readstat_writer_set_file_label(writer, file_labl))

        if note:
            readstat_add_note(writer, note.encode("utf-8"))

        if file_format_version > -1:
            check_exit_status(readstat_writer_set_file_format_version(writer, file_format_version))

        # table name is used only for xpt files
        if table_name:
            table_name_bytes = table_name.encode("utf-8")
            tab_name = <char *> table_name_bytes
            check_exit_status(readstat_writer_set_table_name(writer, tab_name))

        # add variables
        if column_labels:
            col_label_count = len(column_labels)
            if col_label_count != col_count:
                raise PyreadstatError("length of column labels must be the same as number of columns")
     
        for col_indx in range(col_count):
            curtype, max_length, _ = col_types[col_indx]
            #if file_format == FILE_FORMAT_XPORT and curtype == PYWRITER_DOUBLE:
            #    max_length = 8
            variable_name = col_names[col_indx]
            variable = readstat_add_variable(writer, variable_name.encode("utf-8"), pandas_to_readstat_types[curtype], max_length)
            if curtype in pyrwriter_datetimelike_types:
                curformat = get_datetimelike_format_for_readstat(file_format, curtype)
                readstat_variable_set_format(variable, curformat)
            if col_label_count:
                if column_labels[col_indx] is not None:
                    if type(column_labels[col_indx]) != str:
                        raise PyreadstatError("Column labels must be strings")
                    cur_col_label = column_labels[col_indx].encode("utf-8")
                    readstat_variable_set_label(variable, cur_col_label)
            if variable_value_labels:
                value_labels = variable_value_labels.get(variable_name)
                if value_labels:
                    labelset_name = variable_name + str(lblset_cnt)
                    lblset_cnt += 1
                    curuser_missing = None
                    if missing_user_values:
                        curuser_missing = missing_user_values.get(variable_name)
                    label_set = set_value_label(writer, value_labels, labelset_name,
                        col_names_to_types[variable_name], file_format, variable_name, curuser_missing)
                    readstat_variable_set_label_set(variable, label_set)
                if missing_ranges:
                    cur_ranges = missing_ranges.get(variable_name)
                    if cur_ranges:
                        if not isinstance(cur_ranges, list):
                            msg = "missing_ranges: values in dictionary must be list"
                            raise PyreadstatError(msg)
                        add_missing_ranges(cur_ranges, variable)
                if variable_alignment:
                    # At the moment this is ineffective for sav and dta (the function runs but in
                    # the resulting file all alignments are still unknown)
                    cur_alignment = variable_alignment.get(variable_name)
                    if cur_alignment:
                        set_variable_alignment(variable, cur_alignment, variable_name)
                if variable_display_width:
                    cur_display_width = variable_display_width.get(variable_name)
                    if cur_display_width:
                        set_variable_display_width(variable, cur_display_width, variable_name)
                if variable_measure:
                    cur_measure = variable_measure.get(variable_name)
                    if cur_measure:
                        set_variable_measure(variable, cur_measure, variable_name)

        # start writing
        if file_format == FILE_FORMAT_SAS7BCAT:
            check_exit_status(readstat_begin_writing_sas7bcat(writer, &fd))
        elif file_format == FILE_FORMAT_DTA:
            check_exit_status(readstat_begin_writing_dta(writer, &fd, row_count))
        elif file_format == FILE_FORMAT_SAV:
            check_exit_status(readstat_begin_writing_sav(writer, &fd, row_count))
        elif file_format == FILE_FORMAT_POR:
            check_exit_status(readstat_begin_writing_por(writer, &fd, row_count))
        elif file_format == FILE_FORMAT_SAS7BDAT:
            check_exit_status(readstat_begin_writing_sas7bdat(writer, &fd, row_count))
        elif file_format == FILE_FORMAT_XPORT:
            check_exit_status(readstat_begin_writing_xport(writer, &fd, row_count))
        else:
            raise PyreadstatError("unknown file format")

        # validation
        check_exit_status(readstat_validate_metadata(writer))
        for col_indx in range(col_count):
            tempvar = readstat_get_variable(writer, col_indx)
            check_exit_status(readstat_validate_variable(writer, tempvar))

        # inserting
        values = df.values

        for  row in values:
            check_exit_status(readstat_begin_row(writer))

            for col_indx in range(col_count):

                tempvar = readstat_get_variable(writer, col_indx)
                curval = row[col_indx]
                curtype = col_types[col_indx][0]
                is_missing = col_types[col_indx][2]
                curuser_missing = None
                if missing_user_values:
                    curuser_missing = missing_user_values.get(col_names[col_indx])

                if is_missing:
                    if curval is None or (type(curval) in numeric_types and np.isnan(curval)):
                        check_exit_status(readstat_insert_missing_value(writer, tempvar))
                        continue

                if curuser_missing and curtype in pywriter_numeric_types:
                    if curval in curuser_missing:
                        check_exit_status(readstat_insert_tagged_missing_value(writer, tempvar, ord(curval)))
                        continue

                if curtype == PYWRITER_DOUBLE:
                    check_exit_status(readstat_insert_double_value(writer, tempvar, <double>curval))
                elif curtype == PYWRITER_INTEGER:
                    check_exit_status(readstat_insert_int32_value(writer, tempvar, curval))
                elif curtype == PYWRITER_LOGICAL:
                    check_exit_status(readstat_insert_int32_value(writer, tempvar, <int>curval))
                elif curtype == PYWRITER_CHARACTER:
                    check_exit_status(readstat_insert_string_value(writer, tempvar, curval.encode("utf-8")))
                elif curtype == PYWRITER_OBJECT:
                    curvalstr = str(curval)
                    check_exit_status(readstat_insert_string_value(writer, tempvar, curvalstr.encode("utf-8")))
                elif curtype in pyrwriter_datetimelike_types:
                    dtimelikeval = convert_datetimelike_to_number(file_format, curtype, curval)
                    check_exit_status(readstat_insert_double_value(writer, tempvar, dtimelikeval))
                else:
                    raise PyreadstatError("Unknown data format to insert")

            check_exit_status(readstat_end_row(writer))

        check_exit_status(readstat_end_writing(writer))

    except:
        raise
    finally:
        readstat_writer_free(writer)
        close_file(fd)

    return 0
