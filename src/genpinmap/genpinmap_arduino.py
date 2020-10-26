import argparse
import datetime
import fnmatch
import json
import os
import re
import string
import sys
import textwrap
from xml.dom.minidom import parse, Node
from argparse import RawTextHelpFormatter

mcu_file = ""
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
start_elem_format = "  {{{:{width}}"
end_array_format = """  {{NC,{0:{w1}}NP,{0:{w2}}0}}
}};
#endif
"""


def find_gpio_file():
    res = "ERROR"
    itemlist = xml_mcu.getElementsByTagName("IP")
    for s in itemlist:
        a = s.attributes["Name"].value
        if "GPIO" in a:
            res = s.attributes["Version"].value
    return res


def get_gpio_af_num(pintofind, iptofind):
    if "STM32F10" in mcu_file:
        return get_gpio_af_numF1(pintofind, iptofind)
    # DBG print ('pin to find ' + pintofind)
    i = 0
    mygpioaf = ""
    for n in xml_gpio.documentElement.childNodes:
        i += 1
        j = 0
        if n.nodeType == Node.ELEMENT_NODE:
            for firstlevel in n.attributes.items():
                # if 'PB7' in firstlevel:
                if pintofind == firstlevel[1]:
                    # DBG print (i , firstlevel)
                    # n = pin node found
                    for m in n.childNodes:
                        j += 1
                        k = 0
                        if m.nodeType == Node.ELEMENT_NODE:
                            for secondlevel in m.attributes.items():
                                k += 1
                                # if 'I2C1_SDA' in secondlevel:
                                if iptofind in secondlevel:
                                    # DBG print (i, j,  m.attributes.items())
                                    # m = IP node found
                                    for p in m.childNodes:
                                        if p.nodeType == Node.ELEMENT_NODE:
                                            # p node of 'Specific parameter'
                                            # DBG print (i,j,k,p.attributes.items())
                                            for myc in p.childNodes:
                                                # DBG print (myc)
                                                if myc.nodeType == Node.ELEMENT_NODE:
                                                    # myc = node of ALTERNATE
                                                    for mygpioaflist in myc.childNodes:
                                                        if (
                                                            mygpioaflist.data
                                                            not in mygpioaf
                                                        ):
                                                            if mygpioaf != "":
                                                                mygpioaf += " "
                                                            mygpioaf += (
                                                                mygpioaflist.data
                                                            )
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
        if n.nodeType == Node.ELEMENT_NODE:
            for firstlevel in n.attributes.items():
                # print ('firstlevel ' , firstlevel)
                #                if 'PB7' in firstlevel:
                if pintofind == firstlevel[1]:
                    # print ('firstlevel ' , i , firstlevel)
                    # n = pin node found
                    for m in n.childNodes:
                        j += 1
                        k = 0
                        if m.nodeType == Node.ELEMENT_NODE:
                            for secondlevel in m.attributes.items():
                                # print ('secondlevel ' , i, j, k , secondlevel)
                                k += 1
                                # if 'I2C1_SDA' in secondlevel:
                                if iptofind in secondlevel:
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
                                                if s.nodeType == Node.ELEMENT_NODE:
                                                    # s node 'Specific parameter'
                                                    # print (i,j,k,p.attributes.items())
                                                    for myc in s.childNodes:
                                                        # DBG print (myc)
                                                        if (
                                                            myc.nodeType
                                                            == Node.ELEMENT_NODE
                                                        ):
                                                            # myc = AF value
                                                            for (
                                                                mygpioaflist
                                                            ) in myc.childNodes:
                                                                if mygpioaf != "":
                                                                    mygpioaf += " "
                                                                mygpioaf += mygpioaflist.data.replace(
                                                                    "__HAL_", ""
                                                                ).replace(
                                                                    "_REMAP", ""
                                                                )
                                                                # print mygpioaf
    if mygpioaf == "":
        mygpioaf = "AFIO_NONE"
    return mygpioaf


def store_pin(pin, name, dest_list):
    if pin in [p[0] for p in dest_list]:
        return
    # store pin I/O
    p = [pin, name]
    if p not in dest_list:
        dest_list.append(p)


# function to store ADC list
def store_adc(pin, name, signal):
    if "IN" in signal:
        adclist.append([pin, name, signal])


# function to store DAC list
def store_dac(pin, name, signal):
    daclist.append([pin, name, signal])


# function to store I2C list
def store_i2c(pin, name, signal):
    # is it SDA or SCL ?
    if "_SCL" in signal:
        i2cscl_list.append([pin, name, signal])
    if "_SDA" in signal:
        i2csda_list.append([pin, name, signal])


