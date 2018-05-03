import argparse
import datetime
import fnmatch
import json
import os
import re
import sys
import textwrap
from xml.dom import minidom
from xml.dom.minidom import parse, Node
from argparse import RawTextHelpFormatter
mcu_file=""
mcu_list = []       #'name'
io_list = []        #'PIN','name'
adclist = []        #'PIN','name','ADCSignal'
daclist = []        #'PIN','name','DACSignal'
i2cscl_list = []    #'PIN','name','I2CSCLSignal'
i2csda_list = []    #'PIN','name','I2CSDASignal'
pwm_list = []       #'PIN','name','PWM'
uarttx_list = []    #'PIN','name','UARTtx'
uartrx_list = []    #'PIN','name','UARTrx'
uartcts_list = []   #'PIN','name','UARTcts'
uartrts_list = []   #'PIN','name','UARTrts'
spimosi_list = []   #'PIN','name','SPIMOSI'
spimiso_list = []   #'PIN','name','SPIMISO'
spissel_list = []   #'PIN','name','SPISSEL'
spisclk_list = []   #'PIN','name','SPISCLK'
cantd_list = []     #'PIN','name','CANTD'
canrd_list = []     #'PIN','name','CANRD'
eth_list = []       #'PIN','name','ETH'
qspi_list = []      #'PIN','name','QUADSPI'
syswkup_list = []   #'PIN','name','SYSWKUP'

def find_gpio_file():
    res = 'ERROR'
    itemlist = xml_mcu.getElementsByTagName('IP')
    for s in itemlist:
        a = s.attributes['Name'].value
        if "GPIO" in a:
            res = s.attributes['Version'].value
    return res

def get_gpio_af_num(pintofind, iptofind):
    if 'STM32F10' in mcu_file:
        return get_gpio_af_numF1(pintofind, iptofind)
    #DBG print ('pin to find ' + pintofind)
    i=0
    mygpioaf = 'NOTFOUND'
    for n in  xml_gpio.documentElement.childNodes:
        i += 1
        j = 0
        if n.nodeType == Node.ELEMENT_NODE:
            for firstlevel in n.attributes.items():
#                if 'PB7' in firstlevel:
                if pintofind ==  firstlevel[1]:
                    #DBG print (i , firstlevel)
                    #n = pin node found
                    for m in n.childNodes:
                        j += 1
                        k = 0
                        if m.nodeType == Node.ELEMENT_NODE:
                            for secondlevel in  m.attributes.items():
                                k += 1
#                                if 'I2C1_SDA' in secondlevel:
                                if iptofind in secondlevel:
                                    #DBG print (i, j,  m.attributes.items())
                                    # m = IP node found
                                    for p in m.childNodes:
                                        if p.nodeType == Node.ELEMENT_NODE:
                                            #p node of 'Specific parameter'
                                            #DBG print (i,j,k,p.attributes.items())
                                            for myc in p.childNodes:
                                                #DBG print (myc)
                                                if myc.nodeType == Node.ELEMENT_NODE:
                                                    #myc = node of ALTERNATE
                                                    for mygpioaflist in myc.childNodes:
                                                        mygpioaf += ' ' + mygpioaflist.data
                                                        #print (mygpioaf)
    if mygpioaf == 'NOTFOUND':
        print ('GPIO AF not found in ' + gpiofile + ' for ' + pintofind + ' and the IP ' + iptofind)
        #quit()
    return mygpioaf.replace('NOTFOUND ', '')

def get_gpio_af_numF1(pintofind, iptofind):
    #print ('pin to find ' + pintofind + ' ip to find ' + iptofind)
    i=0
    mygpioaf = 'NOTFOUND'
    for n in  xml_gpio.documentElement.childNodes:
        i += 1
        j = 0
        if n.nodeType == Node.ELEMENT_NODE:
            for firstlevel in n.attributes.items():
                #print ('firstlevel ' , firstlevel)
