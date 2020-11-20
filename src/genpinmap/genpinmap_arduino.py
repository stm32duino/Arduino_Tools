import argparse
import datetime
import json
import re
import string
import subprocess
import sys
import textwrap
from argparse import RawTextHelpFormatter
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from xml.dom.minidom import parse, Node

mcu_list = []  # 'name'
io_list = []  # 'PIN','name'
alt_list = []  # 'PIN','name'
dualpad_list = []  # 'PIN','name'
remap_list = []  # 'PIN','name'
adclist = []  # 'PIN','name','ADCSignal'
daclist = []  # 'PIN','name','DACSignal'
i2cscl_list = []  # 'PIN','name','I2CSCLSignal'
i2csda_list = []  # 'PIN','name','I2CSDASignal'
pwm_list = []  # 'PIN','name','PWM'
uarttx_list = []  # 'PIN','name','UARTtx'
uartrx_list = []  # 'PIN','name','UARTrx'
uartcts_list = []  # 'PIN','name','UARTcts'
uartrts_list = []  # 'PIN','name','UARTrts'
spimosi_list = []  # 'PIN','name','SPIMOSI'
spimiso_list = []  # 'PIN','name','SPIMISO'
spissel_list = []  # 'PIN','name','SPISSEL'
spisclk_list = []  # 'PIN','name','SPISCLK'
cantd_list = []  # 'PIN','name','CANTD'
canrd_list = []  # 'PIN','name','CANRD'
eth_list = []  # 'PIN','name','ETH'
quadspidata0_list = []  # 'PIN','name','QUADSPIDATA0'
quadspidata1_list = []  # 'PIN','name','QUADSPIDATA1'
quadspidata2_list = []  # 'PIN','name','QUADSPIDATA2'
quadspidata3_list = []  # 'PIN','name','QUADSPIDATA3'
quadspisclk_list = []  # 'PIN','name','QUADSPISCLK'
quadspissel_list = []  # 'PIN','name','QUADSPISSEL'
syswkup_list = []  # 'PIN','name','SYSWKUP'
usb_list = []  # 'PIN','name','USB'
usb_otgfs_list = []  # 'PIN','name','USB'
usb_otghs_list = []  # 'PIN','name','USB'
sd_list = []  # 'PIN','name','SD'

# format
# Peripheral
start_elem_fmt = "  {{{:{width}}"
end_array_fmt = """  {{NC,{0:{w1}}NP,{0:{w2}}0}}
}};
#endif
"""

license_header = """/*
 *******************************************************************************
 * Copyright (c) {}, STMicroelectronics
 * All rights reserved.
 *
 * This software component is licensed by ST under BSD 3-Clause license,
 * the "License"; You may not use this file except in compliance with the
 * License. You may obtain a copy of the License at:
 *                        opensource.org/licenses/BSD-3-Clause
 *
 *******************************************************************************
 */""".format(
    datetime.datetime.now().year
)

# GPIO file parsing
def find_gpio_file():
    res = "ERROR"
    itemlist = xml_mcu.getElementsByTagName("IP")
    for s in itemlist:
        if "GPIO" in s.attributes["Name"].value:
            res = s.attributes["Version"].value
            break
    return res


def get_gpio_af_num(pintofind, iptofind):
    if "STM32F10" in mcu_file.stem:
        return get_gpio_af_numF1(pintofind, iptofind)
    # DBG print ('pin to find ' + pintofind)
    i = 0
    mygpioaf = ""
    for n in xml_gpio.documentElement.childNodes:
        i += 1
        j = 0
        if n.nodeType != Node.ELEMENT_NODE:
            continue
        for firstlevel in n.attributes.items():
            # if 'PB7' in firstlevel:
            if pintofind != firstlevel[1]:
                continue
            # DBG print (i , firstlevel)
            # n = pin node found
            for m in n.childNodes:
                j += 1
                k = 0
                if m.nodeType != Node.ELEMENT_NODE:
                    continue
                for secondlevel in m.attributes.items():
                    k += 1
                    # if 'I2C1_SDA' in secondlevel:
                    if iptofind not in secondlevel:
                        continue
                    # DBG print (i, j,  m.attributes.items())
                    # m = IP node found
                    for p in m.childNodes:
                        if p.nodeType != Node.ELEMENT_NODE:
                            continue
                        # p node of 'Specific parameter'
                        # DBG print (i,j,k,p.attributes.items())
                        for myc in p.childNodes:
                            # DBG print (myc)
                            if myc.nodeType != Node.ELEMENT_NODE:
                                continue
                            # myc = node of ALTERNATE
                            for mygpioaflist in myc.childNodes:
                                if mygpioaflist.data not in mygpioaf:
                                    if mygpioaf != "":
                                        mygpioaf += " "
                                    mygpioaf += mygpioaflist.data
                                # print (mygpioaf)
    if mygpioaf == "":
        mygpioaf = "GPIO_AF_NONE"
    return mygpioaf


def get_gpio_af_numF1(pintofind, iptofind):
    # print ('pin to find ' + pintofind + ' ip to find ' + iptofind)
    i = 0
    mygpioaf = ""
    for n in xml_gpio.documentElement.childNodes:
        i += 1
        j = 0
        if n.nodeType != Node.ELEMENT_NODE:
            continue
        for firstlevel in n.attributes.items():
            # print ('firstlevel ' , firstlevel)
            #                if 'PB7' in firstlevel:
            if pintofind != firstlevel[1]:
                continue
            # print ('firstlevel ' , i , firstlevel)
            # n = pin node found
            for m in n.childNodes:
                j += 1
                k = 0
                if m.nodeType != Node.ELEMENT_NODE:
                    continue
                for secondlevel in m.attributes.items():
                    # print ('secondlevel ' , i, j, k , secondlevel)
                    k += 1
                    # if 'I2C1_SDA' in secondlevel:
                    if iptofind not in secondlevel:
                        continue
                    # m = IP node found
                    # print (i, j,  m.attributes.items())
                    for p in m.childNodes:
                        # p node 'RemapBlock'
                        if (
                            p.nodeType == Node.ELEMENT_NODE
                            and p.hasChildNodes() is False
                        ):
                            if mygpioaf != "":
                                mygpioaf += " "
                            mygpioaf += "AFIO_NONE"
                        else:
                            for s in p.childNodes:
                                if s.nodeType != Node.ELEMENT_NODE:
                                    continue
                                # s node 'Specific parameter'
                                # print (i,j,k,p.attributes.items())
                                for myc in s.childNodes:
                                    # DBG print (myc)
                                    if myc.nodeType != Node.ELEMENT_NODE:
                                        continue
                                    # myc = AF value
                                    for mygpioaflist in myc.childNodes:
                                        if mygpioaf != "":
                                            mygpioaf += " "
                                        mygpioaf += mygpioaflist.data.replace(
                                            "__HAL_", ""
                                        ).replace("_REMAP", "")
                                        # print mygpioaf
    if mygpioaf == "":
        mygpioaf = "AFIO_NONE"
    return mygpioaf


