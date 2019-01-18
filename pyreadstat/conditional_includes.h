/* The include and declarations in this file exists because when cython translates to c it cannot translate an IF UNAME_SYSNAME=="Windows" to
 * a c #ifdef. That means the resulting c file will be different if produced on windows or on unix. We want our c files to be portable and 
 * therefore do the right includes for windows here, and just declare dummy symbols for unix. 
 */
 
#ifdef _WIN32

    #include <fcntl.h>
    #include <share.h>
    
    // Stuff for handling paths with internation characters on windows
    void assign_fd(void *io_ctx, int fd) { ((unistd_io_ctx_t*)io_ctx)->fd = fd; }
        
#else
    
    int _wsopen(const wchar_t *filename, int oflag, int shflag, int pmode){};
    int _O_RDONLY;
    int _O_BINARY;
    int _SH_DENYRW;  
    int _SH_DENYWR; 
    int _SH_DENYRD;
    int _SH_DENYNO;
    void assign_fd(void *io_ctx, int fd){};
    
#endif