#                if 'PB7' in firstlevel:
                if pintofind ==  firstlevel[1]:
                    #print ('firstlevel ' , i , firstlevel)
                    #n = pin node found
                    for m in n.childNodes:
                        j += 1
                        k = 0
                        if m.nodeType == Node.ELEMENT_NODE:
                            for secondlevel in  m.attributes.items():
                                #print ('secondlevel ' , i, j, k , secondlevel)
                                k += 1
#                                if 'I2C1_SDA' in secondlevel:
                                if iptofind in secondlevel:
                                    # m = IP node found
                                    #print (i, j,  m.attributes.items())
                                    for p in m.childNodes:
                                        #p node 'RemapBlock'
                                        if p.nodeType == Node.ELEMENT_NODE and p.hasChildNodes() == False:
                                            mygpioaf += ' AFIO_NONE'
                                        else:
                                            for s in p.childNodes:
                                                if s.nodeType == Node.ELEMENT_NODE:
                                                    #s node 'Specific parameter'
                                                    #DBG print (i,j,k,p.attributes.items())
                                                    for myc in s.childNodes:
                                                        #DBG print (myc)
                                                        if myc.nodeType == Node.ELEMENT_NODE:
                                                            #myc = AF value
                                                            for mygpioaflist in myc.childNodes:
                                                                mygpioaf += ' ' + mygpioaflist.data.replace("__HAL_", "").replace("_REMAP", "")
                                                                #print mygpioaf
    if mygpioaf == 'NOTFOUND':
        print ('GPIO AF not found in ' + gpiofile + ' for ' + pintofind + ' and the IP ' + iptofind + ' set as AFIO_NONE')
        mygpioaf = 'AFIO_NONE'
    return mygpioaf.replace('NOTFOUND ', '')


def store_pin (pin, name):
    #store pin I/O
    p = [pin, name]
    io_list.append(p)

#function to store ADC list
def store_adc (pin, name, signal):
    adclist.append([pin,name,signal])

#function to store DAC list
def store_dac (pin, name, signal):
    daclist.append([pin,name,signal])

#function to store I2C list
def store_i2c (pin, name, signal):
    #is it SDA or SCL ?
    if "_SCL" in signal:
        i2cscl_list.append([pin,name,signal])
    if "_SDA" in signal:
        i2csda_list.append([pin,name,signal])

#function to store timers
def store_pwm(pin, name, signal):
    if "_CH" in signal:
        pwm_list.append([pin,name,signal])

#function to store Uart pins
def store_uart(pin, name, signal):
    if "_TX" in signal:
        uarttx_list.append([pin,name,signal])
    if "_RX" in signal:
        uartrx_list.append([pin,name,signal])
    if "_CTS" in signal:
        uartcts_list.append([pin,name,signal])
    if "_RTS" in signal:
        uartrts_list.append([pin,name,signal])

#function to store SPI pins
def store_spi(pin, name, signal):
    if "_MISO" in signal:
        spimiso_list.append([pin,name,signal])
    if "_MOSI" in signal:
        spimosi_list.append([pin,name,signal])
    if "_SCK" in signal:
        spisclk_list.append([pin,name,signal])
    if "_NSS" in signal:
        spissel_list.append([pin,name,signal])

#function to store CAN pins
def store_can(pin, name, signal):
    if "_RX" in signal:
        canrd_list.append([pin,name,signal])
    if "_TX" in signal:
        cantd_list.append([pin,name,signal])

#function to store ETH list
def store_eth (pin, name, signal):
    eth_list.append([pin,name,signal])

#function to store QSPI pins
def store_qspi (pin, name, signal):
    qspi_list.append([pin,name,signal])

#function to store SYS pins
def store_sys (pin, name, signal):
    if "_WKUP" in signal:
        syswkup_list.append([pin,name,signal])

def print_header():
    s =  ("""/*
 *******************************************************************************
 * Copyright (c) %i, STMicroelectronics
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
 * Automatically generated from %s
 */
#include "Arduino.h"
#include "%s.h"

/* =====
 * Note: Commented lines are alternative possibilities which are not used per default.
 *       If you change them, you will have to know what you do
 * =====
 */
""" % (datetime.datetime.now().year, os.path.basename(input_file_name), re.sub('\.c$', '', out_c_filename)))
    out_c_file.write( s)