# Storage
# Store pin I/O
def store_pin(pin, name, dest_list):
    if pin in [p[0] for p in dest_list]:
        return
    p = [pin, name]
    if p not in dest_list:
        dest_list.append(p)


# Store ADC list
def store_adc(pin, name, signal):
    if "IN" in signal:
        adclist.append([pin, name, signal])


# Store DAC list
def store_dac(pin, name, signal):
    daclist.append([pin, name, signal])


# Store I2C list
def store_i2c(pin, name, signal):
    # is it SDA or SCL ?
    if "_SCL" in signal:
        i2cscl_list.append([pin, name, signal])
    if "_SDA" in signal:
        i2csda_list.append([pin, name, signal])


# Store timers
def store_pwm(pin, name, signal):
    if "_CH" in signal:
        pwm_list.append([pin, name, signal])


# Store Uart pins
def store_uart(pin, name, signal):
    if "_TX" in signal:
        uarttx_list.append([pin, name, signal])
    if "_RX" in signal:
        uartrx_list.append([pin, name, signal])
    if "_CTS" in signal:
        uartcts_list.append([pin, name, signal])
    if "_RTS" in signal:
        uartrts_list.append([pin, name, signal])


# Store SPI pins
def store_spi(pin, name, signal):
    if "_MISO" in signal:
        spimiso_list.append([pin, name, signal])
    if "_MOSI" in signal:
        spimosi_list.append([pin, name, signal])
    if "_SCK" in signal:
        spisclk_list.append([pin, name, signal])
    if "_NSS" in signal:
        spissel_list.append([pin, name, signal])


# Store CAN pins
def store_can(pin, name, signal):
    if "_RX" in signal:
        canrd_list.append([pin, name, signal])
    if "_TX" in signal:
        cantd_list.append([pin, name, signal])


# Store ETH list
def store_eth(pin, name, signal):
    eth_list.append([pin, name, signal])


# Store QSPI pins
def store_qspi(pin, name, signal):
    if "_IO0" in signal:
        quadspidata0_list.append([pin, name, signal])
    if "_IO1" in signal:
        quadspidata1_list.append([pin, name, signal])
    if "_IO2" in signal:
        quadspidata2_list.append([pin, name, signal])
    if "_IO3" in signal:
        quadspidata3_list.append([pin, name, signal])
    if "_CLK" in signal:
        quadspisclk_list.append([pin, name, signal])
    if "_NCS" in signal:
        quadspissel_list.append([pin, name, signal])


# Store SYS pins
def store_sys(pin, name, signal):
    if "_WKUP" in signal:
        signal = signal.replace("PWR", "SYS")
        syswkup_list.append([pin, name, signal])


# Store USB pins
def store_usb(pin, name, signal):
    if "OTG" not in signal:
        usb_list.append([pin, name, signal])
    if signal.startswith("USB_OTG_FS"):
        usb_otgfs_list.append([pin, name, signal])
    if signal.startswith("USB_OTG_HS"):
        usb_otghs_list.append([pin, name, signal])


# Store SD pins
def store_sd(pin, name, signal):
    sd_list.append([pin, name, signal])


def print_periph_header():
    s = """{}
/*
 * Automatically generated from {}
 * CubeMX DB release {}
 */
#include "Arduino.h"
#include "{}.h"

/* =====
 * Notes:
 * - The pins mentioned Px_y_ALTz are alternative possibilities which use other
 *   HW peripheral instances. You can use them the same way as any other "normal"
 *   pin (i.e. analogWrite(PA7_ALT0, 128);). These pins are not available thanks
 *   pin number (Dx or x).
 *
 * - Commented lines are alternative possibilities which are not used per default.
 *   If you change them, you will have to know what you do
 * =====
 */
""".format(
        license_header,
        mcu_file.name,
        db_release,
        re.sub("\\.c$", "", periph_c_filename),
    )
    periph_c_file.write(s)


def print_all_lists():
    if print_list_header("ADC", "ADC", ["ADC"], adclist):
        print_adc()
    if print_list_header("DAC", "DAC", ["DAC"], daclist):
        print_dac()
    if print_list_header("I2C", "I2C_SDA", ["I2C"], i2csda_list, i2cscl_list):
        print_i2c(i2csda_list)
        if print_list_header("", "I2C_SCL", ["I2C"], i2cscl_list):
            print_i2c(i2cscl_list)
    if print_list_header("PWM", "PWM", ["TIM"], pwm_list):
        print_pwm()
    if print_list_header(
        "SERIAL",
        "UART_TX",
        ["UART"],
        uarttx_list,
        uartrx_list,
        uartrts_list,
        uartcts_list,
    ):
        print_uart(uarttx_list)
        if print_list_header("", "UART_RX", ["UART"], uartrx_list):
            print_uart(uartrx_list)
        if print_list_header("", "UART_RTS", ["UART"], uartrts_list):
            print_uart(uartrts_list)
        if print_list_header("", "UART_CTS", ["UART"], uartcts_list):
            print_uart(uartcts_list)
    if print_list_header(
        "SPI",
        "SPI_MOSI",
        ["SPI"],
        spimosi_list,
        spimiso_list,
        spisclk_list,
        spissel_list,
    ):
        print_spi(spimosi_list)
        if print_list_header("", "SPI_MISO", ["SPI"], spimiso_list):
            print_spi(spimiso_list)
        if print_list_header("", "SPI_SCLK", ["SPI"], spisclk_list):
            print_spi(spisclk_list)
        if print_list_header("", "SPI_SSEL", ["SPI"], spissel_list):
            print_spi(spissel_list)
    if len(canrd_list) and "FDCAN" in canrd_list[0][2]:
        canname = "FDCAN"
    else:
        canname = "CAN"
    if print_list_header(canname, "CAN_RD", [canname], canrd_list, cantd_list):
        print_can(canrd_list)
        if print_list_header("", "CAN_TD", [canname], cantd_list):
            print_can(cantd_list)
    if print_list_header("ETHERNET", "Ethernet", ["ETH"], eth_list):
        print_eth()
    inst = "QUADSPI"
    mod = "QSPI"
    if len(quadspidata0_list) > 0 and "OCTOSPI" in quadspidata0_list[0][2]:
        inst = "OCTOSPI"
        mod = "OSPI"
    if print_list_header(
        inst,
        inst + "_DATA0",
        [mod],
        quadspidata0_list,
        quadspidata1_list,
        quadspidata2_list,
        quadspidata3_list,
        quadspisclk_list,
        quadspissel_list,
    ):
        print_qspi(quadspidata0_list)
        if print_list_header("", inst + "_DATA1", [mod], quadspidata1_list):
            print_qspi(quadspidata1_list)
        if print_list_header("", inst + "_DATA2", [mod], quadspidata2_list):
            print_qspi(quadspidata2_list)
        if print_list_header("", inst + "_DATA3", [mod], quadspidata3_list):
            print_qspi(quadspidata3_list)
        if print_list_header("", inst + "_SCLK", [mod], quadspisclk_list):
            print_qspi(quadspisclk_list)
        if print_list_header("", inst + "_SSEL", [mod], quadspissel_list):
            print_qspi(quadspissel_list)
    if print_list_header(
        "USB", "USB", ["PCD", "HCD"], usb_list, usb_otgfs_list, usb_otghs_list
    ):
        print_usb(usb_list)
        if print_list_header("", "USB_OTG_FS", ["PCD", "HCD"], usb_otgfs_list):
            print_usb(usb_otgfs_list)
        if print_list_header("", "USB_OTG_HS", ["PCD", "HCD"], usb_otghs_list):
            print_usb(usb_otghs_list)
    if print_list_header("SD", "SD", ["SD"], sd_list):
        print_sd()
    # Print specific PinNames in header file
    print_dualpad_h()
    print_alt_h()
    print_syswkup_h()
    print_usb_h()