# function to store timers
def store_pwm(pin, name, signal):
    if "_CH" in signal:
        pwm_list.append([pin, name, signal])


# function to store Uart pins
def store_uart(pin, name, signal):
    if "_TX" in signal:
        uarttx_list.append([pin, name, signal])
    if "_RX" in signal:
        uartrx_list.append([pin, name, signal])
    if "_CTS" in signal:
        uartcts_list.append([pin, name, signal])
    if "_RTS" in signal:
        uartrts_list.append([pin, name, signal])


# function to store SPI pins
def store_spi(pin, name, signal):
    if "_MISO" in signal:
        spimiso_list.append([pin, name, signal])
    if "_MOSI" in signal:
        spimosi_list.append([pin, name, signal])
    if "_SCK" in signal:
        spisclk_list.append([pin, name, signal])
    if "_NSS" in signal:
        spissel_list.append([pin, name, signal])


# function to store CAN pins
def store_can(pin, name, signal):
    if "_RX" in signal:
        canrd_list.append([pin, name, signal])
    if "_TX" in signal:
        cantd_list.append([pin, name, signal])


# function to store ETH list
def store_eth(pin, name, signal):
    eth_list.append([pin, name, signal])


# function to store QSPI pins
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


# function to store SYS pins
def store_sys(pin, name, signal):
    if "_WKUP" in signal:
        signal = signal.replace("PWR", "SYS")
        syswkup_list.append([pin, name, signal])


# function to store USB pins
def store_usb(pin, name, signal):
    if "OTG" not in signal:
        usb_list.append([pin, name, signal])
    if signal.startswith("USB_OTG_FS"):
        usb_otgfs_list.append([pin, name, signal])
    if signal.startswith("USB_OTG_HS"):
        usb_otghs_list.append([pin, name, signal])


# function to store SD pins
def store_sd(pin, name, signal):
    sd_list.append([pin, name, signal])


def print_header():
    s = """/*
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
 * Automatically generated from {}
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
        datetime.datetime.now().year,
        os.path.basename(input_file_name),
        re.sub("\\.c$", "", out_c_filename),
    )
    out_c_file.write(s)


def print_all_lists():
    if print_list_header("ADC", "ADC", "ADC", adclist):
        print_adc()
    if print_list_header("DAC", "DAC", "DAC", daclist):
        print_dac()
    if print_list_header("I2C", "I2C_SDA", "I2C", i2csda_list, i2cscl_list):
        print_i2c(i2csda_list)
        if print_list_header("", "I2C_SCL", "I2C", i2cscl_list):
            print_i2c(i2cscl_list)
    if print_list_header("PWM", "PWM", "TIM", pwm_list):
        print_pwm()
    if print_list_header(
        "SERIAL",
        "UART_TX",
        "UART",
        uarttx_list,
        uartrx_list,
        uartrts_list,
        uartcts_list,
    ):
        print_uart(uarttx_list)
        if print_list_header("", "UART_RX", "UART", uartrx_list):
            print_uart(uartrx_list)
        if print_list_header("", "UART_RTS", "UART", uartrts_list):
            print_uart(uartrts_list)
        if print_list_header("", "UART_CTS", "UART", uartcts_list):
            print_uart(uartcts_list)
    if print_list_header(
        "SPI", "SPI_MOSI", "SPI", spimosi_list, spimiso_list, spisclk_list, spissel_list
    ):
        print_spi(spimosi_list)
        if print_list_header("", "SPI_MISO", "SPI", spimiso_list):
            print_spi(spimiso_list)
        if print_list_header("", "SPI_SCLK", "SPI", spisclk_list):
            print_spi(spisclk_list)
        if print_list_header("", "SPI_SSEL", "SPI", spissel_list):
            print_spi(spissel_list)
    if len(canrd_list) and "FDCAN" in canrd_list[0][2]:
        canname = "FDCAN"
    else:
        canname = "CAN"
    if print_list_header(canname, "CAN_RD", canname, canrd_list, cantd_list):
        print_can(canrd_list)
        if print_list_header("", "CAN_TD", canname, cantd_list):
            print_can(cantd_list)
    if print_list_header("ETHERNET", "Ethernet", "ETH", eth_list):
        print_eth()
    inst = "QUADSPI"
    mod = "QSPI"
    if len(quadspidata0_list) > 0 and "OCTOSPI" in quadspidata0_list[0][2]:
        inst = "OCTOSPI"
        mod = "OSPI"
    if print_list_header(
        inst,
        inst + "_DATA0",
        mod,
        quadspidata0_list,
        quadspidata1_list,
        quadspidata2_list,
        quadspidata3_list,
        quadspisclk_list,
        quadspissel_list,
    ):
        print_qspi(quadspidata0_list)
        if print_list_header("", inst + "_DATA1", mod, quadspidata1_list):
            print_qspi(quadspidata1_list)
        if print_list_header("", inst + "_DATA2", mod, quadspidata2_list):
            print_qspi(quadspidata2_list)
        if print_list_header("", inst + "_DATA3", mod, quadspidata3_list):
            print_qspi(quadspidata3_list)
        if print_list_header("", inst + "_SCLK", mod, quadspisclk_list):
            print_qspi(quadspisclk_list)
        if print_list_header("", inst + "_SSEL", mod, quadspissel_list):
            print_qspi(quadspissel_list)
    if print_list_header("USB", "USB", "PCD", usb_list, usb_otgfs_list, usb_otghs_list):
        print_usb(usb_list)
        if print_list_header("", "USB_OTG_FS", "PCD", usb_otgfs_list):
            print_usb(usb_otgfs_list)
        if print_list_header("", "USB_OTG_HS", "PCD", usb_otghs_list):
            print_usb(usb_otghs_list)
    if print_list_header("SD", "SD", "SD", sd_list):
        print_sd()
    # Print specific PinNames in header file
    print_dualpad_h()
    print_alt_h()
    print_syswkup_h()
    print_usb_h()


def print_list_header(feature, lname, switch, *argslst):
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
            s += """
