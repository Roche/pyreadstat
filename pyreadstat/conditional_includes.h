#include "Python.h"
 
#ifdef _WIN32

	#include <fcntl.h>
	#include <share.h>
	
	void assign_fd(void *io_ctx, int fd) { ((unistd_io_ctx_t*)io_ctx)->fd = fd; }
	
    long seek_fd(readstat_off_t offset, readstat_io_flags_t whence, void *io_ctx)
        {
            int origin;
            if (whence == READSTAT_SEEK_SET)
                origin = SEEK_SET;
            else if (whence == READSTAT_SEEK_CUR)
                origin = SEEK_CUR;
            else
                origin = SEEK_END;
            return _lseek(((unistd_io_ctx_t*)io_ctx)->fd, offset, origin);
        }
		
#else
	
	int _wsopen(const wchar_t *filename, int oflag, int shflag, int pmode){};
    int _O_RDONLY;
    int _O_BINARY;
	int _SH_DENYRW;  
    int _SH_DENYWR; 
    int _SH_DENYRD;
    int _SH_DENYNO;
	void assign_fd(void *io_ctx, int fd);
    long seek_fd(readstat_off_t offset, readstat_io_flags_t whence, void *io_ctx){};
	
#endif