def print_list_header(feature, lname, lswitch, *argslst):
    lenlst = 0
    for lst in argslst:
        lenlst += len(lst)
    if lenlst > 0:
        # There is data for the feature
        if feature:
            s = """
//*** {} ***
""".format(
                feature
            )
        else:
            s = ""
        # Only for the first list
        if argslst[0]:
            if len(lswitch) == 1:
                s += """
#ifdef HAL_{}_MODULE_ENABLED""".format(
                    lswitch[0]
                )
            else:
                s += """
#if defined(HAL_{}_MODULE_ENABLED)""".format(
                    lswitch[0]
                )
                for mod in lswitch[1:]:
                    s += " || defined(HAL_{}_MODULE_ENABLED)".format(mod)

            s += """
WEAK const PinMap PinMap_{}[] = {{
""".format(
                lname
            )
    else:
        # No data for the feature or the list
        s = """
//*** No {} ***
""".format(
            feature if feature else lname
        )

    periph_c_file.write(s)
    return lenlst


def width_format(srclist):
    # PY_n_C_ALTX
    if any("_C_ALT" in p[0] for p in srclist):
        return 14
    # PY_n_ALTX
    elif any("_ALT" in p[0] for p in srclist):
        return 12
    # PY_n_C
    elif any("_C" in p[0] for p in srclist):
        return 9
    else:
        return 7


def print_adc():
    # Check GPIO version (alternate or not)
    s_pin_data = "STM_PIN_DATA_EXT(STM_MODE_ANALOG"
    # For STM32L47xxx/48xxx, it is necessary to configure
    # the GPIOx_ASCR register
    if re.match("STM32L4[78]+", mcu_file.stem):
        s_pin_data += "_ADC_CONTROL"
    s_pin_data += ", GPIO_NOPULL, 0, "

    wpin = width_format(adclist)

    for p in adclist:
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        a = p[2].split("_")
        inst = a[0].replace("ADC", "")
        if len(inst) == 0:
            inst = "1"  # single ADC for this product
        s1 += "{:6}".format("ADC" + inst + ",")
        chan = re.sub("IN[N|P]?", "", a[1])
        s1 += s_pin_data + chan
        s1 += ", 0)}, // " + p[2] + "\n"
        periph_c_file.write(s1)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=3))


def print_dac():
    wpin = width_format(daclist)

    for p in daclist:
        b = p[2]
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the DAC signal
        if b[3] == "_":  # 1 DAC in this chip
            s1 += (
                "DAC1, STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, "
                + b[7]
                + ", 0)}, // "
                + b
                + "\n"
            )
        else:
            s1 += (
                "DAC"
                + b[3]
                + ", STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, "
                + b[8]
                + ", 0)}, // "
                + b
                + "\n"
            )
        periph_c_file.write(s1)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=3))


def print_i2c(lst):
    wpin = width_format(lst)
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the I2C XXX signal
        b = p[2].split("_")[0]
        s1 += (
            b[: len(b) - 1]
            + b[len(b) - 1]
            + ", STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, "
        )
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            periph_c_file.write(s2)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=3))


def print_pwm():
    wpin = width_format(pwm_list)

    for p in pwm_list:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the PWM signal
        a = p[2].split("_")
        inst = a[0]
        if len(inst) == 3:
            inst += "1"
        s1 += "{:7}".format(inst + ",")
        chan = a[1].replace("CH", "")
        if chan.endswith("N"):
            neg = ", 1"
            chan = chan.strip("N")
        else:
            neg = ", 0"
        s1 += "STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ", " + chan + neg + ")}, // " + p[2] + "\n"
            periph_c_file.write(s2)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=4))


def print_uart(lst):
    wpin = width_format(lst)
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the UART_XX signal
        b = p[2].split("_")[0]
        s1 += "{:9}".format((b[: len(b) - 1] + b[len(b) - 1 :] + ","))
        if "STM32F10" in mcu_file.stem and lst == uartrx_list:
            s1 += "STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, "
        else:
            s1 += "STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            periph_c_file.write(s2)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=6))


def print_spi(lst):
    wpin = width_format(lst)
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the SPI_XXXX signal
        instance = p[2].split("_")[0].replace("SPI", "")
        s1 += "SPI" + instance + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            periph_c_file.write(s2)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=3))


def print_can(lst):
    wpin = width_format(lst)
    # "(FD)?CAN(d)?, "
    winst = len(lst[0][2].split("_")[0].rstrip(string.digits))
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the (FD)CAN_XX signal
        instance_name = p[2].split("_")[0]
        instance_number = instance_name.replace("FD", "").replace("CAN", "")
        if len(instance_number) == 0:
            instance_name += "1"
        if "STM32F10" in mcu_file.stem and lst == canrd_list:
            s1 += instance_name + ", STM_PIN_DATA(STM_MODE_INPUT, GPIO_NOPULL, "
        else:
            s1 += instance_name + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_NOPULL, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            periph_c_file.write(s2)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=winst))


