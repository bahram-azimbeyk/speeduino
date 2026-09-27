#ifndef IDLE_H
#define IDLE_H

#include <stdint.h>

void initialiseIdle(bool forcehoming);
void idleControl(void);
void disableIdle(void);
void idleInterrupt(void);

#endif

#ifdef INJECTOR_BENCH_TEST
void idleBenchRestorePosition(bool known,uint16_t position);
#endif
