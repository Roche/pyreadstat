#ifndef READSTAT_PARSE_MR_NAME_H
#define READSTAT_PARSE_MR_NAME_H

#include "readstat.h"

readstat_error_t parse_mr_string(const char *line, mr_set_t **mr_sets, int *n_mr_lines);

#endif // READSTAT_PARSE_MR_NAME_H