def print_eth():
    prev_s = ""
    wpin = width_format(eth_list)

    for p in eth_list:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the ETH_XXXX signal
        s1 += "ETH, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, " + result + ")},"
        # check duplicated lines, only signal differs
        if prev_s == s1:
            s1 = "|" + p[2]
        else:
            if len(prev_s) > 0:
                periph_c_file.write("\n")
            prev_s = s1
            s1 += " // " + p[2]
        periph_c_file.write(s1 + "\n")
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=2))


def print_qspi(lst):
    if lst:
        prev_s = ""
        wpin = width_format(lst)
        if "OCTOSPIM_P1" in lst[0][2]:
            winst = 7
        else:
            winst = 6
        for p in lst:
            result = get_gpio_af_num(p[1], p[2])
            s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
            # 2nd element is the XXXXSPI_YYYY signal
            if "OCTOSPIM_P1" in p[2]:
                s1 += "OCTOSPI1,"
            elif "OCTOSPIM_P2" in p[2]:
                s1 += "OCTOSPI2,"
            else:
                s1 += "QUADSPI,"
            s1 += " STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, " + result + ")},"
            # check duplicated lines, only signal differs
            if prev_s == s1:
                s1 = "|" + p[2]
            else:
                if len(prev_s) > 0:
                    periph_c_file.write("\n")
                prev_s = s1
                s1 += " // " + p[2]
            periph_c_file.write(s1 + "\n")
        periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=winst))


def print_sd():
    wpin = width_format(sd_list)
    winst = len(sd_list[0][2].split("_")[0]) - 1

    for p in sd_list:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
        # 2nd element is the SD signal
        a = p[2].split("_")
        if a[1].startswith("C") or a[1].endswith("DIR"):
            s1 += a[0] + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_NOPULL, " + result + ")},"
        else:
            s1 += a[0] + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, " + result + ")},"
        s1 += " // " + p[2] + "\n"
        periph_c_file.write(s1)
    periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=winst))


def print_usb(lst):
    if lst:
        use_hs_in_fs = False
        nb_loop = 1
        inst = "USB"
        if lst == usb_otgfs_list:
            inst = "USB_OTG_FS"
        elif lst == usb_otghs_list:
            inst = "USB_OTG_HS"
            nb_loop = 2
        wpin = width_format(lst)
        winst = len(inst) - 1
        for nb in range(nb_loop):
            for p in lst:
                result = get_gpio_af_num(p[1], p[2])
                s1 = start_elem_fmt.format(p[0] + ",", width=wpin)
                if lst == usb_otghs_list:
                    if nb == 0:
                        if "ULPI" in p[2]:
                            continue
                        elif not use_hs_in_fs:
                            periph_c_file.write("#ifdef USE_USB_HS_IN_FS\n")
                            use_hs_in_fs = True
                    else:
                        if "ULPI" not in p[2]:
                            continue
                        elif use_hs_in_fs:
                            periph_c_file.write("#else\n")
                            use_hs_in_fs = False

                # 2nd element is the USB_XXXX signal
                if not p[2].startswith("USB_D") and "VBUS" not in p[2]:
                    if "ID" not in p[2]:
                        s1 += inst + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, "
                    else:
                        # ID pin: AF_PP + PULLUP
                        s1 += inst + ", STM_PIN_DATA(STM_MODE_AF_OD, GPIO_PULLUP, "
                else:
                    # USB_DM/DP and VBUS: INPUT + NOPULL
                    s1 += inst + ", STM_PIN_DATA(STM_MODE_INPUT, GPIO_NOPULL, "
                if result == "NOTFOUND":
                    s1 += "0)},"
                else:
                    r = result.split(" ")
                    for af in r:
                        s1 += af + ")},"
                s1 += " // " + p[2] + "\n"
                periph_c_file.write(s1)

        if lst == usb_otghs_list:
            periph_c_file.write("#endif /* USE_USB_HS_IN_FS */\n")
        periph_c_file.write(end_array_fmt.format("", w1=wpin - 3, w2=winst))


def print_dualpad_h():
    if len(dualpad_list) != 0:
        pinvar_h_file.write("/* Dual pad pin name */\n")
        for p in dualpad_list:
            s1 = "  %-12s = %-5s | %s,\n" % (
                p[0],
                p[0].split("_C")[0],
                "ALTC",
            )
            pinvar_h_file.write(s1)
    pinvar_h_file.write("\n")


def print_alt_h():
    if len(alt_list) == 0:
        pinvar_h_file.write("/* No alternate */\n")
    else:
        pinvar_h_file.write("/* Alternate pin name */\n")
        # print pin name under switch
        for p in alt_list:
            if "_ALT" in p[0]:
                s1 = "  {:10} = {:5} | {},\n".format(
                    p[0],
                    p[0].split("_A")[0],
                    p[0].split("_")[-1],
                )
                pinvar_h_file.write(s1)
    pinvar_h_file.write("\n")


def print_syswkup_h():
    if len(syswkup_list) == 0:
        pinvar_h_file.write("/* NO SYS_WKUP */\n")
    else:
        pinvar_h_file.write("/* SYS_WKUP */\n")
        # H7xx and F446 start from 0, inc by 1
        num = syswkup_list[0][2].replace("SYS_WKUP", "")
        inc = 0
        if num == "0":
            inc = 1
        # Fill list with missing SYS_WKUPx set to NC
        i = 0
        while i < 8:
            num = 0
            if len(syswkup_list) > i:
                n = syswkup_list[i][2].replace("SYS_WKUP", "")
                if len(n) != 0:
                    num = int(n) if inc == 1 else int(n) - 1
            x = i if inc == 1 else i + 1
            if num != i:
                syswkup_list.insert(i, ["NC", "NC_" + str(x), "SYS_WKUP" + str(x)])
            i += 1
        # print pin name under switch
        for p in syswkup_list:
            num = p[2].replace("SYS_WKUP", "")
            if len(num) == 0:
                s1 = "#ifdef PWR_WAKEUP_PIN1\n"
                s1 += "  SYS_WKUP1"  # single SYS_WKUP for this product
            else:
                s1 = "#ifdef PWR_WAKEUP_PIN{}\n".format(int(num) + inc)
                s1 += "  SYS_WKUP" + str(int(num) + inc)
            s1 += " = " + p[0] + ","
            if (inc == 1) and (p[0] != "NC"):
                s1 += " /* " + p[2] + " */"
            s1 += "\n#endif\n"
            pinvar_h_file.write(s1)


def print_usb_h():
    if usb_list or usb_otgfs_list or usb_otghs_list:
        pinvar_h_file.write("/* USB */\n")
        pinvar_h_file.write("#ifdef USBCON\n")
        for p in usb_list + usb_otgfs_list + usb_otghs_list:
            pinvar_h_file.write("  " + p[2] + " = " + p[0] + ",\n")
        pinvar_h_file.write("#endif\n")


