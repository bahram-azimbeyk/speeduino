#pragma once
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
#define STM32F407xx 1
#define INJECTOR_BENCH_TEST 1
#define TIM11 11
#define NUM_DIGITAL_PINS 128
#define TIM_CR1_CEN 1U
#define TIM_CR1_ARPE 128U
#define TIM_DIER_UIE 1U
#define TICK_FORMAT 0
struct Registers { uint32_t CR1=0,DIER=0,SR=0,CNT=0,ARR=0; } timer;
#define TIM7 (&timer)
uint32_t mask=0;
uint32_t __get_PRIMASK() { return mask; }
void __disable_irq() { mask=1; }
void __enable_irq() { mask=0; }
uint32_t millis() { return 10000; }
uint32_t micros() { return 10000000; }
bool engineRunning=false;
bool engineIsRunning(uint32_t) { return engineRunning; }
void (*triggerCallbacks[2])()={};
#define CHANGE 1
uint8_t digitalPinToInterrupt(uint8_t p) { return p==28 ? 0 : 1; }
void attachInterrupt(uint8_t i,void (*cb)(),int) {triggerCallbacks[i]=cb;}
int restored=0;
void initialiseTriggers() { ++restored; }
struct HardwareTimer {
 HardwareTimer(Registers*) {}
 void pause() { timer.CR1 &= ~TIM_CR1_CEN; }
 uint32_t getTimerClkFreq() { return 84000000; }
 void setPrescaleFactor(uint32_t x) { assert(x==84); }
 void setOverflow(uint32_t x,int) {timer.ARR=x-1;}
 void attachInterrupt(void (*)()) {}
 void refresh() {timer.CNT=0;}
 void resume() {timer.CR1|=1;timer.DIER|=1;}
};
enum class SyncStatus {None,Full};
struct DecoderStatus {SyncStatus syncStatus=SyncStatus::None;};
struct Decoder {DecoderStatus status; bool isEngineRunning(uint32_t){return engineRunning;} DecoderStatus getStatus(){return status;} };
Decoder buildDecoder(uint8_t){++restored;return {};}
struct {uint8_t TrigPattern=0;} configPage4;
void detachInterrupt(uint8_t i) {triggerCallbacks[i]=nullptr;}
#define A15 119
#define KNOCK_MODE_DIGITAL 1
#define KNOCK_MODE_ANALOG 2
uint8_t pinTranslateAnalog(uint8_t pin) {return pin+64;}
#define PD3 28
#define PD4 29
struct InjectorCounts {uint8_t primary=8,secondary=0;uint8_t getTotalInjectors() const {return primary+secondary;}};
struct {InjectorCounts injOutputs;uint8_t maxIgnOutputs=8;Decoder decoder; bool isTestModeActive=false; uint8_t testOutputs=0,idleLoad=0;uint16_t RPM=0;bool hasSync=false,toothLogEnabled=false;uint8_t compositeTriggerUsed=0;} currentStatus;
struct {uint8_t pinMapping=14,fanEnable=1,flexEnabled=0;} configPage2;
struct {uint8_t boostEnabled=1,vvtEnabled=1,fanInv=0,iacPWMdir=0,iacChannels=0,iacAlgorithm=2,iacStepTime=1,iacStepHome=100;} configPage6;
uint8_t HWTest_INJ_Pulsed=0,HWTest_IGN_Pulsed=0;
enum {OFF, PENDING};
struct Schedule {void (*_pStartCallback)()=nullptr;int _status=OFF;bool hasNextSchedule=false;};
using FuelSchedule=Schedule;using IgnitionSchedule=Schedule;
Schedule fuelSchedule1,fuelSchedule2,fuelSchedule3,fuelSchedule4,fuelSchedule5,fuelSchedule6,fuelSchedule7,fuelSchedule8;
Schedule ignitionSchedule1,ignitionSchedule2,ignitionSchedule3,ignitionSchedule4,ignitionSchedule5,ignitionSchedule6,ignitionSchedule7,ignitionSchedule8;
uint8_t triggerInterrupt=0,triggerInterrupt2=1;
uint8_t pinInjector1=1,pinInjector2=2,pinInjector3=3,pinInjector4=4,pinInjector5=5,pinInjector6=6,pinInjector7=7,pinInjector8=8;
uint8_t pinCoil1=11,pinCoil2=12,pinCoil3=13,pinCoil4=14,pinCoil5=15,pinCoil6=16,pinCoil7=17,pinCoil8=18;
uint8_t pinFuelPump=20,pinFan=21,pinBoost=22,pinVVT_1=23,pinVVT_2=24,pinIdle1=25,pinIdle2=26,pinTachOut=27,pinTrigger=28,pinTrigger2=29;
unsigned opensSeen[8]={};bool levels[8]={};
#define PIN(N) void openInjector##N(){++opensSeen[N-1];levels[N-1]=true;} void closeInjector##N(){levels[N-1]=false;}
PIN(1) PIN(2) PIN(3) PIN(4) PIN(5) PIN(6) PIN(7) PIN(8)
struct FastCRC32 { uint32_t crc32(const uint8_t *p,uint16_t n) {
 uint32_t c=~0U;while(n--){c^=*p++;for(int i=0;i<8;i++)c=(c>>1)^((c&1)?0xedb88320U:0);}return ~c;
}};

