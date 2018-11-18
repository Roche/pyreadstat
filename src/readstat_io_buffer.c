
#include <fcntl.h>
#include <stdlib.h>

#include "readstat.h"
#include "readstat_io_buffer.h"

int buffer_open_handler(const char *ignored, void *io_ctx) {
    ((buffer_io_ctx_t*) io_ctx)->pos = 0;
    return READSTAT_HANDLER_OK;
}

int buffer_close_handler(void *io_ctx) {
    ((buffer_io_ctx_t*) io_ctx)->pos = 0;
    return READSTAT_HANDLER_OK;
}

readstat_off_t buffer_seek_handler(readstat_off_t offset,
                                   readstat_io_flags_t whence,
                                   void *io_ctx) {
    readstat_off_t new_pos = 0;
    switch(whence) {
        case READSTAT_SEEK_SET:
            new_pos = offset;
            break;
        case READSTAT_SEEK_CUR:
            new_pos = ((buffer_io_ctx_t*) io_ctx)->pos+offset;
            break;
        case READSTAT_SEEK_END:
            new_pos = ((buffer_io_ctx_t*) io_ctx)->size+offset;
            break;
        default:
            return -1;
    }
    if(new_pos < 0)
        return -1;

    ((buffer_io_ctx_t*) io_ctx)->pos = new_pos;
    return ((buffer_io_ctx_t*) io_ctx)->pos;
}

ssize_t buffer_read_handler(void *buf, size_t nbyte, void *io_ctx) {
    buffer_io_ctx_t* buf_ctx = (buffer_io_ctx_t*) io_ctx;
    ssize_t available = buf_ctx->size - buf_ctx->pos;
    if((ssize_t)nbyte > available)
        nbyte = available > 0 ? available : 0;
    if(nbyte <= 0) 
        return 0;
    memcpy(buf, buf_ctx->buf + buf_ctx->pos, nbyte);
    buf_ctx->pos += nbyte;
    return nbyte;
}

readstat_error_t buffer_update_handler(long file_size, 
        readstat_progress_handler progress_handler, void *user_ctx,
        void *io_ctx) {
    if (!progress_handler)
        return READSTAT_OK;

    if (progress_handler(1.0 * ((buffer_io_ctx_t*) io_ctx)->pos / file_size, user_ctx))
        return READSTAT_ERROR_USER_ABORT;

    return READSTAT_OK;
}

readstat_error_t buffer_io_init(readstat_parser_t *parser, const char *buffer, size_t size) {
    readstat_error_t retval = READSTAT_OK;
    buffer_io_ctx_t *io_ctx = NULL;

    if ((retval = readstat_set_open_handler(parser, buffer_open_handler)) != READSTAT_OK)
        return retval;

    if ((retval = readstat_set_close_handler(parser, buffer_close_handler)) != READSTAT_OK)
        return retval;

    if ((retval = readstat_set_seek_handler(parser, buffer_seek_handler)) != READSTAT_OK)
        return retval;

    if ((retval = readstat_set_read_handler(parser, buffer_read_handler)) != READSTAT_OK)
        return retval;

    if ((readstat_set_update_handler(parser, buffer_update_handler)) != READSTAT_OK)
        return retval;

    io_ctx = calloc(1, sizeof(buffer_io_ctx_t));
    io_ctx->buf = buffer;
    io_ctx->size = size;
    io_ctx->pos = 0;

    retval = readstat_set_io_ctx(parser, (void*) io_ctx);
    parser->io->io_ctx_needs_free = 1;

    return retval;
}