#ifdef HAL_{}_MODULE_ENABLED
WEAK const PinMap PinMap_{}[] = {{
""".format(
                switch, lname
            )
    else:
        # No data for the feature or the list
        s = """
//*** No {} ***
""".format(
            feature if feature else lname
        )

    out_c_file.write(s)
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
    if re.match("STM32L4[78]+", mcu_file):
        s_pin_data += "_ADC_CONTROL"
    s_pin_data += ", GPIO_NOPULL, 0, "

    manage_alternate(adclist)
    wpin = width_format(adclist)

    for p in adclist:
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
        a = p[2].split("_")
        inst = a[0].replace("ADC", "")
        if len(inst) == 0:
            inst = "1"  # single ADC for this product
        s1 += "{:6}".format("ADC" + inst + ",")
        chan = re.sub("IN[N|P]?", "", a[1])
        s1 += s_pin_data + chan
        s1 += ", 0)}, // " + p[2] + "\n"
        out_c_file.write(s1)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=3))


def print_dac():
    wpin = width_format(daclist)

    for p in daclist:
        b = p[2]
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
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
        out_c_file.write(s1)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=3))


def print_i2c(lst):
    manage_alternate(lst)
    wpin = width_format(lst)
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
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
            out_c_file.write(s2)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=3))


def print_pwm():
    manage_alternate(pwm_list)
    wpin = width_format(pwm_list)

    for p in pwm_list:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
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
            out_c_file.write(s2)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=4))


def print_uart(lst):
    manage_alternate(lst)
    wpin = width_format(lst)
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
        # 2nd element is the UART_XX signal
        b = p[2].split("_")[0]
        s1 += "{:9}".format((b[: len(b) - 1] + b[len(b) - 1 :] + ","))
        if "STM32F10" in mcu_file and lst == uartrx_list:
            s1 += "STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, "
        else:
            s1 += "STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            out_c_file.write(s2)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=6))


def print_spi(lst):
    manage_alternate(lst)
    wpin = width_format(lst)
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
        # 2nd element is the SPI_XXXX signal
        instance = p[2].split("_")[0].replace("SPI", "")
        s1 += "SPI" + instance + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            out_c_file.write(s2)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=3))


def print_can(lst):
    wpin = width_format(lst)
    # "(FD)?CAN(d)?, "
    winst = len(lst[0][2].split("_")[0].rstrip(string.digits))
    for p in lst:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
        # 2nd element is the (FD)CAN_XX signal
        instance_name = p[2].split("_")[0]
        instance_number = instance_name.replace("FD", "").replace("CAN", "")
        if len(instance_number) == 0:
            instance_name += "1"
        if "STM32F10" in mcu_file and lst == canrd_list:
            s1 += instance_name + ", STM_PIN_DATA(STM_MODE_INPUT, GPIO_NOPULL, "
        else:
            s1 += instance_name + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_NOPULL, "
        r = result.split(" ")
        for af in r:
            s2 = s1 + af + ")},\n"
            out_c_file.write(s2)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=winst))


def print_eth():
    prev_s = ""
    wpin = width_format(eth_list)

    for p in eth_list:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
        # 2nd element is the ETH_XXXX signal
        s1 += "ETH, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, " + result + ")},"
        # check duplicated lines, only signal differs
        if prev_s == s1:
            s1 = "|" + p[2]
        else:
            if len(prev_s) > 0:
                out_c_file.write("\n")
            prev_s = s1
            s1 += " // " + p[2]
        out_c_file.write(s1 + "\n")
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=2))


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
            s1 = start_elem_format.format(p[0] + ",", width=wpin)
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
                    out_c_file.write("\n")
                prev_s = s1
                s1 += " // " + p[2]
            out_c_file.write(s1 + "\n")
        out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=winst))


def print_sd():
    wpin = width_format(sd_list)
    winst = len(sd_list[0][2].split("_")[0]) - 1

    for p in sd_list:
        result = get_gpio_af_num(p[1], p[2])
        s1 = start_elem_format.format(p[0] + ",", width=wpin)
        # 2nd element is the SD signal
        a = p[2].split("_")
        if a[1].startswith("C") or a[1].endswith("DIR"):
            s1 += a[0] + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_NOPULL, " + result + ")},"
        else:
            s1 += a[0] + ", STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, " + result + ")},"
        s1 += " // " + p[2] + "\n"
        out_c_file.write(s1)
    out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=winst))


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
                s1 = start_elem_format.format(p[0] + ",", width=wpin)
                if lst == usb_otghs_list:
                    if nb == 0:
                        if "ULPI" in p[2]:
                            continue
                        elif not use_hs_in_fs:
                            out_c_file.write("#ifdef USE_USB_HS_IN_FS\n")
                            use_hs_in_fs = True
                    else:
                        if "ULPI" not in p[2]:
                            continue
                        elif use_hs_in_fs:
                            out_c_file.write("#else\n")
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
                out_c_file.write(s1)

        if lst == usb_otghs_list:
            out_c_file.write("#endif /* USE_USB_HS_IN_FS */\n")
        out_c_file.write(end_array_format.format("", w1=wpin - 3, w2=winst))


def print_dualpad_h():
    if len(dualpad_list) != 0:
        out_h_file.write("/* Dual pad pin name */\n")
        for p in dualpad_list:
            s1 = "  %-12s = %-5s | %s,\n" % (p[0], p[0].split("_C")[0], "ALTC",)
            out_h_file.write(s1)
    out_h_file.write("\n")


def print_alt_h():
    if len(alt_list) == 0:
        out_h_file.write("/* No alternate */\n")
    else:
        out_h_file.write("/* Alternate pin name */\n")
        # print pin name under switch
        for p in alt_list:
            if "_ALT" in p[0]:
                s1 = "  {:10} = {:5} | {},\n".format(
                    p[0], p[0].split("_A")[0], p[0].split("_")[2],
                )
                out_h_file.write(s1)
    out_h_file.write("\n")


def print_syswkup_h():
    if len(syswkup_list) == 0:
        out_h_file.write("/* NO SYS_WKUP */\n")
    else:
        out_h_file.write("/* SYS_WKUP */\n")
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
            out_h_file.write(s1)


def print_usb_h():
    if usb_list or usb_otgfs_list or usb_otghs_list:
        out_h_file.write("/* USB */\n")
        out_h_file.write("#ifdef USBCON\n")
        for p in usb_list + usb_otgfs_list + usb_otghs_list:
            out_h_file.write("  " + p[2] + " = " + p[0] + ",\n")
        out_h_file.write("#endif\n")


tokenize = re.compile(r"(\d+)|(\D+)").findall


def manage_alternate(lst):
    prev_p = ""
    alt_index = 0
    for index, p in enumerate(lst):
        if p[0] == prev_p:
            p[0] += "_ALT%d" % alt_index
            lst[index] = p
            store_pin(p[0], p[1], alt_list)
            alt_index += 1
        else:
            prev_p = p[0]
            alt_index = 0


def natural_sortkey(list_2_elem):
    return tuple(int(num) if num else alpha for num, alpha in tokenize(list_2_elem[0]))


def natural_sortkey2(list_2_elem):
    return tuple(int(num) if num else alpha for num, alpha in tokenize(list_2_elem[2]))


def sort_my_lists():
    io_list.sort(key=natural_sortkey)
    alt_list.sort(key=natural_sortkey)
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


# main
cur_dir = os.getcwd()
out_c_filename = "PeripheralPins.c"
out_h_filename = "PinNamesVar.h"
config_filename = "config.json"

try:
    config_file = open(config_filename, "r")
except IOError:
    print("Please set your configuration in '{}' file".format(config_filename))
    config_file = open(config_filename, "w", newline="\n")
    if sys.platform.startswith("win32"):
        print("Platform is Windows")
        cubemxdir = (
            "C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeMX\\db\\mcu"
        )
    elif sys.platform.startswith("linux"):
        print("Platform is Linux")
        cubemxdir = os.getenv("HOME") + "/STM32CubeMX/db/mcu"
    elif sys.platform.startswith("darwin"):
        print("Platform is Mac OSX")
        cubemxdir = (
            "/Applications/STMicroelectronics/STM32CubeMX.app/Contents/Resources/db/mcu"
        )
    else:
        print("Platform unknown")
        cubemxdir = "<Set CubeMX install directory>/db/mcu"
    config_file.write(json.dumps({"CUBEMX_DIRECTORY": cubemxdir}))
    config_file.close()
    exit(1)

config = json.load(config_file)
config_file.close()
cubemxdir = config["CUBEMX_DIRECTORY"]

# by default, generate for all mcu xml files description
parser = argparse.ArgumentParser(
    description=textwrap.dedent(
        """\
By default, generate {} and {} for all xml files description available in
STM32CubeMX directory defined in '{}':
\t{}""".format(
            out_c_filename, out_h_filename, config_filename, cubemxdir
        )
    ),
    epilog=textwrap.dedent(
        """\
After files generation, review them carefully and please report any issue to github:
\thttps://github.com/stm32duino/Arduino_Tools/issues\n
Once generated, you have to comment a line if the pin is generated several times
for the same IP or if the pin should not be used (overlaid with some HW on the board,
for instance)"""
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
Generate {} and {} for specified mcu xml file description
in STM32CubeMX. This xml file contains non alpha characters in
its name, you should call it with double quotes""".format(
            out_c_filename, out_h_filename
        )
    ),
)
args = parser.parse_args()

