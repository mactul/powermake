#ifndef MY_LIB_H
#define MY_LIB_H

#ifdef __cplusplus
extern "C" {
#endif

extern int add_numbers(int x, int y);
#ifndef DISABLE_GNU_AS
extern int _multiply(int x, int y);
#endif
extern int _subtract(int x, int y);

#ifdef __cplusplus
}
#endif

#endif