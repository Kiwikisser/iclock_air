#! /usr/bin/python2

import time
import sys

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()

    print("Bye!")
    sys.exit()

#ck dt
hx1 = HX711(5, 6)
hx2 = HX711(20, 16)
hx3 = HX711(19, 13)
hx4 = HX711(22, 27)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx1.set_reading_format("MSB", "MSB")
hx2.set_reading_format("MSB", "MSB")
hx3.set_reading_format("MSB", "MSB")
hx4.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
# if 418 grams i 1237, then 1000 grams is 1237 / 418 = 2.959
#hx.set_reference_unit(113)
hx1.set_reference_unit(2.959)
hx2.set_reference_unit(2.959)
hx3.set_reference_unit(2.959)
hx4.set_reference_unit(2.959)

hx1.reset()
hx2.reset()
hx3.reset()
hx4.reset()

hx1.tare()
hx2.tare()
hx3.tare()
hx4.tare()

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.

        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string

        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val1 = hx1.get_weight(5)
        val2 = hx2.get_weight(5)
        val3 = hx3.get_weight(5)
        val4 = hx4.get_weight(5)
        print("Sensor 1: %s,\t 2: %s,\t 3: %s,\t 4: %s" % (val1, val2, val3, val4))

        # To get weight from both channels (if you have load cells hooked up
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print "A: %s  B: %s" % ( val_A, val_B )

        hx1.power_down()
        hx1.power_up()
        hx2.power_down()
        hx2.power_up()
        hx3.power_down()
        hx3.power_up()
        hx4.power_down()
        hx4.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
