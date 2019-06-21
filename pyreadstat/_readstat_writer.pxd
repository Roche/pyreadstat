from readstat_api cimport *
#cdef int write_test()

cdef extern from "readstat_io_unistd.h":
    cdef struct unistd_io_ctx_t "unistd_io_ctx_s":
        pass

cdef extern from "conditional_includes.h":
    int O_RDONLY
    int O_BINARY
    int O_WRONLY
    int O_CREAT
    int O_TRUNC
    int open(const char *path, int oflag, int mode)

cdef int run_write(df, str filename_path, dst_file_format file_format, str file_label) except *

ctypedef enum dst_file_format:
    FILE_FORMAT_SAS7BDAT
    FILE_FORMAT_SAS7BCAT
    FILE_FORMAT_XPORT
    FILE_FORMAT_SAV
    FILE_FORMAT_DTA
    FILE_FORMAT_POR

ctypedef enum pywriter_variable_type:
    PYWRITER_DOUBLE
    PYWRITER_INTEGER
    PYWRITER_CHARACTER
    PYWRITER_LOGICAL
    PYWRITER_OBJECT
    PYWRITER_DATE
    PYWRITER_DATETIME
    PYWRITER_DATETIMENS
    PYWRITER_TIME