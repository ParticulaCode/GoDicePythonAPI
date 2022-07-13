
# GoDice Python API (with demo)

## Overview

Use the GoDice Python API to integrate GoDice functionality into your own Python applications

Here are some of the things that you can do with the GoDice Python API:

* Turn ON/OFF GoDice RGB Leds
* Ask for the die Color (dots color)
* Ask for the die battery level
* Get differernt notifications reagrding the die state (Rolling or Stable and get the outcome number)
* Use and configure different shells (D6, D20, D12 etc.)

To run the demo (that uses the API) make sure you have the Bleak library installed and run main.py as following:
``` console
python main.py
```

Then enter the index of the GoDice you want to connect (or click Enter to connect to all available dice).
Once connected you will start get notification from the connected dice (Rolling, Stable, etc...)

 Dependencies Installation
------------
The GoDice Python API is dependent on the [Bleak](https://github.com/hbldh/bleak) library for bluetooth (BLE) communication with the dice

You can install bleak by using this command:

    $ pip install bleak
   or from sources ([Bleak installation docs](https://bleak.readthedocs.io/en/latest/installation.html))

Usage
=====
**See Main.py for more examples of usage**

Discovering and connecting
----
To discover dice using GoDice library:
```python
from godice import *

# Example how to discover GoDice bluetooth devices  
def main():  
  
	# Discovering GoDice devices using BLE  
	dice_devices = discover_dice()
```

Connecting to a die and creating a die object (use "create_dice" and pass it a die device):
```python
My_die = create_dice(dice_devices[0])
```

Messages
-----------
Activating LEDs:

```python
# Turn On/Off RGB LEDs, will turn off if led1 and led2 are None
# led1 - a list to control the 1st LED in the following format '[R, G, B]'
#        where R, G, and B are numbers in the range of 0-255
# led2 - same as led1 fot the second led

set_led(led1: list, led2: list)
```

```python
# Pulses the die's leds for set time
# pulse_count - How many pulses
# on_time - How much time to spend on (units of 10 ms)
# off_time - How much time to spend off (units of 10 ms)
# rgb - List of RGB values to set die to pulse to

pulse_led(pulse_count, on_time, off_time, rgb)
```

Requests
-----------
(Instanced methods of GoDice object)
```python
# Sends request for color of die
send_color_request()
```


```python
# Changes die type (shell)
# new_die_type - DieType Enum:
#	D6 = 0 (default)
#	D20 = 1,
#	D10 = 2,
#	D10x = 3,
#	D4 = 4,
#	D8 = 5,
#	D12 = 6
# For example: set_die_type(DieType.D20)

set_die_type(new_die_type)  
```

Reading responses
-----------
Each die object has a "result_queue" attribute.
Whenever a response/message is sent to the die, it's resposne code (if it has one) and it's value placed in the result queue as a tuple.

Example for iterating throught the queue:
```python
while not die_object.result_queue.empty():

	current_result = die_object.result_queue.get()
	
	result_code = current_result[0]
	if result_code == "S":
		value = current_result[1]
		# Do something
	.
	.
	.
```

**Possible 'Results In Queue' (tuples)**

("R" - On roll start, No value)

("S" - Stable event, Value of die)

("TS" - Tilt stable event, Value of die)

("MS" - Move stable event, Value of die)

("FS" - Fake stable event, Value of die)

("B" - Battery response, Battery charge precent: 0-100)

("C" - Color response, ID of color of die: 0-5)

```python
# Black		0
# Red		1
# Green		2
# Blue		3
# Yellow	4
# Orange	5
```