def print_all_lists():
    if print_list_header("ADC", "ADC", adclist, "ADC"):
        print_adc()
    if print_list_header("DAC", "DAC", daclist, "DAC"):
        print_dac()
    if print_list_header("I2C", "I2C_SDA", i2csda_list, "I2C"):
        print_i2c(i2csda_list)
    if print_list_header("", "I2C_SCL", i2cscl_list, "I2C"):
        print_i2c(i2cscl_list)
    if print_list_header("PWM", "PWM", pwm_list, "TIM"):
        print_pwm()
    if print_list_header("SERIAL", "UART_TX", uarttx_list, "UART"):
        print_uart(uarttx_list)
    if print_list_header("", "UART_RX", uartrx_list, "UART"):
        print_uart(uartrx_list)
    if print_list_header("", "UART_RTS", uartrts_list, "UART"):
        print_uart(uartrts_list)
    if print_list_header("", "UART_CTS", uartcts_list, "UART"):
        print_uart(uartcts_list)
    if print_list_header("SPI", "SPI_MOSI", spimosi_list, "SPI"):
        print_spi(spimosi_list)
    if print_list_header("", "SPI_MISO", spimiso_list, "SPI"):
        print_spi(spimiso_list)
    if print_list_header("", "SPI_SCLK", spisclk_list, "SPI"):
        print_spi(spisclk_list)
    if print_list_header("", "SPI_SSEL", spissel_list, "SPI"):
        print_spi(spissel_list)
    if print_list_header("CAN", "CAN_RD", canrd_list, "CAN"):
        print_can(canrd_list)
    if print_list_header("", "CAN_TD", cantd_list, "CAN"):
        print_can(cantd_list)
    if print_list_header("ETHERNET", "Ethernet", eth_list, "ETH"):
        print_eth()
    if print_list_header("QUADSPI", "QUADSPI", qspi_list, "QSPI"):
        print_qspi()
    # Print specific PinNames
    print_syswkup()

def print_list_header(comment, name, l, switch):
    if len(l)>0:
        if comment:
            s = ("""
//*** %s ***
""") % comment
        else:
            s = ""
        s += ("""
#ifdef HAL_%s_MODULE_ENABLED
const PinMap PinMap_%s[] = {
""") % (switch, name)
    else:
        if comment:
            s = ("""
//*** %s ***
""") % comment
        else:
            s = ""
        s+=("""
//*** No %s ***
""") % name
    out_c_file.write(s)
    return len(l)

def print_adc():
    # Check GPIO version (alternate or not)
    s_pin_data = 'STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, '
    for p in adclist:
        if "IN" in p[2]:
            s1 = "%-12s" % ("    {" + p[0] + ',')
            a = p[2].split('_')
            inst = a[0].replace("ADC", "")
            if len(inst) == 0:
                inst = '1' #single ADC for this product
            s1 += "%-7s" % ('ADC' + inst + ',')
            chan = re.sub('IN[N|P]?', '', a[1])
            s1 += s_pin_data + chan
            s1 += ', 0)}, // ' + p[2] + '\n'
            out_c_file.write(s1)
    out_c_file.write( """    {NC,    NP,    0}
};
#endif
""")

def print_dac():
    for p in daclist:
        b=p[2]
        s1 = "%-12s" % ("    {" + p[0] + ',')
        #2nd element is the DAC signal
        if b[3] == '_': # 1 DAC in this chip
            s1 += 'DAC1, STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, ' + b[7] + ', 0)}, // ' + b + '\n'
        else:
            s1 += 'DAC' + b[3] + ', STM_PIN_DATA_EXT(STM_MODE_ANALOG, GPIO_NOPULL, 0, ' + b[8] + ', 0)}, // ' + b + '\n'
        out_c_file.write(s1)
    out_c_file.write( """    {NC,   NP,    0}
};
#endif
""")

