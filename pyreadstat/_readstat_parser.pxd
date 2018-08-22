        
from readstat_api cimport *

# Definitions of enum types

ctypedef enum py_file_format:
    FILE_FORMAT_SAS
    FILE_FORMAT_SPSS
    FILE_FORMAT_STATA
    
ctypedef enum py_datetime_format:
    DATE_FORMAT_NOTADATE
    DATE_FORMAT_DATE
    DATE_FORMAT_DATETIME
    DATE_FORMAT_TIME
    
ctypedef enum py_variable_format:
    VAR_FORMAT_STRING
    VAR_FORMAT_LONG
    VAR_FORMAT_FLOAT
    VAR_FORMAT_MISSING
    
# Definitions of extension types
    
cdef class data_container:
    """
    This extension type holds all the data we need to get from our file from 
    the readstat parser and will be used later to compose our pandas data frame
    """
    cdef int n_obs
    cdef int n_vars
    cdef int max_n_obs
    cdef list col_data
    cdef list col_data_len
    cdef list col_names
    cdef list col_labels
    cdef list col_dtypes
    cdef list col_formats
    cdef list col_formats_original
    cdef object origin
    cdef py_file_format file_format
    cdef bint is_unkown_number_rows
    cdef str file_label
    cdef str file_encoding
    cdef bint metaonly
    cdef bint dates_as_pandas
    cdef object label_to_var_name
    cdef object labels_raw
    cdef object notes
    cdef str user_encoding
    cdef str table_name
    

# definitions of functions
cdef py_datetime_format transform_variable_format(str var_format, py_file_format file_format)
cdef object transform_datetime(py_datetime_format var_format, double tstamp, py_file_format file_format, object origin, bint dates_as_pandas)

cdef int handle_metadata(readstat_metadata_t *metadata, void *ctx) except READSTAT_HANDLER_ABORT
cdef int handle_variable(int index, readstat_variable_t *variable, 
                         char *val_labels, void *ctx) except READSTAT_HANDLER_ABORT
cdef int handle_value(int obs_index, readstat_variable_t * variable, readstat_value_t value, void *ctx) except READSTAT_HANDLER_ABORT
cdef int handle_value_label(char *val_labels, readstat_value_t value, char *label, void *ctx) except READSTAT_HANDLER_ABORT
cdef int handle_note (int note_index, char *note, void *ctx) except READSTAT_HANDLER_ABORT

cdef void run_readstat_parser(char * filename, data_container data, readstat_error_t parse_func(readstat_parser_t *parse, const char *, void *)) except *
cdef object data_container_to_pandas_dataframe(data_container data)
cdef object data_container_extract_metadata(data_container data)
cdef object run_conversion(str filename_path, py_file_format file_format, readstat_error_t parse_func(readstat_parser_t *parse, const char *, void *),
                           str encoding, bint metaonly, bint dates_as_pandas)

# definitions for stuff about dates
cdef list sas_date_formats 
cdef list sas_datetime_formats 
cdef list sas_time_formats 
cdef list sas_all_formats 
cdef object sas_origin

cdef list spss_datetime_formats 
cdef list spss_date_formats 
cdef list spss_time_formats 
cdef list spss_all_formats 
cdef object spss_origin

cdef list stata_datetime_formats
cdef list stata_date_formats
cdef list stata_time_formats 
cdef list stata_all_formats 
cdef object stata_origin
    