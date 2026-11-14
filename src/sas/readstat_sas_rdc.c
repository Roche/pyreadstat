
#include <sys/types.h>
#include <string.h>
#include <stdint.h>

#if defined(_MSC_VER)
#include <BaseTsd.h>
typedef SSIZE_T ssize_t;
#endif

#include "readstat_sas_rdc.h"

/* Command layout (after a 16-bit big-endian control word; a set bit
 * means "command", a clear bit means "literal byte"):
 *
 *   marker 0x0N, B          -> insert (3 + N) copies of B          (3..18)
 *   marker 0x1N, H, B       -> insert (19 + N + 16*H) copies of B  (19..4114)
 *   marker 0x2N, H, L       -> copy (16 + L) bytes from offset (3 + N + 16*H)
 *   marker 0xCN, H (C >= 3) -> copy C bytes from offset (3 + N + 16*H)
 */

#define RDC_MIN_RUN            3
#define RDC_MAX_SHORT_RUN     18
#define RDC_MAX_LONG_RUN    4114
#define RDC_MIN_COPY           3
#define RDC_MAX_SHORT_COPY    15
#define RDC_MAX_LONG_COPY    271
#define RDC_MIN_OFFSET         3
#define RDC_MAX_OFFSET      4098

#define RDC_HASH_BITS         12
#define RDC_HASH_SIZE         (1 << RDC_HASH_BITS)

ssize_t sas_rdc_decompressed_len(const void *input_buf, size_t input_len) {
    return sas_rdc_decompress(NULL, 0, input_buf, input_len);
}

ssize_t sas_rdc_decompress(void *output_buf, size_t output_len,
        const void *input_buf, size_t input_len) {
    const unsigned char *input = (const unsigned char *)input_buf;
    const unsigned char *input_end = input + input_len;
    unsigned char *buffer = (unsigned char *)output_buf;
    size_t out = 0;

    while (input + 2 <= input_end) {
        int i;
        unsigned short prefix = (input[0] << 8) + input[1];
        input += 2;
        for (i=0; i<16; i++) {
            if ((prefix & (1 << (15 - i))) == 0) {
                if (input + 1 > input_end)
                    break;
                if (buffer) {
                    if (out + 1 > output_len)
                        return -1;
                    buffer[out] = *input;
                }
                input++;
                out++;
                continue;
            }

            if (input + 2 > input_end)
                return -1;

            unsigned char marker_byte = *input++;
            unsigned char next_byte = *input++;
            size_t insert_len = 0, copy_len = 0;
            unsigned char insert_byte = 0x00;
            size_t back_offset = 0;

            if (marker_byte <= 0x0F) {
                insert_len = 3 + marker_byte;
                insert_byte = next_byte;
            } else if ((marker_byte >> 4) == 1) {
                if (input + 1 > input_end)
                    return -1;
                insert_len = 19 + (marker_byte & 0x0F) + next_byte * 16;
                insert_byte = *input++;
            } else if ((marker_byte >> 4) == 2) {
                if (input + 1 > input_end)
                    return -1;
                copy_len = 16 + (*input++);
                back_offset = 3 + (marker_byte & 0x0F) + next_byte * 16;
            } else {
                copy_len = (marker_byte >> 4);
                back_offset = 3 + (marker_byte & 0x0F) + next_byte * 16;
            }

            if (insert_len) {
                if (buffer) {
                    if (out + insert_len > output_len)
                        return -1;
                    memset(&buffer[out], insert_byte, insert_len);
                }
                out += insert_len;
            } else if (copy_len) {
                if (out < back_offset || copy_len > back_offset)
                    return -1;
                if (buffer) {
                    if (out + copy_len > output_len)
                        return -1;
                    memcpy(&buffer[out], &buffer[out - back_offset], copy_len);
                }
                out += copy_len;
            }
        }
    }

    return out;
}

ssize_t sas_rdc_compressed_len(const void *bytes, size_t len) {
    return sas_rdc_compress(NULL, 0, bytes, len);
}

