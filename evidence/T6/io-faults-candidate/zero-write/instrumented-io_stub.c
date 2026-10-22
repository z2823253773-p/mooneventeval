
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <sys/stat.h>
#define FAULT_MODE 4
static int oc,sc,rc,cc,wc,live;
static void record_stats(void) {
  FILE *f=fopen("/Users/henryz/Desktop/\u6bd4\u8d5b/mooneventeval-t0/evidence/T6/io-faults-candidate/zero-write/syscalls.json","wb");
  if(f){fprintf(f,"{\"open_calls\":%d,\"stat_calls\":%d,\"read_calls\":%d,\"close_calls\":%d,\"stdout_write_calls\":%d,\"live_input_fds\":%d}\n",oc,sc,rc,cc,wc,live);fclose(f);}
}
__attribute__((constructor)) static void init_stats(void){atexit(record_stats);}
static int fault_open(const char *p,int flags){oc++;if(FAULT_MODE==1&&oc==1){errno=EINTR;return -1;}int fd=open(p,flags);if(fd>=0)live++;return fd;}
static int fault_stat(int fd,struct stat *s){sc++;if(FAULT_MODE==1&&sc==1){errno=EINTR;return -1;}return fstat(fd,s);}
static ssize_t fault_read(int fd,void *b,size_t n){rc++;if(FAULT_MODE==1&&rc==1){errno=EINTR;return -1;}if((FAULT_MODE==2&&rc==1)||(FAULT_MODE==3&&rc==2)){errno=EIO;return -1;}if((FAULT_MODE==1||FAULT_MODE==3)&&n>17)n=17;return read(fd,b,n);}
static int fault_close(int fd){cc++;int r=close(fd);if(r==0)live--;if(FAULT_MODE==6||FAULT_MODE==7){errno=FAULT_MODE==7?EINTR:EIO;return -1;}return r;}
static ssize_t fault_write(int fd,const void *b,size_t n){if(fd==1){wc++;if(FAULT_MODE==1&&wc==1){errno=EINTR;return -1;}if(FAULT_MODE==4)return 0;if(FAULT_MODE==5&&wc==2){errno=EIO;return -1;}if((FAULT_MODE==1||FAULT_MODE==5)&&n>7)n=7;}return write(fd,b,n);}
typedef void (*handler)(int);
static handler fault_signal(int s,handler h){if(FAULT_MODE==8)return SIG_ERR;return signal(s,h);}
#define open fault_open
#define fstat fault_stat
#define read fault_read
#define close fault_close
#define write fault_write
#define signal fault_signal
#include <stdint.h>
#include <limits.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <sys/stat.h>

_Static_assert(sizeof(int32_t) == sizeof(int), "MoonBit Int must match C int");
_Static_assert(SSIZE_MAX >= INT32_MAX, "ssize_t must cover bounded requests");

// All borrowed pointers are used synchronously; none are stored or freed.
// -1 = ordinary OS I/O failure; -2 = violated private wrapper precondition.
int32_t mee_init(void) {
  return signal(SIGPIPE, SIG_IGN) == SIG_ERR ? -1 : 0;
}

int32_t mee_open_readonly(const uint8_t *path) {
  int fd;
  do { fd = open((const char *)path, O_RDONLY | O_NONBLOCK | O_CLOEXEC); }
  while (fd < 0 && errno == EINTR);
  if (fd < 0) return -1;
  struct stat st;
  int result;
  do { result = fstat(fd, &st); } while (result < 0 && errno == EINTR);
  if (result < 0 || !S_ISREG(st.st_mode)) {
    // Never retry close(EINTR): the descriptor may already have been released.
    close(fd);
    return -1;
  }
  return (int32_t)fd;
}

int32_t mee_read(int32_t fd, uint8_t *buffer, int32_t count) {
  if (count < 0 || count > 65536) return -2;
  ssize_t n;
  do { n = read(fd, buffer, (size_t)count); } while (n < 0 && errno == EINTR);
  return n < 0 ? -1 : (int32_t)n; // n <= count <= 65536
}

int32_t mee_close(int32_t fd) { return close(fd) < 0 ? -1 : 0; }

int32_t mee_write(int32_t fd, const uint8_t *buffer, int32_t count) {
  if (count < 0 || count > 65536) return -2;
  ssize_t n;
  do { n = write(fd, buffer, (size_t)count); } while (n < 0 && errno == EINTR);
  return n < 0 ? -1 : (int32_t)n; // n <= count <= 65536
}
