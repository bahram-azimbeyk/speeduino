#pragma once
#include <stdint.h>
#ifdef INJECTOR_BENCH_TEST
uint8_t injectorBenchTelemetry();
bool injectorBenchOwnsOutputs();
bool injectorBenchOwnsPin(uint8_t pin);
void injectorBenchTick();
void injectorBenchKeepAlive();
void injectorBenchStop();
// In-place framed command handler; returns response length including result code.
uint16_t injectorBenchCommand(uint8_t *payload, uint16_t length);
#else
inline bool injectorBenchOwnsOutputs() { return false; }
inline bool injectorBenchOwnsPin(uint8_t) { return false; }
inline void injectorBenchTick() {}
inline void injectorBenchKeepAlive() {}
inline void injectorBenchStop() {}
#endif