static size_t rdc_hash(const unsigned char *p) {
    uint32_t v = ((uint32_t)p[0] << 16) | ((uint32_t)p[1] << 8) | p[2];
    return (v * 2654435761u) >> (32 - RDC_HASH_BITS);
}

ssize_t sas_rdc_compress(void *output_buf, size_t output_len,
        const void *input_buf, size_t input_len) {
    const unsigned char *input = (const unsigned char *)input_buf;
    unsigned char *output = (unsigned char *)output_buf;
    size_t hash_table[RDC_HASH_SIZE];
    size_t in = 0, out = 0;
    size_t ctrl_pos = 0;
    int ctrl_bits = 16;
    unsigned short ctrl = 0;
    int i;

    for (i=0; i<RDC_HASH_SIZE; i++)
        hash_table[i] = SIZE_MAX;

#define RDC_EMIT(b) do { \
        if (output) { \
            if (out >= output_len) return -1; \
            output[out] = (unsigned char)(b); \
        } \
        out++; \
    } while (0)

#define RDC_FLUSH_CTRL() do { \
        if (output) { \
            output[ctrl_pos] = (unsigned char)(ctrl >> 8); \
            output[ctrl_pos+1] = (unsigned char)(ctrl & 0xFF); \
        } \
    } while (0)

    while (in < input_len) {
        if (ctrl_bits == 16) {
            if (out > 0)
                RDC_FLUSH_CTRL();
            ctrl_pos = out;
            ctrl = 0;
            ctrl_bits = 0;
            RDC_EMIT(0);
            RDC_EMIT(0);
        }

        /* Run of identical bytes */
        size_t run_len = 1;
        while (in + run_len < input_len && run_len < RDC_MAX_LONG_RUN &&
                input[in + run_len] == input[in]) {
            run_len++;
        }

        /* Back-reference (never overlapping, as the reader requires) */
        size_t copy_len = 0, back_offset = 0;
        if (in + RDC_MIN_COPY <= input_len) {
            size_t h = rdc_hash(&input[in]);
            size_t cand = hash_table[h];
            hash_table[h] = in;
            if (cand != SIZE_MAX && in - cand >= RDC_MIN_OFFSET && in - cand <= RDC_MAX_OFFSET) {
                size_t offset = in - cand;
                size_t max_len = offset;
                if (max_len > RDC_MAX_LONG_COPY)
                    max_len = RDC_MAX_LONG_COPY;
                if (max_len > input_len - in)
                    max_len = input_len - in;
                size_t len = 0;
                while (len < max_len && input[cand + len] == input[in + len])
                    len++;
                if (len >= RDC_MIN_COPY) {
                    copy_len = len;
                    back_offset = offset;
                }
            }
        }

        if (run_len >= RDC_MIN_RUN && run_len >= copy_len) {
            ctrl |= (1 << (15 - ctrl_bits));
            if (run_len <= RDC_MAX_SHORT_RUN) {
                RDC_EMIT(run_len - 3);
                RDC_EMIT(input[in]);
            } else {
                size_t n = run_len - 19;
                RDC_EMIT(0x10 | (n & 0x0F));
                RDC_EMIT(n >> 4);
                RDC_EMIT(input[in]);
            }
            in += run_len;
        } else if (copy_len) {
            size_t n = back_offset - 3;
            ctrl |= (1 << (15 - ctrl_bits));
            if (copy_len <= RDC_MAX_SHORT_COPY) {
                RDC_EMIT((copy_len << 4) | (n & 0x0F));
                RDC_EMIT(n >> 4);
            } else {
                RDC_EMIT(0x20 | (n & 0x0F));
                RDC_EMIT(n >> 4);
                RDC_EMIT(copy_len - 16);
            }
            in += copy_len;
        } else {
            RDC_EMIT(input[in]);
            in++;
        }
        ctrl_bits++;
    }

    if (out > 0)
        RDC_FLUSH_CTRL();

#undef RDC_EMIT
#undef RDC_FLUSH_CTRL

    return out;
}