def print_i2c(l):
    for p in l:
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the I2C XXX signal
            b = p[2].split('_')[0]
            s1 += b[:len(b)-1] + b[len(b)-1] + ', STM_PIN_DATA(STM_MODE_AF_OD, GPIO_NOPULL, '
            r = result.split(' ')
            for af in r:
                s2 = s1 + af  + ')},\n'
                out_c_file.write(s2)
    out_c_file.write( """    {NC,    NP,    0}
};
#endif
""")

def print_pwm():
    for p in pwm_list:
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the PWM signal
            a = p[2].split('_')
            inst = a[0]
            if len(inst) == 3:
                inst += '1'
            s1 += "%-8s" % (inst + ',')
            chan = a[1].replace("CH", "")
            if chan.endswith('N'):
                neg = ', 1'
                chan = chan.strip('N')
            else:
                neg = ', 0'
            s1 += 'STM_PIN_DATA_EXT(STM_MODE_AF_PP, GPIO_PULLUP, '
            r = result.split(' ')
            for af in r:
                s2 = s1 + af + ', ' + chan + neg + ')},  // ' + p[2] + '\n'
                out_c_file.write(s2)
    out_c_file.write( """    {NC,    NP,    0}
};
#endif
""")

def print_uart(l):
    for p in l:
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the UART_XX signal
            b=p[2].split('_')[0]
            s1 += "%-9s" % (b[:len(b)-1] +  b[len(b)-1:] + ',')
            if 'STM32F10' in mcu_file and l == uartrx_list:
                s1 += 'STM_PIN_DATA(STM_MODE_INPUT, GPIO_PULLUP, '
            else:
                s1 += 'STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, '
            r = result.split(' ')
            for af in r:
                s2 = s1 + af  + ')},\n'
                out_c_file.write(s2)
    out_c_file.write( """    {NC,    NP,    0}
};
#endif
""")

def print_spi(l):
    for p in l:
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the SPI_XXXX signal
            instance=p[2].split('_')[0].replace("SPI", "")
            s1 += 'SPI' + instance + ', STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, '
            r = result.split(' ')
            for af in r:
                s2 = s1 + af  + ')},\n'
                out_c_file.write(s2)
    out_c_file.write( """    {NC,    NP,    0}
};
#endif
""")

def print_can(l):
    for p in l:
        b=p[2]
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the CAN_XX signal
            instance = p[2].split('_')[0].replace("CAN", "")
            if len(instance) == 0:
                instance = '1'
            if 'STM32F10' in mcu_file and l == canrd_list:
                s1 += 'CAN' + instance + ', STM_PIN_DATA(STM_MODE_INPUT, GPIO_NOPULL, '
            else:
                s1 += 'CAN' + instance + ', STM_PIN_DATA(STM_MODE_AF_PP, GPIO_NOPULL, '
            r = result.split(' ')
            for af in r:
                s2 = s1 + af  + ')},\n'
                out_c_file.write(s2)
    out_c_file.write( """    {NC,    NP,    0}
};
#endif
""")

def print_eth():
    prev_s = ''
    for p in eth_list:
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the ETH_XXXX signal
            s1 += 'ETH, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, ' + result +')},'
            #check duplicated lines, only signal differs
            if (prev_s == s1):
                s1 = '|' + p[2]
            else:
                if len(prev_s)>0:
                    out_c_file.write('\n')
                prev_s = s1
                s1 += '  // ' + p[2]
            out_c_file.write(s1)
    out_c_file.write( """\n    {NC,    NP,    0}
};
#endif
""")

def print_qspi():
    prev_s = ''
    for p in qspi_list:
        result = get_gpio_af_num(p[1], p[2])
        if result != 'NOTFOUND':
            s1 = "%-12s" % ("    {" + p[0] + ',')
            #2nd element is the QUADSPI_XXXX signal
            s1 += 'QUADSPI, STM_PIN_DATA(STM_MODE_AF_PP, GPIO_PULLUP, ' + result +')},'
            #check duplicated lines, only signal differs
            if (prev_s == s1):
                s1 = '|' + p[2]
            else:
                if len(prev_s)>0:
                    out_c_file.write('\n')
                prev_s = s1
                s1 += '  // ' + p[2]
            out_c_file.write(s1)
    out_c_file.write( """\n    {NC,    NP,    0}
};
#endif
""")