#define OUTPUT 1
bool gpio[128]={};
void digitalWrite(uint8_t p,int v) {assert(p<128);gpio[p]=v;}
void pinMode(uint8_t p,int m) {assert(p<128 && m==OUTPUT);}
bool pinIsReserved(uint8_t p) {return p==120;}

uint8_t pinTrigger3=30,pinStepperDir=31,pinStepperStep=32,pinStepperEnable=33,
 pinAirConComp=34,pinAirConFan=35,pinAirConRequest=36,pinResetControl=37,pinDisplayReset=38,
 pinBaro=39,pinEMAP=40,pinFlex=41,pinVSS=42,pinLaunch=43,pinIdleUp=44,pinIdleUpOutput=45,
 pinWMIEmpty=46,pinWMIIndicator=47,pinWMIEnabled=48,pinFuelPressure=49,pinOilPressure=50,
 pinFuel2Input=51,pinSpark2Input=52,pinIgnBypass=53,pinCTPS=54;
bool coilLevels[8]={}; unsigned chargesSeen[8]={};
#define COIL(N) void beginCoil##N##Charge(){++chargesSeen[N-1];coilLevels[N-1]=true;} void endCoil##N##Charge(){coilLevels[N-1]=false;}
COIL(1) COIL(2) COIL(3) COIL(4) COIL(5) COIL(6) COIL(7) COIL(8)

#define LOW 0
#define HIGH 1

struct {uint8_t airConEnable=1,airConFanEnabled=1,airConCompPol=0,airConFanPol=0;} configPage15;

struct {uint8_t iacMaxSteps=100,iacCoolTime=1,iacStepperInv=0,enable_secondarySerial=0,enable_intcan=0,intcan_available=0;uint8_t caninput_sel[16]={},Auxinpina[16]={},Auxinpinb[16]={};} configPage9;
bool normalStepperIdle=true,restoredPositionKnown=false;
uint16_t restoredPosition=0;
bool idleBenchStepperReady(){return normalStepperIdle;}
void idleBenchRestorePosition(bool known,uint16_t pos){restoredPositionKnown=known;restoredPosition=pos;}

struct {uint8_t fuel2Mode=0,spark2Mode=0,wmiEnabled=0,vvt2Enabled=1,knock_mode=0,knock_pin=0;} configPage10;