# Variant files generation
def spi_pins_variant():
    ss_pin = ss1_pin = ss2_pin = ss3_pin = mosi_pin = miso_pin = sck_pin = "PYn"

    # Iterate to find match instance if any
    for mosi in spimosi_list:
        mosi_inst = mosi[2].split("_", 1)[0]
        for miso in spimiso_list:
            miso_inst = miso[2].split("_", 1)[0]
            if mosi_inst == miso_inst:
                for sck in spisclk_list:
                    sck_inst = sck[2].split("_", 1)[0]
                    if mosi_inst == sck_inst:
                        miso_pin = miso[0].replace("_", "", 1)
                        mosi_pin = mosi[0].replace("_", "", 1)
                        sck_pin = sck[0].replace("_", "", 1)
                        break
                else:
                    continue
                break
        else:
            continue

        # Try to find hw ssel
        for ss in spissel_list:
            ss_inst = ss[2].split("_", 1)[0]
            if mosi_inst == ss_inst:
                if "PYn" == ss_pin:
                    ss_pin = ss[0].replace("_", "", 1)
                elif "PYn" == ss1_pin:
                    ss1_pin = ss[0].replace("_", "", 1)
                elif "PYn" == ss2_pin:
                    ss2_pin = ss[0].replace("_", "", 1)
                elif "PYn" == ss3_pin:
                    ss3_pin = ss[0].replace("_", "", 1)
                    break
        break
    else:
        print("No SPI found!")
    return dict(
        ss=ss_pin,
        ss1=ss1_pin,
        ss2=ss2_pin,
        ss3=ss3_pin,
        mosi=mosi_pin,
        miso=miso_pin,
        sck=sck_pin,
    )


def i2c_pins_variant():
    sda_pin = scl_pin = "PYn"
    # Iterate to find match instance if any
    for sda in i2csda_list:
        sda_inst = sda[2].split("_", 1)[0]
        for scl in i2cscl_list:
            scl_inst = scl[2].split("_", 1)[0]
            if sda_inst == scl_inst:
                sda_pin = sda[0].replace("_", "", 1)
                scl_pin = scl[0].replace("_", "", 1)
                break
        else:
            continue
        break
    else:
        print("No I2C found!")
    return dict(sda=sda_pin, scl=scl_pin)


def serial_pins_variant():
    # Manage (LP)U(S)ART pins
    if uarttx_list:
        # Default if no rx pin
        serialtx_pin = uarttx_list[0][0].replace("_", "")
        serial_inst = uarttx_list[0][2].split("_", 1)[0]
        # Half duplex
        serialrx_pin = serialtx_pin
        if uartrx_list:
            # Iterate to find match instance if any
            for uarttx in uarttx_list:
                serialtx_inst = uarttx[2].split("_", 1)[0]
                for uartrx in uartrx_list:
                    serialrx_inst = uartrx[2].split("_", 1)[0]
                    if serialtx_inst == serialrx_inst:
                        serialtx_pin = uarttx[0].replace("_", "", 1)
                        serialrx_pin = uartrx[0].replace("_", "", 1)
                        serial_inst = serialtx_inst
                        break
                else:
                    continue
                break
        end_num_regex = r".*(\d+)$"
        serialnum = re.match(end_num_regex, serial_inst)
        if serialnum:
            serialnum = serialnum.group(1)
            if serial_inst.startswith("LP"):
                serialnum = "10" + serialnum
        else:
            print("No serial instance number found!")
            serialnum = "-1"
    else:
        serialtx_pin = serialtx_pin = "PYn"
        serialnum = "-1"
        print("No serial found!")
    return dict(instance=serialnum, rx=serialrx_pin, tx=serialtx_pin)


def timer_variant():
    # Choice is based on the fact Tone and Servo do not need output nor compare
    # capabilities, and thus select timer instance which have the less outputs/compare
    # capabilities:
    # - TIM6/TIM7/TIM18 because they have no output and no compare capabilities
    # - TIM10/TIM11/TIM13/TIM14 only 1 compare channel no complementary
    # - TIM16/TIM17 generally only 1 compare channel (with complementary)
    # - TIM9/TIM12/TIM21/TIM22 2 compare channels (no complementary)
    # - TIM15  generally 2 compare channel (with potentially complementary)
    # - TIM3/TIM4/TIM19 up to 4 channels
    # - TIM2/TIM5 (most of the time) the only 32bit timer. Could be reserved
    # for further 32bit support
    # - TIM1/TIM8/TIM20 they are the most advanced/complete timers

    tim_inst_order = [
        "TIM6",
        "TIM7",
        "TIM18",
        "TIM10",
        "TIM11",
        "TIM13",
        "TIM14",
        "TIM16",
        "TIM17",
        "TIM9",
        "TIM12",
        "TIM21",
        "TIM22",
        "TIM15",
        "TIM3",
        "TIM4",
        "TIM19",
        "TIM2",
        "TIM5",
        "TIM1",
        "TIM8",
        "TIM20",
    ]
    tim_inst_list = []
    tim_regex = r"^(TIM\d+)$"
    tone = servo = "TIMx"
    itemlist = xml_mcu.getElementsByTagName("IP")
    # Collect all TIMx instance
    for s in itemlist:
        inst = re.match(tim_regex, s.attributes["InstanceName"].value)
        if inst:
            tim_inst_list.append(inst.group(1))
    if tim_inst_list:
        for pref in tim_inst_order:
            if pref in tim_inst_list:
                if tone == "TIMx":
                    tone = pref
                elif servo == "TIMx":
                    servo = pref
                    break
        else:
            print("Not all TIM instance found!")
    return dict(tone=tone, servo=servo)


