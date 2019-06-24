import os
from readstat_api cimport *
from _readstat_parser import ReadstatError, PyreadstatError

import numpy as np
import pandas as pd
import datetime
from datetime import timezone


cdef set int_types = {int, np.dtype('int32'), np.dtype('int16'), np.dtype('int8'), np.dtype('uint8'), np.dtype('uint16'),
             np.int32, np.int16, np.int8, np.uint8, np.uint16}
cdef set float_types = {float, np.dtype('int64'), np.dtype('uint64'), np.dtype('uint32'), np.dtype('float'),
               np.int64, np.uint64, np.uint32, np.float}
cdef set numeric_types = int_types.union(float_types)
cdef set datetime_types = {datetime.datetime, np.datetime64, pd._libs.tslibs.timestamps.Timestamp}
cdef set pyrwriter_datetimelike_types = {PYWRITER_DATE, PYWRITER_DATETIME, PYWRITER_TIME}

min_32_integer = -2147483648

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
                tstamp = curval.astype(float)/1e9
            elif curval.dtype.name == "datetime64[us]":
                tstamp = curval.astype(float)/1e6
            elif curval.dtype.name == "datetime64[ms]":
                tstamp = curval.astype(float)/1e3

        tstamp += offset_secs
        if file_format == FILE_FORMAT_DTA:
            # stata stores in milliseconds
            tstamp *= 1000

    elif curtype == PYWRITER_DATE:
        if type(curval) == datetime.date:
            days = curval - datetime.datetime(1970,1,1).date()
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
    return int(series.str.encode(encoding="utf-8").str.len().max())

cdef list get_pandas_column_types(object df):
    """
    From a pandas data frame, get a list with tuples column types as first element, max_length as second
    max_lenght is the max length of a string or string representation of an object, 0 for numeric types
    """

    cdef int max_length

    cdef list types = df.dtypes.values.tolist()
    cdef list columns = df.columns.values.tolist()

    cdef list result = list()

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
            missing = pd.isna(curseries)
            if np.any(missing):
                col = curseries.dropna().reset_index(drop=True)

                if len(col):
                    curtype = type(col[0])
                    equal = col.apply(lambda x: type(x) == curtype)
                    if not np.all(equal):
                        max_length = get_pandas_str_series_max_length(col.astype(str))
                        result.append((PYWRITER_OBJECT, max_length))
                        continue
                else:
                    result.append((PYWRITER_LOGICAL, 0))
                    continue
            else:
                curtype = type(curseries[0])
                equal = curseries.apply(lambda x: type(x) == curtype)
                if not np.all(equal):
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


cdef ssize_t write_bytes(const void *data, size_t len, void *ctx):
    """
    for the writer an explicit function to write must be defined 
    """
    cdef int fd
    fd = (<int *>ctx)[0]
    return write(fd, data, len)

cdef int run_write(df, str filename_path, dst_file_format file_format, str file_label, list column_labels,
                   int file_format_version, str note) except *:

    cdef bytes filename_bytes
    cdef char * filename

    filename_bytes = filename_path.encode("utf-8")
    filename = <char *> filename_bytes

    IF PY_MAJOR_VERSION <3:
        if os.name == "nt":
            raise PyreadstatError("Python 2 not supported on windows")

    cdef readstat_writer_t *writer


    writer = readstat_writer_init()
    readstat_set_data_writer(writer, write_bytes)

    cdef bytes file_label_bytes
    cdef char *file_labl
    if file_label:
        file_label_bytes = file_label.encode("utf-8")
        file_labl = <char *> file_label_bytes
        readstat_writer_set_file_label(writer, file_labl)

    if note:
        readstat_add_note(writer, note.encode("utf-8"))

    if file_format_version > -1:
        readstat_writer_set_file_format_version(writer, file_format_version)

    # add variables
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
    if column_labels:
        col_label_count = len(column_labels)
        if col_label_count != col_count:
            raise PyreadstatError("length of column labels must be the same as number of columns")

    for col_indx in range(col_count):
        curtype, max_length = col_types[col_indx]
        #if file_format == FILE_FORMAT_XPORT and curtype == PYWRITER_DOUBLE:
        #    max_length = 8
        #    print(curtype, max_length)
        variable = readstat_add_variable(writer, col_names[col_indx].encode("utf-8"), pandas_to_readstat_types[curtype], max_length)
        if curtype in pyrwriter_datetimelike_types:
            curformat = get_datetimelike_format_for_readstat(file_format, curtype)
            readstat_variable_set_format(variable, curformat)
        if col_label_count:
            cur_col_label = column_labels[col_indx].encode("utf-8")
            readstat_variable_set_label(variable, cur_col_label)
        #readstat_variable_set_label(variable, "First variable")


    flags = O_WRONLY | O_CREAT | O_TRUNC

    cdef char *path = filename
    cdef int fd = open(path, flags, 0644)

    if file_format == FILE_FORMAT_SAS7BCAT:
        readstat_begin_writing_sas7bcat(writer, &fd)
    elif file_format == FILE_FORMAT_DTA:
        readstat_begin_writing_dta(writer, &fd, row_count)
    elif file_format == FILE_FORMAT_SAV:
        readstat_begin_writing_sav(writer, &fd, row_count)
    elif file_format == FILE_FORMAT_POR:
        readstat_begin_writing_por(writer, &fd, row_count)
    elif file_format == FILE_FORMAT_SAS7BDAT:
        readstat_begin_writing_sas7bdat(writer, &fd, row_count)
    elif file_format == FILE_FORMAT_XPORT:
        readstat_begin_writing_xport(writer, &fd, row_count)
    else:
        raise PyreadstatError("unknown file format")

    cdef readstat_variable_t *tempvar
    cdef int row_indx
    cdef str curvalstr
    cdef double dtimelikeval

    #for row_indx in range(row_count):
    for row_indx, row in df.iterrows():
        readstat_begin_row(writer);
        for col_indx in range(col_count):

            tempvar = readstat_get_variable(writer, col_indx)
            curval = row[col_indx]

            if curval is None or (type(curval) in numeric_types and np.isnan(curval)):
                readstat_insert_missing_value(writer, tempvar)
                continue
            curtype = col_types[col_indx][0]

            if curtype == PYWRITER_DOUBLE:
                readstat_insert_double_value(writer, tempvar, <double>curval)
            elif curtype == PYWRITER_INTEGER:
                readstat_insert_int32_value(writer, tempvar, curval)
            elif curtype == PYWRITER_LOGICAL:
                readstat_insert_int32_value(writer, tempvar, <int>curval)
            elif curtype == PYWRITER_CHARACTER:
                readstat_insert_string_value(writer, tempvar, curval.encode("utf-8"))
            elif curtype == PYWRITER_OBJECT:
                curvalstr = str(curval)
                readstat_insert_string_value(writer, tempvar, curvalstr.encode("utf-8"))
            elif curtype in pyrwriter_datetimelike_types:
                dtimelikeval = convert_datetimelike_to_number(file_format, curtype, curval)
                readstat_insert_double_value(writer, tempvar, dtimelikeval)
            else:
                raise PyreadstatError("Unknown data format to insert")

        readstat_end_row(writer);

    readstat_end_writing(writer)
    readstat_writer_free(writer)
    close(fd)

    return 0
