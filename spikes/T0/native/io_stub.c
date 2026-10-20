#include <stdint.h>
#include <limits.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
_Static_assert(sizeof(int32_t) == sizeof(int), "MoonBit Int must match C int");
_Static_assert(SSIZE_MAX >= INT32_MAX, "ssize_t must cover bounded Int requests");
// Borrowed pointers are used only synchronously, never stored or freed here.
int32_t spike_read(const uint8_t *path, uint8_t *buffer, int32_t capacity, int32_t wanted) {
  if (capacity < 0 || capacity > 65536 || wanted < 0 || wanted > capacity) return -2;
  int fd = open((const char *)path, O_RDONLY);
  if (fd < 0) return -1;
  ssize_t got = read(fd, buffer, (size_t)wanted);
  int saved_errno = errno;
  close(fd);
  errno = saved_errno;
  return got < 0 ? -1 : (int32_t)got; // got <= wanted <= 65536
}
int32_t spike_write(const uint8_t *buffer, int32_t capacity, int32_t wanted) {
  if (capacity < 0 || capacity > 65536 || wanted < 0 || wanted > capacity) return -2;
  ssize_t wrote = write(STDOUT_FILENO, buffer, (size_t)wanted);
  return wrote < 0 ? -1 : (int32_t)wrote;
}
