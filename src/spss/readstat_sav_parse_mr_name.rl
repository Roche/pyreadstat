#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "readstat.h"

%%{
    machine mr_name_and_label;

    action extract_mr_name {
        mr_name = (char *)malloc(p - start + 1);
        memcpy(mr_name, start, p - start);
        mr_name[p - start] = '\0';
    }

    action extract_mr_type {
        mr_type = *p;
        start = p + 1;
    }

    action extract_counted_value {
        int n_cv_digs = p - start;
        char *n_dig_str = (char *)malloc(n_cv_digs + 1);
        memcpy(n_dig_str, start, n_cv_digs);
        n_dig_str[n_cv_digs] = '\0';
        int n_digs = strtol(n_dig_str, NULL, 10);
        if (n_digs != 0) {
            char *cv = (char *)malloc(n_digs + 1);
            memcpy(cv, p + 1, n_digs);
            cv[n_digs] = '\0';
            mr_counted_value = strtol(cv, NULL, 10);
            p = p + 1 + n_digs;
            start = p + 1;
        }
        else {
            mr_counted_value = -1;
        }
    }

    action extract_label {
        char *lbl_len_str = (char *)malloc(p - start + 1);
        memcpy(lbl_len_str, start, p - start);
        lbl_len_str[p - start] = '\0';
        int len = strtol(lbl_len_str, NULL, 10);
        mr_label = (char *)malloc(len + 1);
        memcpy(mr_label, p + 1, len);
        mr_label[len] = '\0';
        p = p + 1 + len;
        start = p + 1;
    }

    action extract_subvar {
        int len = p - start;
        char *subvar = (char *)malloc(len + 1);
        memcpy(subvar, start, len);
        subvar[len] = '\0';
        start = p + 1;

        mr_subvariables = realloc(mr_subvariables, sizeof(char *) * (mr_subvar_count + 1));
        mr_subvariables[mr_subvar_count++] = subvar;
    }

    name = (alnum | '_')+ '=' > extract_mr_name;
    type = ('C' | 'D'){1} > extract_mr_type;
    counted_value = digit* ' ' > extract_counted_value;
    label = digit+ ' '+ > extract_label;

    nc = (alnum | '_'); # name character
    end = (space | '\0'); # token terminator
    subvariable = (nc+ end >extract_subvar);

    name_extractor := name type counted_value label subvariable+;
}%%

%% write data;

readstat_error_t extract_mr_data(const char *line, mr_set_t *result) {
    readstat_error_t retval = READSTAT_OK;

    // Variables needed for Ragel operation
    int cs = 0;
    char *p = (char *)line;
    char *start = p;
    char *pe = p + strlen(p) + 1;

    // Variables needed for passing Ragel intermediate results
    char mr_type;
    int mr_counted_value;
    int mr_subvar_count;
    char **mr_subvariables = NULL;
    char *mr_name = NULL;
    char *mr_label = NULL;

    // Execute Ragel finite state machine (FSM)
    %% write init;
    %% write exec;

    // Check if FSM finished successfully
    if (cs < %%{ write first_final; }%% || p != pe) {
        retval = READSTAT_ERROR_BAD_MR_STRING;
        goto cleanup;
    }

    // Assign parsed values to output parameter
    result->name = strdup(mr_name);
    result->label = strdup(mr_label);
    result->type = mr_type;
    result->counted_value = mr_counted_value;
    result->subvariables = mr_subvariables;
    result->num_subvars = mr_subvar_count;
    if (result->type == 'D') {
        result->is_dichotomy = 1;
    }

cleanup:
    if (retval != READSTAT_OK) {
        if (mr_subvariables != NULL) {
            for (int i = 0; i < mr_subvar_count; i++) {
                if (mr_subvariables[i] != NULL) free(mr_subvariables[i]);
            }
            free(mr_subvariables);
        }
        if (mr_name != NULL) free(mr_name);
        if (mr_label != NULL) free(mr_label);
    }
    return retval;
}


readstat_error_t parse_mr_line(const char *line, mr_set_t *result) {
    readstat_error_t retval = READSTAT_OK;
    *result = (mr_set_t){0};

    return extract_mr_data(line, result);
}