def print_variant():
    variant_h_template = j2_env.get_template(variant_h_filename)
    variant_cpp_template = j2_env.get_template(variant_cpp_filename)

    # Default pins definition
    num_digital_pins = len(io_list) + len(dualpad_list) + len(remap_list)
    num_dualpad_pins = len(dualpad_list)
    num_remap_pins = len(remap_list)

    # SPI definition
    spi_pins = spi_pins_variant()

    # I2C definition
    i2c_pins = i2c_pins_variant()

    # Serial definition
    serial = serial_pins_variant()

    # Timers definition
    timer = timer_variant()

    # Manage all pins number, PinName and analog pins
    analog_index = 0
    pins_number_list = []
    analog_pins_list = []
    pinnames_list = []
    idx_sum = len(io_list)
    for idx, io in enumerate(io_list):
        pyn = io[0].replace("_", "", 1)
        if [item for item in adclist if item[0] == io[0]]:
            ax = "A{}".format(analog_index)
            pins_number_list.append({"name": pyn, "val": ax})
            analog_pins_list.append({"val": idx, "ax": ax, "pyn": pyn})
            analog_index += 1
        else:
            pins_number_list.append({"name": pyn, "val": idx})
        pinnames_list.append(io[0])

    for idx, io in enumerate(dualpad_list):
        pyn = io[0].replace("_", "", 1)
        if [item for item in adclist if item[0] == io[0]]:
            ax = "A{}".format(analog_index)
            pins_number_list.append({"name": pyn, "val": ax})
            analog_pins_list.append({"val": idx + idx_sum, "ax": ax, "pyn": pyn})
            analog_index += 1
        else:
            pins_number_list.append({"name": pyn, "val": idx + idx_sum})
        pinnames_list.append(io[0])
    idx_sum += len(dualpad_list)
    for idx, io in enumerate(remap_list):
        pyn = io[0].replace("_", "", 1)
        if [item for item in adclist if item[0] == io[0]]:
            ax = "A{}".format(analog_index)
            pins_number_list.append({"name": pyn, "val": ax})
            analog_pins_list.append({"val": idx + idx_sum, "ax": ax, "pyn": pyn})
            analog_index += 1
        else:
            pins_number_list.append({"name": pyn, "val": idx + idx_sum})
        pinnames_list.append(io[0])
    alt_pins_list = []
    waltpin = [0]
    for p in alt_list:
        if "_ALT" in p[0]:
            pyn = p[0].replace("_", "", 1)
            waltpin.append(len(pyn))
            alt_pins_list.append(
                {"name": pyn, "base": pyn.split("_A")[0], "num": pyn.split("_")[-1]}
            )

    # Define extra HAL modules
    hal_modules_list = []
    if daclist:
        hal_modules_list.append("HAL_DAC_MODULE_ENABLED")
    if eth_list:
        hal_modules_list.append("HAL_ETH_MODULE_ENABLED")
    if quadspidata0_list:
        if "OCTOSPI" in quadspidata0_list[0][2]:
            hal_modules_list.append("HAL_OSPI_MODULE_ENABLED")
        else:
            hal_modules_list.append("HAL_QSPI_MODULE_ENABLED")
    if sd_list:
        hal_modules_list.append("HAL_SD_MODULE_ENABLED")

    mcu_serie = re.match(r"STM32([FGHLW][\dBL]|MP[\d])", mcu_file.stem)
    if not mcu_serie:
      print("No serie match found!")
      exit(1)
    mcu_serie = mcu_serie.group(1).lower()

    variant_h_file.write(
        variant_h_template.render(
            year=datetime.datetime.now().year,
            pins_number_list=pins_number_list,
            alt_pins_list=alt_pins_list,
            waltpin=max(waltpin),
            num_digital_pins=num_digital_pins,
            num_dualpad_pins=num_dualpad_pins,
            num_remap_pins=num_remap_pins,
            num_analog_inputs=len(analog_pins_list),
            spi_pins=spi_pins,
            i2c_pins=i2c_pins,
            timer=timer,
            serial=serial,
            hal_modules_list=hal_modules_list,
        )
    )

    variant_cpp_file.write(
        variant_cpp_template.render(
            year=datetime.datetime.now().year,
            pinnames_list=pinnames_list,
            analog_pins_list=analog_pins_list,
            mcu_serie=mcu_serie,
        )
    )


# List management
tokenize = re.compile(r"(\d+)|(\D+)").findall


def natural_sortkey(list_2_elem):
    return tuple(int(num) if num else alpha for num, alpha in tokenize(list_2_elem[0]))


def natural_sortkey2(list_2_elem):
    return tuple(int(num) if num else alpha for num, alpha in tokenize(list_2_elem[2]))


def sort_my_lists():
    io_list.sort(key=natural_sortkey)
    dualpad_list.sort(key=natural_sortkey)
    remap_list.sort(key=natural_sortkey)
    adclist.sort(key=natural_sortkey)
    daclist.sort(key=natural_sortkey)
    i2cscl_list.sort(key=natural_sortkey)
    i2csda_list.sort(key=natural_sortkey)
    pwm_list.sort(key=natural_sortkey2)
    pwm_list.sort(key=natural_sortkey)
    uarttx_list.sort(key=natural_sortkey)
    uartrx_list.sort(key=natural_sortkey)
    uartcts_list.sort(key=natural_sortkey)
    uartrts_list.sort(key=natural_sortkey)
    spimosi_list.sort(key=natural_sortkey)
    spimiso_list.sort(key=natural_sortkey)
    spissel_list.sort(key=natural_sortkey)
    spisclk_list.sort(key=natural_sortkey)
    cantd_list.sort(key=natural_sortkey)
    canrd_list.sort(key=natural_sortkey)
    eth_list.sort(key=natural_sortkey)
    quadspidata0_list.sort(key=natural_sortkey)
    quadspidata1_list.sort(key=natural_sortkey)
    quadspidata2_list.sort(key=natural_sortkey)
    quadspidata3_list.sort(key=natural_sortkey)
    quadspisclk_list.sort(key=natural_sortkey)
    quadspissel_list.sort(key=natural_sortkey)
    syswkup_list.sort(key=natural_sortkey2)
    usb_list.sort(key=natural_sortkey)
    usb_otgfs_list.sort(key=natural_sortkey)
    usb_otghs_list.sort(key=natural_sortkey)
    sd_list.sort(key=natural_sortkey)


def clean_all_lists():
    del io_list[:]
    del alt_list[:]
    del dualpad_list[:]
    del remap_list[:]
    del adclist[:]
    del daclist[:]
    del i2cscl_list[:]
    del i2csda_list[:]
    del pwm_list[:]
    del uarttx_list[:]
    del uartrx_list[:]
    del uartcts_list[:]
    del uartrts_list[:]
    del spimosi_list[:]
    del spimiso_list[:]
    del spissel_list[:]
    del spisclk_list[:]
    del cantd_list[:]
    del canrd_list[:]
    del eth_list[:]
    del quadspidata0_list[:]
    del quadspidata1_list[:]
    del quadspidata2_list[:]
    del quadspidata3_list[:]
    del quadspisclk_list[:]
    del quadspissel_list[:]
    del syswkup_list[:]
    del usb_list[:]
    del usb_otgfs_list[:]
    del usb_otghs_list[:]
    del sd_list[:]


