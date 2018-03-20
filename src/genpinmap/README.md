# genpinmap

This script is able to generate the `PeripheralPins.c` for a specific board.

After file generation, review it carefully and please report any issue
[here](https://github.com/stm32duino/Arduino_Tools/issues)

Once generated, you should comment a line if the pin is generated<br>
several times for the same IP or if the pin should not be used<br>
(overlaid with some HW on the board, for instance)

Usage: `python genpinmap_arduino.py <Name> <product xml file name>`
   - `<Name>` is the name of the directory where `PeripheralPins.c` will be generated under _./Arduino_ directory
   - `<product xml file name>` is the STM32 file description in [STM32CubeMX](http://www.st.com/en/development-tools/stm32cubemx.html)

**!! This xml file contains non alpha characters in its name, you should call it with quotes**