struct {
 uint8_t injectorPins[8]={1,2,3,4,5,6,7,8};
 uint8_t coilPins[8]={11,12,13,14,15,16,17,18};
 uint8_t &pinAirConComp=::pinAirConComp;
 uint8_t &pinAirConFan=::pinAirConFan;
 uint8_t &pinAirConRequest=::pinAirConRequest;
 uint8_t &pinBaro=::pinBaro;
 uint8_t &pinBoost=::pinBoost;
 uint8_t &pinCTPS=::pinCTPS;
 uint8_t &pinDisplayReset=::pinDisplayReset;
 uint8_t &pinEMAP=::pinEMAP;
 uint8_t &pinFan=::pinFan;
 uint8_t &pinFlex=::pinFlex;
 uint8_t &pinFuel2Input=::pinFuel2Input;
 uint8_t &pinFuelPressure=::pinFuelPressure;
 uint8_t &pinFuelPump=::pinFuelPump;
 uint8_t &pinIdle1=::pinIdle1;
 uint8_t &pinIdle2=::pinIdle2;
 uint8_t &pinIdleUp=::pinIdleUp;
 uint8_t &pinIdleUpOutput=::pinIdleUpOutput;
 uint8_t &pinIgnBypass=::pinIgnBypass;
 uint8_t &pinLaunch=::pinLaunch;

 uint8_t &pinOilPressure=::pinOilPressure;
 uint8_t &pinResetControl=::pinResetControl;
 uint8_t &pinSpark2Input=::pinSpark2Input;
 uint8_t &pinStepperDir=::pinStepperDir;
 uint8_t &pinStepperEnable=::pinStepperEnable;
 uint8_t &pinStepperStep=::pinStepperStep;
 uint8_t &pinTachOut=::pinTachOut;
 uint8_t &pinTrigger=::pinTrigger;
 uint8_t &pinTrigger2=::pinTrigger2;
 uint8_t &pinTrigger3=::pinTrigger3;
 uint8_t &pinVSS=::pinVSS;
 uint8_t &pinVVT_1=::pinVVT_1;
 uint8_t &pinVVT_2=::pinVVT_2;
 uint8_t &pinWMIEmpty=::pinWMIEmpty;
 uint8_t &pinWMIEnabled=::pinWMIEnabled;
 uint8_t &pinWMIIndicator=::pinWMIIndicator;
uint8_t pinTPS=121,pinMAP=122,pinCLT=123,pinIAT=124,pinO2=125,pinO2_2=127,pinBat=126;
} pinNumbers;
void openInjector_DIRECT(uint8_t ch){++opensSeen[ch-1];levels[ch-1]=true;}
void closeInjector_DIRECT(uint8_t ch){levels[ch-1]=false;}
void coilCharging_DIRECT(uint8_t ch){++chargesSeen[ch-1];coilLevels[ch-1]=true;}
void coilStopCharging_DIRECT(uint8_t ch){coilLevels[ch-1]=false;}

struct {uint8_t outputPin[8]={};} configPage13;
void openInjector1and3() {openInjector1();openInjector3();}
void openInjector2and4() {openInjector2();openInjector4();}
void openInjector1and4() {openInjector1();openInjector4();}
void openInjector2and3() {openInjector2();openInjector3();}
void openInjector3and5() {openInjector3();openInjector5();}
void openInjector2and5() {openInjector2();openInjector5();}
void openInjector3and6() {openInjector3();openInjector6();}
void openInjector1and5() {openInjector1();openInjector5();}
void openInjector2and6() {openInjector2();openInjector6();}
void openInjector3and7() {openInjector3();openInjector7();}
void openInjector4and8() {openInjector4();openInjector8();}
void beginCoil1and3Charge() {beginCoil1Charge();beginCoil3Charge();}
void beginCoil2and4Charge() {beginCoil2Charge();beginCoil4Charge();}
void beginCoil1and4Charge() {beginCoil1Charge();beginCoil4Charge();}
void beginCoil2and5Charge() {beginCoil2Charge();beginCoil5Charge();}
void beginCoil3and6Charge() {beginCoil3Charge();beginCoil6Charge();}
void beginCoil1and5Charge() {beginCoil1Charge();beginCoil5Charge();}
void beginCoil2and6Charge() {beginCoil2Charge();beginCoil6Charge();}
void beginCoil3and7Charge() {beginCoil3Charge();beginCoil7Charge();}
void beginCoil4and8Charge() {beginCoil4Charge();beginCoil8Charge();}
void beginTrailingCoilCharge() {beginCoil2Charge();}