def manage_alternate():
    update_alternate(adclist)
    update_alternate(daclist)
    update_alternate(i2cscl_list)
    update_alternate(i2csda_list)
    update_alternate(pwm_list)
    update_alternate(uarttx_list)
    update_alternate(uartrx_list)
    update_alternate(uartcts_list)
    update_alternate(uartrts_list)
    update_alternate(spimosi_list)
    update_alternate(spimiso_list)
    update_alternate(spissel_list)
    update_alternate(spisclk_list)
    update_alternate(cantd_list)
    update_alternate(canrd_list)
    update_alternate(eth_list)
    update_alternate(quadspidata0_list)
    update_alternate(quadspidata1_list)
    update_alternate(quadspidata2_list)
    update_alternate(quadspidata3_list)
    update_alternate(quadspisclk_list)
    update_alternate(quadspissel_list)
    update_alternate(syswkup_list)
    update_alternate(usb_list)
    update_alternate(usb_otgfs_list)
    update_alternate_usb_otg_hs()
    update_alternate(sd_list)

    alt_list.sort(key=natural_sortkey)



def update_alternate(lst):
    prev_p = ""
    alt_index = 1
    for index, p in enumerate(lst):
        if p[0] == prev_p:
            p[0] += "_ALT%d" % alt_index
            lst[index] = p
            store_pin(p[0], p[1], alt_list)
            alt_index += 1
        else:
            prev_p = p[0]
            alt_index = 1


def update_alternate_usb_otg_hs():
    prev_p = ""
    alt_index = 1
    for nb in range(2):
        for index, p in enumerate(usb_otghs_list):
            if nb == 0:
                if "ULPI" in p[2]:
                    continue
            else:
                if "ULPI" not in p[2]:
                    continue
            if p[0] == prev_p:
                p[0] += "_ALT%d" % alt_index
                usb_otghs_list[index] = p
                store_pin(p[0], p[1], alt_list)
                alt_index += 1
            else:
                prev_p = p[0]
                alt_index = 1


def parse_pins():
    print(" * Getting pins per Ips...")
    pinregex = r"^(P[A-Z][0-9][0-5]?[_]?[C]?)|^(ANA[0-9])"
    itemlist = xml_mcu.getElementsByTagName("Pin")
    for s in itemlist:
        m = re.match(pinregex, s.attributes["Name"].value)
        if m:
            if m.group(1) is not None:
                # pin formatted P<port>_<number>: PF_O
                pin = m.group(0)[:2] + "_" + m.group(0)[2:]
            else:
                # pin formatted ANA_<number>: ANA_1
                pin = m.group(0)[:3] + "_" + m.group(0)[3:]
            name = s.attributes["Name"].value.strip()  # full name: "PF0 / OSC_IN"
            if s.attributes["Type"].value in ["I/O", "MonoIO"]:
                if pin.endswith("_C"):
                    store_pin(pin, name, dualpad_list)
                elif (
                    "Variant" in s.attributes
                    and "REMAP" in s.attributes["Variant"].value
                ):
                    pin += "_R"
                    store_pin(pin, name, remap_list)
                else:
                    store_pin(pin, name, io_list)
            else:
                continue
            siglist = s.getElementsByTagName("Signal")
            for a in siglist:
                sig = a.attributes["Name"].value.strip()
                if sig.startswith("ADC"):
                    store_adc(pin, name, sig)
                elif all(["DAC" in sig, "_OUT" in sig]):
                    store_dac(pin, name, sig)
                elif re.match("^I2C", sig) is not None:  # ignore FMPI2C
                    store_i2c(pin, name, sig)
                elif re.match("^TIM", sig) is not None:  # ignore HRTIM
                    store_pwm(pin, name, sig)
                elif re.match("^(LPU|US|U)ART", sig) is not None:
                    store_uart(pin, name, sig)
                elif "SPI" in sig:
                    if "QUADSPI" in sig or "OCTOSPI" in sig:
                        store_qspi(pin, name, sig)
                    else:
                        store_spi(pin, name, sig)
                elif "CAN" in sig:
                    store_can(pin, name, sig)
                elif "ETH" in sig:
                    store_eth(pin, name, sig)
                elif "SYS_" in sig or "PWR_" in sig:
                    store_sys(pin, name, sig)
                elif "USB" in sig:
                    store_usb(pin, name, sig)
                elif re.match("^SD(IO|MMC)", sig) is not None:
                    store_sd(pin, name, sig)


# Config management
def create_config():
    # Create a Json file for a better path management
    try:
        print("Please set your configuration in '{}' file".format(config_filename))
        config_file = open(config_filename, "w", newline="\n")
        if sys.platform.startswith("win32"):
            print("Platform is Windows")
            cubemxdir = Path(
                r"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeMX"
            )
        elif sys.platform.startswith("linux"):
            print("Platform is Linux")
            cubemxdir = Path.home() / "STM32CubeMX"
        elif sys.platform.startswith("darwin"):
            print("Platform is Mac OSX")
            cubemxdir = Path(
                "/Applications/STMicroelectronics/STM32CubeMX.app/Contents/Resources"
            )
        else:
            print("Platform unknown")
            cubemxdir = "<Set CubeMX install directory>"
        config_file.write(
            json.dumps(
                {
                    "CUBEMX_DIRECTORY": str(cubemxdir),
                    "REPO_LOCAL_PATH": str(repo_local_path),
                },
                indent=2,
            )
        )
        config_file.close()
    except IOError:
        print("Failed to open " + config_filename)
    exit(1)


def check_config():
    global cubemxdir
    global repo_local_path
    global repo_path

    if config_filename.is_file():
        try:
            config_file = open(config_filename, "r")
            config = json.load(config_file)
            config_file.close()

            conf = config["REPO_LOCAL_PATH"]
            if conf:
                if conf != "":
                    repo_local_path = Path(conf)
                    repo_path = repo_local_path / repo_name
            conf = config["CUBEMX_DIRECTORY"]
            if conf:
                cubemxdir = Path(conf)
        except IOError:
            print("Failed to open " + config_filename)
    else:
        create_config()


def manage_repo():
    global db_release
    repo_local_path.mkdir(parents=True, exist_ok=True)

    print("Updating " + repo_name + "...")
    try:
        if not args.skip:
            if repo_path.is_dir():
                # Get new tags from the remote
                git_cmds = [
                    ["git", "-C", repo_path, "clean", "-fdx"],
                    ["git", "-C", repo_path, "fetch"],
                    ["git", "-C", repo_path, "reset", "--hard", "origin/master"],
                ]
            else:
                # Clone it as it does not exists yet
                git_cmds = [["git", "-C", repo_local_path, "clone", gh_url]]

            for cmd in git_cmds:
                subprocess.check_output(cmd).decode("utf-8")
        if repo_path.is_dir():
            # Get tag
            sha1_id = (
                subprocess.check_output(
                    ["git", "-C", repo_path, "rev-list", "--tags", "--max-count=1"]
                )
                .decode("utf-8")
                .strip()
            )
            version_tag = (
                subprocess.check_output(
                    ["git", "-C", repo_path, "describe", "--tags", sha1_id]
                )
                .decode("utf-8")
                .strip()
            )
            subprocess.check_output(
                ["git", "-C", repo_path, "checkout", version_tag],
                stderr=subprocess.DEVNULL,
            )
            db_release = version_tag
            return True
    except subprocess.CalledProcessError as e:
        print("Command {} failed with error code {}".format(e.cmd, e.returncode))
    return False


