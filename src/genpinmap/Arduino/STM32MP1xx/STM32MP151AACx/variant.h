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
#define ANA0                    A0
#define ANA1                    A1
#define PA0                     A2
#define PA1                     A3
#define PA2                     A4
#define PA3                     A5
#define PA4                     A6
#define PA5                     A7
#define PA6                     A8
#define PA7                     A9
#define PA8                     10
#define PA9                     11
#define PA10                    12
#define PA11                    13
#define PA12                    14
#define PA13                    15
#define PA14                    16
#define PA15                    17
#define PB0                     A10
#define PB1                     A11
#define PB2                     20
#define PB3                     21
#define PB4                     22
#define PB5                     23
#define PB6                     24
#define PB7                     25
#define PB8                     26
#define PB9                     27
#define PB10                    28
#define PB11                    29
#define PB12                    30
#define PB13                    31
#define PB14                    32
#define PB15                    33
#define PC0                     A12
#define PC1                     A13
#define PC2                     A14
#define PC3                     A15
#define PC4                     A16
#define PC5                     A17
#define PC6                     40
#define PC7                     41
#define PC8                     42
#define PC9                     43
#define PC10                    44
#define PC11                    45
#define PC12                    46
#define PC13                    47
#define PC14                    48
#define PC15                    49
#define PD0                     50
#define PD1                     51
#define PD2                     52
#define PD3                     53
#define PD4                     54
#define PD5                     55
#define PD6                     56
#define PD7                     57
#define PD8                     58
#define PD9                     59
#define PD10                    60
#define PD11                    61
#define PD12                    62
#define PD13                    63
#define PD14                    64
#define PD15                    65
#define PE0                     66
#define PE1                     67
#define PE2                     68
#define PE3                     69
#define PE4                     70
#define PE5                     71
#define PE6                     72
#define PE7                     73
#define PE8                     74
#define PE9                     75
#define PE10                    76
#define PE11                    77
#define PE12                    78
#define PE13                    79
#define PE14                    80
#define PE15                    81
#define PF0                     82
#define PF1                     83
#define PF2                     84
#define PF3                     85
#define PF4                     86
#define PF5                     87
#define PF6                     88
#define PF7                     89
#define PF8                     90
#define PF9                     91
#define PF10                    92
#define PF11                    A18
#define PF12                    A19
#define PF13                    A20
#define PF14                    A21
#define PF15                    97
#define PG0                     98
#define PG1                     99
#define PG2                     100
#define PG3                     101
#define PG4                     102
#define PG5                     103
#define PG6                     104
#define PG7                     105
#define PG8                     106
#define PG9                     107
#define PG10                    108
#define PG11                    109
#define PG12                    110
#define PG13                    111
#define PG14                    112
#define PG15                    113
#define PH0                     114
#define PH1                     115
#define PH2                     116
#define PH3                     117
#define PH4                     118
#define PH5                     119
#define PH6                     120
#define PH7                     121
#define PH8                     122
#define PH9                     123
#define PH10                    124
#define PH11                    125
#define PH12                    126
#define PH13                    127
#define PH14                    128
#define PH15                    129
#define PI0                     130
#define PI1                     131
#define PI2                     132
#define PI3                     133
#define PI4                     134
#define PI5                     135
#define PI6                     136
#define PI7                     137
#define PI8                     138
#define PI9                     139
#define PI10                    140
#define PI11                    141
#define PZ0                     142
#define PZ1                     143
#define PZ2                     144
#define PZ3                     145
#define PZ4                     146
#define PZ5                     147
#define PZ6                     148
#define PZ7                     149

