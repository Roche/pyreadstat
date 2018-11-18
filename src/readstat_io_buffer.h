
typedef struct buffer_io_ctx_s {
	const char *buf;
    size_t     size;
    size_t     pos;
} buffer_io_ctx_t;

int buffer_open_handler(const char *ignored, void *io_ctx);
int buffer_close_handler(void *io_ctx);
readstat_off_t buffer_seek_handler(readstat_off_t offset, readstat_io_flags_t whence, void *io_ctx);
ssize_t buffer_read_handler(void *buf, size_t nbytes, void *io_ctx);
readstat_error_t buffer_update_handler(long file_size, readstat_progress_handler progress_handler, void *user_ctx, void *io_ctx);
readstat_error_t buffer_io_init(readstat_parser_t *parser, const char *buffer, size_t size);
