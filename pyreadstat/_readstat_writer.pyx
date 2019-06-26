# cython: c_string_type=unicode, c_string_encoding=utf8, language_level=2
# cython: profile=True
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

import numpy as np
#cimport numpy as np
import pandas as pd
import datetime
try:
    from datetime import timezone
except: # not available on python 2
    pass
from libc.math cimport round


cdef set int_types = {int, np.dtype('int32'), np.dtype('int16'), np.dtype('int8'), np.dtype('uint8'), np.dtype('uint16'),
             np.int32, np.int16, np.int8, np.uint8, np.uint16}
cdef set float_types = {float, np.dtype('int64'), np.dtype('uint64'), np.dtype('uint32'), np.dtype('float'),
               np.int64, np.uint64, np.uint32, np.float}
cdef set numeric_types = int_types.union(float_types)
cdef set datetime_types = {datetime.datetime, np.datetime64, pd._libs.tslibs.timestamps.Timestamp}
cdef set nat_types = {datetime.datetime, np.datetime64, pd._libs.tslibs.timestamps.Timestamp, datetime.time, datetime.date}
cdef set pyrwriter_datetimelike_types = {PYWRITER_DATE, PYWRITER_DATETIME, PYWRITER_TIME}



cdef dict pandas_to_readstat_types = {PYWRITER_DOUBLE: READSTAT_TYPE_DOUBLE, PYWRITER_INTEGER: READSTAT_TYPE_INT32,
                                      PYWRITER_CHARACTER: READSTAT_TYPE_STRING, PYWRITER_LOGICAL: READSTAT_TYPE_INT32,
                                      PYWRITER_OBJECT: READSTAT_TYPE_STRING, PYWRITER_DATE: READSTAT_TYPE_DOUBLE,
                                      PYWRITER_DATETIME: READSTAT_TYPE_DOUBLE, #PYWRITER_DATETIMENS: READSTAT_TYPE_DOUBLE,
                                      PYWRITER_TIME: READSTAT_TYPE_DOUBLE}

#cdef double spss_offset_secs = -1 * (datetime.datetime(1582, 10, 14, 0, 0, 0, 0, tzinfo=timezone.utc).timestamp())
cdef double spss_offset_secs = 12219379200
#cdef double sas_offset_secs = -1 * (datetime.datetime(1960, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc).timestamp())
cdef double sas_offset_secs = 315619200
cdef double spss_offset_days = 141428
cdef double sas_offset_days = 3653
cdef object date_0 = datetime.datetime(1970,1,1).date()


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
            tstamp = curval.replace(tzinfo=timezone.utc).timestamp()
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


cdef list get_pandas_column_types(object df):
    """
    From a pandas data frame, get a list with tuples column types as first element, max_length as second
    max_lenght is the max length of a string or string representation of an object, 0 for numeric types
    """

    cdef int max_length

    cdef list types = df.dtypes.values.tolist()
    cdef list columns = df.columns.values.tolist()

    cdef list result = list()
    cdef int equal

    for indx, (col_name, col_type) in enumerate(zip(columns, types)):

        max_length = 0
        curseries = df.iloc[:, indx]

        # recover original type for categories
        if type(col_type) is pd.core.dtypes.dtypes.CategoricalDtype:
            col_type = np.asarray(curseries).dtype
        if col_type in int_types:
            result.append((PYWRITER_INTEGER, 0))
        elif col_type in float_types:
            result.append((PYWRITER_DOUBLE, 0))
        elif col_type == np.bool:
            result.append((PYWRITER_LOGICAL, 0))
        # np.datetime64[ns]
        elif col_type == np.dtype('<M8[ns]') or col_type in datetime_types:
            result.append((PYWRITER_DATETIME, 0))
        elif col_type == np.object:
            #missing = pd.isna(curseries)
            if np.any(pd.isna(curseries)):
                col = curseries.dropna().reset_index(drop=True)

                if len(col):
                    curtype = type(col[0])
                    equal = check_series_all_same_types(col, curtype)
                    #equal = col.apply(lambda x: type(x) == curtype)
                    #if not np.all(equal):
                    if not equal:
                        max_length = get_pandas_str_series_max_length(col.astype(str))
                        result.append((PYWRITER_OBJECT, max_length))
                        continue
                else:
                    result.append((PYWRITER_LOGICAL, 0))
                    continue
            else:
                curtype = type(curseries[0])
                equal = check_series_all_same_types(curseries, curtype)
                #equal = curseries.apply(lambda x: type(x) == curtype)
                #if not np.all(equal):
                if not equal:
                    max_length = get_pandas_str_series_max_length(curseries.astype(str))
                    result.append((PYWRITER_OBJECT, max_length))
                    continue

            if curtype in int_types:
                result.append((PYWRITER_INTEGER, 0))
            elif curtype in float_types:
                result.append((PYWRITER_DOUBLE, 0))
            elif curtype == np.bool:
                result.append((PYWRITER_LOGICAL, 0))
            elif curtype == str:
                max_length = get_pandas_str_series_max_length(curseries)
                result.append((PYWRITER_CHARACTER, max_length))
            elif curtype == datetime.date:
                result.append((PYWRITER_DATE, 0))
            elif curtype == datetime.datetime:
                result.append((PYWRITER_DATETIME, 0))
            elif curtype == datetime.time:
                result.append((PYWRITER_TIME, 0))
            else:
                max_length = get_pandas_str_series_max_length(curseries.astype(str))
                result.append((PYWRITER_OBJECT, max_length))

        else:
            # generic object
            max_length = get_pandas_str_series_max_length(curseries.astype(str))
            result.append((PYWRITER_OBJECT, max_length))
    return result


