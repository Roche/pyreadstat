#ifndef READSTAT_SAS_RDC_H
#define READSTAT_SAS_RDC_H

/* Ross Data Compression (RDC), a.k.a. COMPRESS=BINARY in SAS.
 *
 * All functions return the number of bytes produced, or -1 on error.
 * Passing a NULL output buffer computes the length without writing.
 */

#include <sys/types.h>

ssize_t sas_rdc_decompress(void *output_buf, size_t output_len,
        const void *input_buf, size_t input_len);
ssize_t sas_rdc_compress(void *output_buf, size_t output_len,
        const void *input_buf, size_t input_len);

ssize_t sas_rdc_decompressed_len(const void *input_buf, size_t input_len);
ssize_t sas_rdc_compressed_len(const void *bytes, size_t len);

#endif

