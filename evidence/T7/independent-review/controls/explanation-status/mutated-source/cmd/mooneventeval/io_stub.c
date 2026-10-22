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