cdef ssize_t write_bytes(const void *data, size_t _len, void *ctx):
    """
    for the writer an explicit function to write must be defined 
    """
    cdef int fd
    fd = (<int *>ctx)[0]
    return write(fd, data, _len)

cdef void check_exit_status(readstat_error_t retcode) except *:
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
        return -1
        # if os.name == "nt":
        #     return -1
        # else:
        #     filename_bytes = filename_path.encode("utf-8")
        #     path = <char *> filename_bytes
        #     flags = O_WRONLY | O_CREAT | O_TRUNC
        #     fd = open(path, flags, 0644)

    return fd

cdef int close_file(int fd):
    if os.name == "nt":
        return _close(fd)
    else:
        return close(fd)

from time import time

cdef int run_write(df, str filename_path, dst_file_format file_format, str file_label, list column_labels,
                   int file_format_version, str note, str table_name) except *:
    """
    main entry point for writing all formats
    """

    IF PY_MAJOR_VERSION <3:
        #if os.name == "nt":
        raise PyreadstatError("Python 2 writing API not supported on python 2")

    cdef readstat_error_t retcode
    cdef char *err_readstat
    cdef str err_message

    cdef readstat_writer_t *writer

    cdef bytes file_label_bytes
    cdef char *file_labl

    cdef list col_names = df.columns.values.tolist()
    cdef list col_types = get_pandas_column_types(df)
    cdef int row_count = len(df)
    cdef int col_count = len(col_names)

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

    # cdef bytes filename_bytes = filename_path.encode("utf-8")
    # cdef char *path = <char *> filename_bytes
    # cdef int flags = O_WRONLY | O_CREAT | O_TRUNC
    # if os.name == "nt":
    #     flags = _O_WRONLY | _O_CREAT | _O_BINARY
    # cdef int fd = open(path, flags, 0644)
    cdef int fd = open_file(filename_path)
    #t0 = time()
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
        #print("setup", time()-t0)
        #t0 = time()
        for col_indx in range(col_count):
            curtype, max_length = col_types[col_indx]
            #if file_format == FILE_FORMAT_XPORT and curtype == PYWRITER_DOUBLE:
            #    max_length = 8
            variable = readstat_add_variable(writer, col_names[col_indx].encode("utf-8"), pandas_to_readstat_types[curtype], max_length)
            if curtype in pyrwriter_datetimelike_types:
                curformat = get_datetimelike_format_for_readstat(file_format, curtype)
                readstat_variable_set_format(variable, curformat)
            if col_label_count:
                if column_labels[col_indx] is not None:
                    if type(column_labels[col_indx]) != str:
                        raise PyreadstatError("Column labels must be strings")
                    cur_col_label = column_labels[col_indx].encode("utf-8")
                    readstat_variable_set_label(variable, cur_col_label)
        #print("add variables", time()-t0)
        #t0 = time()
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
        #print("start writing", time()-t0)
        #t0 = time()
        # inserting
        values = df.values
        #print("converting values", time()-t0)
        #t0 = time()
        for  row in values:
            check_exit_status(readstat_begin_row(writer))

            for col_indx in range(col_count):

                tempvar = readstat_get_variable(writer, col_indx)
                curval = row[col_indx]

                if curval is None or (type(curval) in numeric_types and np.isnan(curval)):
                    check_exit_status(readstat_insert_missing_value(writer, tempvar))
                    continue
                curtype = col_types[col_indx][0]

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
        #print("inserting", time()-t0)

    except:
        raise
    finally:
        #t0 = time()
        readstat_writer_free(writer)
        #close(fd)
        close_file(fd)
        #print("cleaning", time()-t0)

    return 0