if not (os.path.isdir(cubemxdir)):
    print("\nCube Mx seems not to be installed or not at the requested location.")
    print(
        "\nPlease check the value you set for 'CUBEMX_DIRECTORY' in '{}' file.".format(
            config_filename
        )
    )
    quit()

cubemxdirIP = os.path.join(cubemxdir, "IP")

if args.mcu:
    # check input file exists
    if not (os.path.isfile(os.path.join(cubemxdir, args.mcu))):
        print("\n" + args.mcu + " file not found")
        print("\nCheck in " + cubemxdir + " the correct name of this file")
        print("\nYou may use double quotes for file containing special characters")
        quit()
    mcu_list.append(args.mcu)
else:
    mcu_list = fnmatch.filter(os.listdir(cubemxdir), "STM32*.xml")

if args.list:
    print("Available xml files description: {}".format(mcu_list))
    for f in mcu_list:
        print(f)
    quit()

for mcu_file in mcu_list:
    print(
        "Generating {} and {} for '{}'...".format(
            out_c_filename, out_h_filename, mcu_file
        )
    )
    input_file_name = os.path.join(cubemxdir, mcu_file)
    out_path = os.path.join(
        cur_dir,
        "Arduino",
        os.path.splitext(mcu_file)[0][:7],
        os.path.splitext(mcu_file)[0],
    )
    output_c_filename = os.path.join(out_path, out_c_filename)
    output_h_filename = os.path.join(out_path, out_h_filename)
    if not (os.path.isdir(out_path)):
        os.makedirs(out_path)

    # open output file
    if os.path.isfile(output_c_filename):
        os.remove(output_c_filename)
    out_c_file = open(output_c_filename, "w", newline="\n")
    if os.path.isfile(output_h_filename):
        os.remove(output_h_filename)
    out_h_file = open(output_h_filename, "w", newline="\n")

    # open input file
    xml_mcu = parse(input_file_name)
    gpiofile = find_gpio_file()
    if gpiofile == "ERROR":
        print("Could not find GPIO file")
        quit()
    xml_gpio = parse(os.path.join(cubemxdirIP, "GPIO-" + gpiofile + "_Modes.xml"))

    parse_pins()
    sort_my_lists()
    print_header()
    print_all_lists()

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

    out_c_file.close()
    out_h_file.close()
