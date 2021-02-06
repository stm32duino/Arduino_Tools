/*
 *******************************************************************************
 * Copyright (c) 2021, STMicroelectronics
 * All rights reserved.
 *
 * This software component is licensed by ST under BSD 3-Clause license,
 * the "License"; You may not use this file except in compliance with the
 * License. You may obtain a copy of the License at:
 *                        opensource.org/licenses/BSD-3-Clause
 *
 *******************************************************************************
 */

#ifndef _VARIANT_ARDUINO_STM32_
#define _VARIANT_ARDUINO_STM32_
#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

/*----------------------------------------------------------------------------
 *        STM32 pins number
 *----------------------------------------------------------------------------*/
#define PA0                     A0
#define PA1                     A1
#define PA2                     A2
#define PA3                     A3
#define PA4                     A4
#define PA5                     A5
#define PA6                     A6
#define PA7                     A7
#define PA8                     8
#define PA9                     9
#define PA10                    10
#define PA11                    11
#define PA12                    12
#define PA13                    13
#define PA14                    14
#define PA15                    15
#define PB0                     A8
#define PB1                     A9
#define PB3                     18
#define PB4                     19
#define PB5                     20
#define PB6                     21
#define PB7                     22
#define PB8                     23
#define PB9                     24
#define PB10                    25
#define PB11                    26
#define PB12                    27
#define PB13                    28
#define PB14                    29
#define PB15                    30
#define PC13                    31
#define PC14                    32
#define PC15                    33
#define PF0                     34
#define PF1                     35
#define PF11                    36

// Alternate pins number
#define PA1_ALT1                (PA1  | ALT1)
#define PA2_ALT1                (PA2  | ALT1)
#define PA3_ALT1                (PA3  | ALT1)
#define PA6_ALT1                (PA6  | ALT1)
#define PA7_ALT1                (PA7  | ALT1)
#define PA7_ALT2                (PA7  | ALT2)
#define PA7_ALT3                (PA7  | ALT3)
#define PB0_ALT1                (PB0  | ALT1)
#define PB1_ALT1                (PB1  | ALT1)
#define PB1_ALT2                (PB1  | ALT2)
#define PB14_ALT1               (PB14 | ALT1)
#define PB15_ALT1               (PB15 | ALT1)
#define PB15_ALT2               (PB15 | ALT2)

#define NUM_DIGITAL_PINS        37
#define NUM_ANALOG_INPUTS       10

// On-board LED pin number
#ifndef LED_BUILTIN
#define LED_BUILTIN             PYn
#endif

// On-board user button
#ifndef USER_BTN
#define USER_BTN                PYn
#endif

// SPI definitions
#ifndef PIN_SPI_SS
#define PIN_SPI_SS              PA4
#endif
#ifndef PIN_SPI_SS1
#define PIN_SPI_SS1             PA15
#endif
#ifndef PIN_SPI_SS2
#define PIN_SPI_SS2             PYn
#endif
#ifndef PIN_SPI_SS3
#define PIN_SPI_SS3             PYn
#endif
#ifndef PIN_SPI_MOSI
#define PIN_SPI_MOSI            PA7
#endif
#ifndef PIN_SPI_MISO
#define PIN_SPI_MISO            PA6
#endif
#ifndef PIN_SPI_SCK
#define PIN_SPI_SCK             PA5
#endif

// I2C definitions
#ifndef PIN_WIRE_SDA
#define PIN_WIRE_SDA            PA10
#endif
#ifndef PIN_WIRE_SCL
#define PIN_WIRE_SCL            PA9
#endif

// Timer Definitions
// Use TIM6/TIM7 when possible as servo and tone don't need GPIO output pin
#ifndef TIMER_TONE
#define TIMER_TONE              TIM6
#endif
#ifndef TIMER_SERVO
#define TIMER_SERVO             TIM7
#endif

// UART Definitions
#ifndef SERIAL_UART_INSTANCE
#define SERIAL_UART_INSTANCE    4
#endif

// Default pin used for generic 'Serial' instance
// Mandatory for Firmata
#ifndef PIN_SERIAL_RX
#define PIN_SERIAL_RX           PA1
#endif
#ifndef PIN_SERIAL_TX
#define PIN_SERIAL_TX           PA0
#endif

// Extra HAL modules
#define HAL_DAC_MODULE_ENABLED

#ifdef __cplusplus
} // extern "C"
#endif

/*----------------------------------------------------------------------------
 *        Arduino objects - C++ only
 *----------------------------------------------------------------------------*/

#ifdef __cplusplus
  // These serial port names are intended to allow libraries and architecture-neutral
  // sketches to automatically default to the correct port name for a particular type
  // of use.  For example, a GPS module would normally connect to SERIAL_PORT_HARDWARE_OPEN,
  // the first hardware serial port whose RX/TX pins are not dedicated to another use.
  //
  // SERIAL_PORT_MONITOR        Port which normally prints to the Arduino Serial Monitor
  //
  // SERIAL_PORT_USBVIRTUAL     Port which is USB virtual serial
  //
  // SERIAL_PORT_LINUXBRIDGE    Port which connects to a Linux system via Bridge library
  //
  // SERIAL_PORT_HARDWARE       Hardware serial port, physical RX & TX pins.
  //
  // SERIAL_PORT_HARDWARE_OPEN  Hardware serial ports which are open for use.  Their RX & TX
  //                            pins are NOT connected to anything by default.
  #define SERIAL_PORT_MONITOR   Serial
  #define SERIAL_PORT_HARDWARE  Serial
#endif

#endif /* _VARIANT_ARDUINO_STM32_ */