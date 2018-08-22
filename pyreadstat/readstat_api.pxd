"""
These are C definitions coming from the readstat API (readstat.h) plus some
dependecies of that to the C standard library
"""

cdef extern from "<stdint.h>" nogil:

    # 7.18.1 Integer types
    # 7.18.1.1 Exact-width integer types
    ctypedef   signed char  int8_t
    ctypedef   signed short int16_t
    ctypedef   signed int   int32_t
    ctypedef   signed long  int64_t
    

cdef extern from "readstat.h":

    ctypedef enum:
        READSTAT_HANDLER_OK,
        READSTAT_HANDLER_ABORT,
        READSTAT_HANDLER_SKIP_VARIABLE

    ctypedef struct readstat_variable_t:
        int index

    ctypedef struct readstat_label_set_t:
        pass
        
    ctypedef struct readstat_metadata_t:
        pass
    
    ctypedef enum readstat_error_t:
        READSTAT_OK,
        READSTAT_ERROR_OPEN = 1,
        READSTAT_ERROR_READ,
        READSTAT_ERROR_MALLOC,
        READSTAT_ERROR_USER_ABORT,
        READSTAT_ERROR_PARSE,
        READSTAT_ERROR_UNSUPPORTED_COMPRESSION,
        READSTAT_ERROR_UNSUPPORTED_CHARSET,
        READSTAT_ERROR_COLUMN_COUNT_MISMATCH,
        READSTAT_ERROR_ROW_COUNT_MISMATCH,
        READSTAT_ERROR_ROW_WIDTH_MISMATCH,
        READSTAT_ERROR_BAD_FORMAT_STRING,
        READSTAT_ERROR_VALUE_TYPE_MISMATCH,
        READSTAT_ERROR_WRITE,
        READSTAT_ERROR_WRITER_NOT_INITIALIZED,
        READSTAT_ERROR_SEEK,
        READSTAT_ERROR_CONVERT,
        READSTAT_ERROR_CONVERT_BAD_STRING,
        READSTAT_ERROR_CONVERT_SHORT_STRING,
        READSTAT_ERROR_CONVERT_LONG_STRING,
        READSTAT_ERROR_NUMERIC_VALUE_IS_OUT_OF_RANGE,
        READSTAT_ERROR_TAGGED_VALUE_IS_OUT_OF_RANGE,
        READSTAT_ERROR_STRING_VALUE_IS_TOO_LONG,
        READSTAT_ERROR_TAGGED_VALUES_NOT_SUPPORTED,
        READSTAT_ERROR_UNSUPPORTED_FILE_FORMAT_VERSION,
        READSTAT_ERROR_NAME_BEGINS_WITH_ILLEGAL_CHARACTER,
        READSTAT_ERROR_NAME_CONTAINS_ILLEGAL_CHARACTER,
        READSTAT_ERROR_NAME_IS_RESERVED_WORD,
        READSTAT_ERROR_NAME_IS_TOO_LONG,
        READSTAT_ERROR_BAD_TIMESTAMP,
        READSTAT_ERROR_BAD_FREQUENCY_WEIGHT,
        READSTAT_ERROR_TOO_MANY_MISSING_VALUE_DEFINITIONS,
        READSTAT_ERROR_NOTE_IS_TOO_LONG,
        READSTAT_ERROR_STRING_REFS_NOT_SUPPORTED,
        READSTAT_ERROR_STRING_REF_IS_REQUIRED,
        READSTAT_ERROR_ROW_IS_TOO_WIDE_FOR_PAGE
        
    ctypedef enum readstat_type_t:
        READSTAT_TYPE_STRING,
        READSTAT_TYPE_INT8,
        READSTAT_TYPE_INT16,
        READSTAT_TYPE_INT32,
        READSTAT_TYPE_FLOAT,
        READSTAT_TYPE_DOUBLE,
        READSTAT_TYPE_STRING_REF
        
    ctypedef struct readstat_value_t:
        pass
    
    ctypedef struct readstat_parser_t:
        pass
    
    cdef readstat_parser_t *readstat_parser_init()
    cdef void readstat_parser_free(readstat_parser_t *parser)

    ctypedef int (*readstat_metadata_handler)(readstat_metadata_t *metadata, void *ctx);
    ctypedef int (*readstat_variable_handler)(int index, readstat_variable_t *variable, char *val_labels, void *ctx);
    ctypedef int (*readstat_value_handler)(int obs_index, readstat_variable_t *variable, readstat_value_t value, void *ctx);
    ctypedef int (*readstat_value_label_handler)(const char *val_labels, readstat_value_t value, const char *label, void *ctx);
    ctypedef int (*readstat_note_handler)(int note_index, const char *note, void *ctx);

    cdef readstat_error_t readstat_set_metadata_handler(readstat_parser_t *parser, readstat_metadata_handler metadata_handler);
    cdef readstat_error_t readstat_set_note_handler(readstat_parser_t *parser, readstat_note_handler note_handler);
    cdef readstat_error_t readstat_set_variable_handler(readstat_parser_t *parser, readstat_variable_handler variable_handler)
    cdef readstat_error_t readstat_set_value_handler(readstat_parser_t *parser, readstat_value_handler value_handler);
    cdef readstat_error_t readstat_set_value_label_handler(readstat_parser_t *parser, readstat_value_label_handler value_label_handler);

    cdef readstat_error_t readstat_set_file_character_encoding(readstat_parser_t *parser, const char *encoding);
    
    cdef  int readstat_get_row_count(readstat_metadata_t *metadata);
    cdef int readstat_get_var_count(readstat_metadata_t *metadata);
    cdef char *readstat_get_file_label(readstat_metadata_t *metadata);
    cdef char *readstat_get_file_encoding(readstat_metadata_t *metadata);
    cdef char *readstat_get_table_name(readstat_metadata_t *metadata);
    
    cdef char *readstat_variable_get_name(readstat_variable_t *variable)
    cdef char *readstat_variable_get_label(readstat_variable_t *variable)
    cdef char *readstat_variable_get_format(readstat_variable_t *variable)
    readstat_type_t readstat_variable_get_type(const readstat_variable_t *variable);
    
    cdef int readstat_value_is_missing(readstat_value_t value, readstat_variable_t *variable);
    cdef readstat_type_t readstat_value_type(readstat_value_t value);
    
    cdef readstat_error_t readstat_parse_dta(readstat_parser_t *parser, const char *path, void *user_ctx);
    cdef readstat_error_t readstat_parse_sav(readstat_parser_t *parser, const char *path, void *user_ctx);
    cdef readstat_error_t readstat_parse_por(readstat_parser_t *parser, const char *path, void *user_ctx);
    cdef readstat_error_t readstat_parse_sas7bdat(readstat_parser_t *parser, const char *path, void *user_ctx);
    cdef readstat_error_t readstat_parse_sas7bcat(readstat_parser_t *parser, const char *path, void *user_ctx);
    cdef readstat_error_t readstat_parse_xport(readstat_parser_t *parser, const char *path, void *user_ctx);
    
    char *readstat_string_value(readstat_value_t value);
    char readstat_int8_value(readstat_value_t value);
    int16_t readstat_int16_value(readstat_value_t value);
    int32_t readstat_int32_value(readstat_value_t value);
    float readstat_float_value(readstat_value_t value);
    double readstat_double_value(readstat_value_t value);

    char *readstat_error_message(readstat_error_t error_code);