// Alternate pins number
#define ANA0_ALT1               (ANA0 | ALT1)
#define ANA0_ALT2               (ANA0 | ALT2)
#define ANA0_ALT3               (ANA0 | ALT3)
#define ANA1_ALT1               (ANA1 | ALT1)
#define PA0_ALT1                (PA0  | ALT1)
#define PA1_ALT1                (PA1  | ALT1)
#define PA1_ALT2                (PA1  | ALT2)
#define PA2_ALT1                (PA2  | ALT1)
#define PA2_ALT2                (PA2  | ALT2)
#define PA3_ALT1                (PA3  | ALT1)
#define PA3_ALT2                (PA3  | ALT2)
#define PA4_ALT1                (PA4  | ALT1)
#define PA4_ALT2                (PA4  | ALT2)
#define PA5_ALT1                (PA5  | ALT1)
#define PA5_ALT2                (PA5  | ALT2)
#define PA5_ALT3                (PA5  | ALT3)
#define PA6_ALT1                (PA6  | ALT1)
#define PA7_ALT1                (PA7  | ALT1)
#define PA7_ALT2                (PA7  | ALT2)
#define PA7_ALT3                (PA7  | ALT3)
#define PA8_ALT1                (PA8  | ALT1)
#define PA9_ALT1                (PA9  | ALT1)
#define PA11_ALT1               (PA11 | ALT1)
#define PA12_ALT1               (PA12 | ALT1)
#define PA15_ALT1               (PA15 | ALT1)
#define PA15_ALT2               (PA15 | ALT2)
#define PA15_ALT3               (PA15 | ALT3)
#define PB0_ALT1                (PB0  | ALT1)
#define PB0_ALT2                (PB0  | ALT2)
#define PB0_ALT3                (PB0  | ALT3)
#define PB1_ALT1                (PB1  | ALT1)
#define PB1_ALT2                (PB1  | ALT2)
#define PB2_ALT1                (PB2  | ALT1)
#define PB3_ALT1                (PB3  | ALT1)
#define PB3_ALT2                (PB3  | ALT2)
#define PB4_ALT1                (PB4  | ALT1)
#define PB4_ALT2                (PB4  | ALT2)
#define PB5_ALT1                (PB5  | ALT1)
#define PB5_ALT2                (PB5  | ALT2)
#define PB6_ALT1                (PB6  | ALT1)
#define PB7_ALT1                (PB7  | ALT1)
#define PB8_ALT1                (PB8  | ALT1)
#define PB8_ALT2                (PB8  | ALT2)
#define PB8_ALT3                (PB8  | ALT3)
#define PB9_ALT1                (PB9  | ALT1)
#define PB9_ALT2                (PB9  | ALT2)
#define PB9_ALT3                (PB9  | ALT3)
#define PB11_ALT1               (PB11 | ALT1)
#define PB12_ALT1               (PB12 | ALT1)
#define PB14_ALT1               (PB14 | ALT1)
#define PB14_ALT2               (PB14 | ALT2)
#define PB15_ALT1               (PB15 | ALT1)
#define PB15_ALT2               (PB15 | ALT2)
#define PC0_ALT1                (PC0  | ALT1)
#define PC1_ALT1                (PC1  | ALT1)
#define PC1_ALT2                (PC1  | ALT2)
#define PC1_ALT3                (PC1  | ALT3)
#define PC2_ALT1                (PC2  | ALT1)
#define PC3_ALT1                (PC3  | ALT1)
#define PC4_ALT1                (PC4  | ALT1)
#define PC5_ALT1                (PC5  | ALT1)
#define PC5_ALT2                (PC5  | ALT2)
#define PC5_ALT3                (PC5  | ALT3)
#define PC6_ALT1                (PC6  | ALT1)
#define PC6_ALT2                (PC6  | ALT2)
#define PC6_ALT3                (PC6  | ALT3)
#define PC7_ALT1                (PC7  | ALT1)
#define PC7_ALT2                (PC7  | ALT2)
#define PC7_ALT3                (PC7  | ALT3)
#define PC8_ALT1                (PC8  | ALT1)
#define PC9_ALT1                (PC9  | ALT1)
#define PC10_ALT1               (PC10 | ALT1)
#define PC11_ALT1               (PC11 | ALT1)
#define PD0_ALT1                (PD0  | ALT1)
#define PD1_ALT1                (PD1  | ALT1)
#define PD2_ALT1                (PD2  | ALT1)
#define PD3_ALT1                (PD3  | ALT1)
#define PD3_ALT2                (PD3  | ALT2)
#define PD3_ALT3                (PD3  | ALT3)
#define PD12_ALT1               (PD12 | ALT1)
#define PD13_ALT1               (PD13 | ALT1)
#define PE4_ALT1                (PE4  | ALT1)
#define PE4_ALT2                (PE4  | ALT2)
#define PE4_ALT3                (PE4  | ALT3)
#define PE5_ALT1                (PE5  | ALT1)
#define PE5_ALT2                (PE5  | ALT2)
#define PE5_ALT3                (PE5  | ALT3)
#define PE6_ALT1                (PE6  | ALT1)
#define PE15_ALT1               (PE15 | ALT1)
#define PF0_ALT1                (PF0  | ALT1)
#define PF1_ALT1                (PF1  | ALT1)
#define PF2_ALT1                (PF2  | ALT1)
#define PF2_ALT2                (PF2  | ALT2)
#define PF4_ALT1                (PF4  | ALT1)
#define PF8_ALT1                (PF8  | ALT1)
#define PF9_ALT1                (PF9  | ALT1)
#define PF12_ALT1               (PF12 | ALT1)
#define PF14_ALT1               (PF14 | ALT1)
#define PF15_ALT1               (PF15 | ALT1)
#define PG8_ALT1                (PG8  | ALT1)
#define PG11_ALT1               (PG11 | ALT1)
#define PH11_ALT1               (PH11 | ALT1)
#define PH12_ALT1               (PH12 | ALT1)
#define PZ0_ALT1                (PZ0  | ALT1)
#define PZ1_ALT1                (PZ1  | ALT1)
#define PZ1_ALT2                (PZ1  | ALT2)
#define PZ1_ALT3                (PZ1  | ALT3)
#define PZ2_ALT1                (PZ2  | ALT1)
#define PZ3_ALT1                (PZ3  | ALT1)
#define PZ3_ALT2                (PZ3  | ALT2)
#define PZ3_ALT3                (PZ3  | ALT3)
#define PZ4_ALT1                (PZ4  | ALT1)
#define PZ4_ALT2                (PZ4  | ALT2)
#define PZ4_ALT3                (PZ4  | ALT3)
#define PZ5_ALT1                (PZ5  | ALT1)
#define PZ5_ALT2                (PZ5  | ALT2)
#define PZ5_ALT3                (PZ5  | ALT3)
#define PZ6_ALT1                (PZ6  | ALT1)
#define PZ7_ALT1                (PZ7  | ALT1)

#define NUM_DIGITAL_PINS        150
#define NUM_ANALOG_INPUTS       22

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
#define PIN_SPI_SS2             PZ3
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
#define PIN_WIRE_SDA            PA12
#endif
#ifndef PIN_WIRE_SCL
#define PIN_WIRE_SCL            PA11
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
#define HAL_ETH_MODULE_ENABLED
#define HAL_QSPI_MODULE_ENABLED
#define HAL_SD_MODULE_ENABLED

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