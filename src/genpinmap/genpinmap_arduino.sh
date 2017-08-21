#!/bin/bash -
#===============================================================================
#
#          FILE: genpinmap_arduino.sh
#
#         USAGE: ./genpinmap_arduino.sh
#
#   DESCRIPTION:
#
#       OPTIONS: None
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: fpistm
#  ORGANIZATION: STMicroelectronics
#       CREATED: 03/07/17 08:42
#      REVISION: 1.0
#===============================================================================

set -o nounset                              # Treat unset variables as an error

# See xml file name in <STM32CubeMX install dir>\db\mcu

python genpinmap_arduino.py NUCLEO_F030R8 "STM32F030R8Tx.xml"
python genpinmap_arduino.py NUCLEO_F091RC "STM32F091R(B-C)Tx.xml"
python genpinmap_arduino.py DISCO_F100RB "STM32F100R(8-B)Tx.xml"
python genpinmap_arduino.py NUCLEO_F103RB "STM32F103R(8-B)Tx.xml"
python genpinmap_arduino.py NUCLEO_F207ZG "STM32F207Z(C-E-F-G)Tx.xml"
python genpinmap_arduino.py NUCLEO_F303RE "STM32F303R(D-E)Tx.xml"
python genpinmap_arduino.py NUCLEO_F401RE "STM32F401R(D-E)Tx.xml"
python genpinmap_arduino.py NUCLEO_F411RE "STM32F411R(C-E)Tx.xml"
python genpinmap_arduino.py NUCLEO_F429ZI "STM32F429Z(E-G-I)Tx.xml"
python genpinmap_arduino.py DISCO_F407G   "STM32F407V(E-G)Tx.xml"
python genpinmap_arduino.py DISCO_F746NG  "STM32F746N(E-G)Hx.xml"
python genpinmap_arduino.py NUCLEO_L053R8 "STM32L053R(6-8)Tx.xml"
python genpinmap_arduino.py NUCLEO_L152RE "STM32L152RETx.xml"
python genpinmap_arduino.py NUCLEO_L432KC "STM32L432K(B-C)Ux.xml"
python genpinmap_arduino.py DISCO_L475VG  "STM32L475V(C-E-G)Tx.xml"
python genpinmap_arduino.py NUCLEO_L476RG "STM32L475R(C-E-G)Tx.xml"

python genpinmap_arduino.py BLUEPILL_F103C8 "STM32F103C(8-B)Tx.xml"
#same for MAPLEMINI_F103CB
python genpinmap_arduino.py MAPLEMINI_F103CB "STM32F103C(8-B)Tx.xml"
