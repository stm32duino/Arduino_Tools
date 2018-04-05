/*
 *******************************************************************************
 * Copyright (c) 2018, STMicroelectronics
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 * 3. Neither the name of STMicroelectronics nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *******************************************************************************
 * Automatically generated from STM32F410T(8-B)Yx.xml
 */
#include "Arduino.h"
#include "PeripheralPins.h"

/* =====
 * Note: Commented lines are alternative possibilities which are not used per default.
 *       If you change them, you will have to know what you do
 * =====
 */

//*** ADC ***

#ifdef HAL_ADC_MODULE_ENABLED
const PinMap PinMap_ADC[] = {
    {PA_0,  ADC1,  STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, 0, 0)}, // ADC1_IN0
    {PA_2,  ADC1,  STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, 2, 0)}, // ADC1_IN2
    {PA_3,  ADC1,  STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, 3, 0)}, // ADC1_IN3
    {PA_5,  ADC1,  STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, 5, 0)}, // ADC1_IN5
    {NC,    NP,    0}
};
#endif

//*** DAC ***

#ifdef HAL_DAC_MODULE_ENABLED
const PinMap PinMap_DAC[] = {
    {PA_5,  DAC1, STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, 1, 0)}, // DAC_OUT1
    {NC,   NP,    0}
};
#endif

//*** I2C ***

#ifdef HAL_I2C_MODULE_ENABLED
const PinMap PinMap_I2C_SDA[] = {
    {PB_3,  FMPI2C1, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF4_FMPI2C1)},
    {PB_3,  I2C2, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF9_I2C2)},
    {PB_7,  I2C1, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF4_I2C1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_I2C_MODULE_ENABLED
const PinMap PinMap_I2C_SCL[] = {
    {PA_8,  FMPI2C1, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF4_FMPI2C1)},
    {PB_6,  I2C1, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF4_I2C1)},
    {PB_8,  I2C1, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF4_I2C1)},
    {PB_10, FMPI2C1, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF9_FMPI2C1)},
    {PB_10, I2C2, STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, GPIO_AF4_I2C2)},
    {NC,    NP,    0}
};
#endif

//*** PWM ***

#ifdef HAL_TIM_MODULE_ENABLED
const PinMap PinMap_PWM[] = {
    {PA_0,  TIM5,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF2_TIM5, 1, 0)},  // TIM5_CH1
    {PA_2,  TIM5,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF2_TIM5, 3, 0)},  // TIM5_CH3
    {PA_2,  TIM9,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF3_TIM9, 1, 0)},  // TIM9_CH1
    {PA_3,  TIM5,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF2_TIM5, 4, 0)},  // TIM5_CH4
    {PA_3,  TIM9,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF3_TIM9, 2, 0)},  // TIM9_CH2
    {PA_8,  TIM1,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF1_TIM1, 1, 0)},  // TIM1_CH1
    {PB_12, TIM5,   STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF2_TIM5, 1, 0)},  // TIM5_CH1
    {NC,    NP,    0}
};
#endif

//*** SERIAL ***

#ifdef HAL_UART_MODULE_ENABLED
const PinMap PinMap_UART_TX[] = {
    {PA_2,  USART2,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART2)},
    {PA_15, USART1,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART1)},
    {PB_6,  USART1,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_UART_MODULE_ENABLED
const PinMap PinMap_UART_RX[] = {
    {PA_3,  USART2,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART2)},
    {PB_3,  USART1,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART1)},
    {PB_7,  USART1,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_UART_MODULE_ENABLED
const PinMap PinMap_UART_RTS[] = {
    {PA_12, USART1,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_UART_MODULE_ENABLED
const PinMap PinMap_UART_CTS[] = {
    {PA_0,  USART2,  STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF7_USART2)},
    {NC,    NP,    0}
};
#endif

//*** SPI ***

#ifdef HAL_SPI_MODULE_ENABLED
const PinMap PinMap_SPI_MOSI[] = {
    {PB_5,  SPI1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF5_SPI1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_SPI_MODULE_ENABLED
const PinMap PinMap_SPI_MISO[] = {
    {PB_4,  SPI1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF5_SPI1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_SPI_MODULE_ENABLED
const PinMap PinMap_SPI_SCLK[] = {
    {PA_5,  SPI1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF5_SPI1)},
    {PB_3,  SPI1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF5_SPI1)},
    {NC,    NP,    0}
};
#endif

#ifdef HAL_SPI_MODULE_ENABLED
const PinMap PinMap_SPI_SSEL[] = {
    {PA_15, SPI1, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, GPIO_AF5_SPI1)},
    {NC,    NP,    0}
};
#endif

//*** CAN ***

//*** No CAN_RD ***

//*** No CAN_TD ***

//*** ETHERNET ***

//*** No Ethernet ***

//*** QUADSPI ***

//*** No QUADSPI ***