def print_syswkup():
    out_h_file.write("    /* SYS_WKUP */\n")
    # H7xx and F446 start from 0, inc by 1
    num = syswkup_list[0][2].replace("SYS_WKUP", "")
    inc = 0
    if num == '0':
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
            syswkup_list.insert(i,['NC', 'NC_' + str(x), 'SYS_WKUP'+ str(x)])
        i += 1
    # print pin name under switch
    for p in syswkup_list:
        num = p[2].replace("SYS_WKUP", "")
        if len(num) == 0:
            s1 = '#ifdef PWR_WAKEUP_PIN1\n'
            s1 += '    SYS_WKUP1' #single SYS_WKUP for this product
        else:
            s1 = '#ifdef PWR_WAKEUP_PIN%i\n' % (int(num) + inc)
            s1 += '    SYS_WKUP' + str(int(num) + inc)
        s1 += ' = ' + p[0] + ','
        if (inc == 1) and (p[0] != 'NC'):
            s1 += ' /* ' + p[2] + ' */'
        s1 += '\n#endif\n'
        out_h_file.write(s1)

tokenize = re.compile(r'(\d+)|(\D+)').findall
def natural_sortkey(list_2_elem):
    return tuple(int(num) if num else alpha for num, alpha in tokenize(list_2_elem[0]))

def natural_sortkey2(list_2_elem):
    return tuple(int(num) if num else alpha for num, alpha in tokenize(list_2_elem[2]))

def sort_my_lists():
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
    qspi_list.sort(key=natural_sortkey)
    syswkup_list.sort(key=natural_sortkey2)

def clean_all_lists():
    del io_list[:]
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
    del qspi_list[:]
    del syswkup_list[:]

def parse_pins():
    print (" * Getting pins per Ips...")
    pinregex=r'^(P[A-Z][0-9][0-5]?)'
    itemlist = xml_mcu.getElementsByTagName('Pin')
    for s in itemlist:
        m = re.match(pinregex, s.attributes['Name'].value)
        if m:
            pin = m.group(0)[:2] + '_' + m.group(0)[2:] # pin formatted P<port>_<number>: PF_O
            name = s.attributes['Name'].value.strip()   # full name: "PF0 / OSC_IN"
            if s.attributes['Type'].value == "I/O":
                store_pin(pin, name)
            else:
                continue
            siglist = s.getElementsByTagName('Signal')
            for a in siglist:
                sig = a.attributes['Name'].value.strip()
                if "ADC" in sig:
                    store_adc(pin, name, sig)
                if all(["DAC" in sig, "_OUT" in sig]):
                    store_dac(pin, name, sig)
                if "I2C" in sig:
                    store_i2c(pin, name, sig)
                if re.match('^TIM', sig) is not None: #ignore HRTIM
                    store_pwm(pin, name, sig)
                if re.match('^(LPU|US|U)ART', sig) is not None:
                    store_uart(pin, name, sig)
                if "SPI" in sig:
                    store_spi(pin, name, sig)
                if "CAN" in sig:
                    store_can(pin, name, sig)
                if "ETH" in sig:
                    store_eth(pin, name, sig)
                if "QUADSPI" in sig:
                    store_qspi(pin, name, sig)
                if "SYS_" in sig:
                    store_sys(pin, name, sig)
# main
cur_dir = os.getcwd()
out_c_filename = 'PeripheralPins.c'
out_h_filename = 'PinNamesVar.h'
config_filename = 'config.json'

try:
    config_file = open(config_filename, "r")
except IOError:
    print("Please set your configuration in '%s' file" % config_filename)
    config_file = open(config_filename, "w")
    if sys.platform.startswith('win32'):
        print("Platform is Windows")
        cubemxdir = 'C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeMX\\db\\mcu'
    elif sys.platform.startswith('linux'):
        print("Platform is Linux")
        cubemxdir = os.getenv("HOME")+'/STM32CubeMX/db/mcu'
    elif sys.platform.startswith('darwin'):
        print("Platform is Mac OSX")
        cubemxdir = '/Applications/STMicroelectronics/STM32CubeMX.app/Contents/Resources/db/mcu'
    else:
        print("Platform unknown")
        cubemxdir = '<Set CubeMX install directory>/db/mcu'
    config_file.write(json.dumps({"CUBEMX_DIRECTORY":cubemxdir}))
    config_file.close()
    exit(1)

