# genpinmap

By default,this script is able to generate `PeripheralPins.c` and `PinNamesVar.h` for all xml files description available in
[STM32CubeMX](http://www.st.com/en/development-tools/stm32cubemx.html) directory defined in `config.json`.

After file generation, review them carefully and please report any issue
[here](https://github.com/stm32duino/Arduino_Tools/issues).

Once generated, you should comment a line if the pin is generated several times for the same IP or if the pin should not be used
(overlaid with some HW on the board, for instance).

usage: `python genpinmap_arduino.py [-h] [-l | -m xml]`

optional arguments:

  `-h, --help`         show this help message and exit<br>
  `-l, --list`         list available xml files description in [STM32CubeMX](http://www.st.com/en/development-tools/stm32cubemx.html)<br>
  `-m xml, --mcu xml`  Generate `PeripheralPins.c` and `PinNamesVar.h` for specified mcu xml file description
                       in [STM32CubeMX](http://www.st.com/en/development-tools/stm32cubemx.html).
					 **This xml file contains non alpha characters in its name, you should call it with double quotes**

All generated file are available under _./Arduino/<mcu_name>_ directory