# main
cur_dir = Path.cwd()
templates_dir = cur_dir / "templates"
periph_c_filename = "PeripheralPins.c"
pinvar_h_filename = "PinNamesVar.h"
config_filename = Path("config.json")
variant_h_filename = "variant.h"
variant_cpp_filename = "variant.cpp"
repo_local_path = cur_dir / "repo"
gh_url = "https://github.com/STMicroelectronics/STM32_open_pin_data"
repo_name = gh_url.rsplit("/", 1)[-1]
repo_path = repo_local_path / repo_name
db_release = "Unknown"

check_config()

# By default, generate for all mcu xml files description
parser = argparse.ArgumentParser(
    description=textwrap.dedent(
        """\
By default, generate {}, {}, {} and {}
for all xml files description available in STM32CubeMX internal database.
Internal database path must be defined in {}.
It can be the one from STM32CubeMX directory if defined:
\t{}
or the one from GitHub:
\t{}

""".format(
            periph_c_filename,
            pinvar_h_filename,
            variant_cpp_filename,
            variant_h_filename,
            config_filename,
            cubemxdir,
            gh_url,
        )
    ),
    epilog=textwrap.dedent(
        """\
After files generation, review them carefully and please report any issue to GitHub:
\thttps://github.com/stm32duino/Arduino_Tools/issues\n
Once generated, you can comment a line if the pin should not be used
(overlaid with some HW on the board, for instance) and update all undefined pins
in variant."""
    ),
    formatter_class=RawTextHelpFormatter,
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-l",
    "--list",
    help="list available xml files description in STM32CubeMX",
    action="store_true",
)
group.add_argument(
    "-m",
    "--mcu",
    metavar="xml",
    help=textwrap.dedent(
        """\
Generate {}, {}, {} and {}
for specified mcu xml file description in STM32CubeMX.
This xml file can contain non alpha characters in its name,
you should call it with double quotes""".format(
            periph_c_filename,
            pinvar_h_filename,
            variant_cpp_filename,
            variant_h_filename,
        )
    ),
)

parser.add_argument(
    "-c",
    "--cube",
    help=textwrap.dedent(
        """\
Use STM32CubeMX internal database. Default use GitHub {} repository.
""".format(
            repo_name
        )
    ),
    action="store_true",
)
parser.add_argument(
    "-s",
    "--skip",
    help="Skip {} clone/fetch".format(repo_name),
    action="store_true",
)
args = parser.parse_args()

# Using GitHub repo is the preferred way, CubeMX used as a fallback
fallback = False
if not args.cube:
    if manage_repo():
        dirMCU = repo_path / "mcu"
        dirIP = dirMCU / "IP"
    else:
        fallback = True
if fallback or args.cube:
    if not (cubemxdir.is_dir()):
        print(
            """
Cube Mx seems not to be installed or not at the specified location.

Please check the value set for 'CUBEMX_DIRECTORY' in '{}' file.""".format(
                config_filename
            )
        )
        quit()

    dirMCU = cubemxdir / "db" / "mcu"
    dirIP = dirMCU / "IP"
    version_file = cubemxdir / "db" / "package.xml"
    if version_file.is_file():
        xml_file = parse(str(version_file))
        PackDescription_item = xml_file.getElementsByTagName("PackDescription")
        for item in PackDescription_item:
            db_release = item.attributes["Release"].value

# Process DB release
release_regex = r".*(\d+.\d+.\d+)$"
release_match = re.match(release_regex, db_release)
if release_match:
    db_release = release_match.group(1)
print("CubeMX DB release {}\n".format(db_release))

if args.mcu:
    # Check input file exists
    if not ((dirMCU / args.mcu).is_file()):
        print("\n" + args.mcu + " file not found")
        print("\nCheck in " + dirMCU + " the correct name of this file")
        print("\nYou may use double quotes for file containing special characters")
        quit()
    mcu_list.append(dirMCU / args.mcu)
else:
    mcu_list = dirMCU.glob("STM32*.xml")

if args.list:
    print("Available xml files description:")
    for f in mcu_list:
        print(f.name)
    quit()

# Create the jinja2 environment.
j2_env = Environment(
    loader=FileSystemLoader(templates_dir),
    trim_blocks=True,
)

for mcu_file in mcu_list:
    print("Generating files for '{}'...".format(mcu_file.name))
    out_path = cur_dir / "Arduino" / mcu_file.name[:7] / mcu_file.stem
    periph_c_filepath = out_path / periph_c_filename
    periph_h_filepath = out_path / pinvar_h_filename
    variant_cpp_filepath = out_path / variant_cpp_filename
    variant_h_filepath = out_path / variant_h_filename
    out_path.mkdir(parents=True, exist_ok=True)

    # open output file
    periph_c_filepath.unlink(missing_ok=True)
    periph_c_file = open(periph_c_filepath, "w", newline="\n")
    periph_h_filepath.unlink(missing_ok=True)
    pinvar_h_file = open(periph_h_filepath, "w", newline="\n")
    variant_cpp_filepath.unlink(missing_ok=True)
    variant_cpp_file = open(variant_cpp_filepath, "w", newline="\n")
    variant_h_filepath.unlink(missing_ok=True)
    variant_h_file = open(variant_h_filepath, "w", newline="\n")

    # open input file
    xml_mcu = parse(str(mcu_file))
    gpiofile = find_gpio_file()
    if gpiofile == "ERROR":
        print("Could not find GPIO file")
        quit()
    xml_gpio = parse(str(dirIP / ("GPIO-" + gpiofile + "_Modes.xml")))

    parse_pins()
    sort_my_lists()
    manage_alternate()
    print_periph_header()
    print_all_lists()
    print_variant()

    print(
        "* Total I/O pins found: {}".format(
            len(io_list) + len(alt_list) + len(dualpad_list) + len(remap_list)
        )
    )
    print("   - {} I/O pins".format(len(io_list)))
    if len(dualpad_list):
        print("   - {} dual pad".format(len(dualpad_list)))
    if len(remap_list):
        print("   - {} remap pins".format(len(remap_list)))
    print("   - {} ALT I/O pins".format(len(alt_list)))

    # for io in io_list:
    #     print(io[0] + ", " + io[1])

    clean_all_lists()

    periph_c_file.close()
    pinvar_h_file.close()
    variant_h_file.close()
    variant_cpp_file.close()