config = json.load(config_file)
config_file.close()
cubemxdir = config["CUBEMX_DIRECTORY"]

# by default, generate for all mcu xml files description
parser = argparse.ArgumentParser(
    description=textwrap.dedent('''\
By default, generate %s and %s for all xml files description available in
STM32CubeMX directory defined in '%s':
\t%s''' % (out_c_filename, out_h_filename, config_filename, cubemxdir)),
    epilog=textwrap.dedent('''\
After files generation, review them carefully and please report any issue to github:
\thttps://github.com/stm32duino/Arduino_Tools/issues\n
Once generated, you have to comment a line if the pin is generated several times
for the same IP or if the pin should not be used (overlaid with some HW on the board,
for instance)'''),
    formatter_class=RawTextHelpFormatter)
group = parser.add_mutually_exclusive_group()
group.add_argument("-l", "--list", help="list available xml files description in STM32CubeMX", action="store_true")
group.add_argument("-m", "--mcu", metavar='xml', help=textwrap.dedent('''\
Generate %s and %s for specified mcu xml file description
in STM32CubeMX. This xml file contains non alpha characters in
its name, you should call it with double quotes''' % (out_c_filename, out_h_filename)))
args = parser.parse_args()

if not(os.path.isdir(cubemxdir)):
    print ("\n ! ! ! Cube Mx seems not to be installed or not at the requested location")
    print ("\n ! ! ! please check the value you set for 'CUBEMX_DIRECTORY' in '%s' file" % config_filename)
    quit()

cubemxdirIP = os.path.join(cubemxdir, 'IP')

if args.mcu:
    #check input file exists
    if not(os.path.isfile(os.path.join(cubemxdir, args.mcu))):
        print ("\n ! ! ! " + args.mcu + " file not found")
        print ("\n ! ! ! Check in " + cubemxdir + " the correct name of this file")
        print ("\n ! ! ! You may use double quotes for this file if it contains special characters")
        quit()
    mcu_list.append(args.mcu)
else:
    mcu_list=fnmatch.filter(os.listdir(cubemxdir), 'STM32*.xml')

if args.list:
    print("Available xml files description: %i" % len(mcu_list))
    for f in mcu_list:
        print(f)
    quit()

for mcu_file in mcu_list:
    print("Generating %s and %s for '%s'..." % (out_c_filename, out_h_filename, mcu_file))
    input_file_name = os.path.join(cubemxdir, mcu_file)
    out_path = os.path.join(cur_dir, 'Arduino', os.path.splitext(mcu_file)[0])
    output_c_filename = os.path.join(out_path, out_c_filename)
    output_h_filename = os.path.join(out_path, out_h_filename)
    if not(os.path.isdir(out_path)):
        os.makedirs(out_path)

    #open output file
    if (os.path.isfile(output_c_filename)):
        #print (" * Requested %s file already exists and will be overwritten" % out_c_filename)
        os.remove(output_c_filename)
    out_c_file = open(output_c_filename, 'w')
    if (os.path.isfile(output_h_filename)):
        #print (" * Requested %s file already exists and will be overwritten" % out_h_filename)
        os.remove(output_h_filename)
    out_h_file = open(output_h_filename, 'w')

    #open input file
    xml_mcu = parse(input_file_name)
    gpiofile = find_gpio_file()
    if gpiofile == 'ERROR':
        print("Could not find GPIO file")
        quit()
    xml_gpio = parse(os.path.join(cubemxdirIP, 'GPIO-' + gpiofile + '_Modes.xml'))

    parse_pins()
    sort_my_lists()
    print_header()
    print_all_lists()

    nb_pin = (len(io_list))
    print (" * I/O pins found: %i" % nb_pin)
    print ("done\n")
    clean_all_lists()

    out_c_file.close()
    out_h_file.close()
