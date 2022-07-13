import time
from godice import *


def main():

    print("Scanning for GoDice devices...")
    dice_devices = discover_dice()
    while len(dice_devices) < 1:
        print("Found no go dice, press Enter to scan again")
        input()
        dice_devices = discover_dice()

    # Printing all available dice to the user
    for i in range(len(dice_devices)):
        print("Index: {} - Die: {}".format(i, dice_devices[i]))

    connected_dice = []

    # Letting user choose die/dice
    inp = input("Enter the index to connect to or press enter to connect to all available dice:\n")
    while (inp.isdigit() and (0 > int(inp) or int(inp) > len(dice_devices))) and (not(inp == "")):
        inp = input("Enter the index to connect to or press 'Enter' to connect to all available dice:\n")

    if inp.isdigit():
        # Single die
        go_dice = create_dice(dice_devices[int(inp)])
        connected_dice.append(go_dice)
    else:
        # Connect to all available dice
        for die in dice_devices:
            try:
                die_object = create_dice(die)
                connected_dice.append(die_object)
            except asyncio.exceptions.TimeoutError:
                print("Timed out")            

    # Get information from each connected die
    for connected_die in connected_dice:

        # Waiting until first die is initiated
        while not connected_die.initiated:
            time.sleep(1)

        # Turning the LED blue for 2 seconds
        connected_die.set_led([0, 0, 255], [0, 0, 255])
        time.sleep(2)
        connected_die.set_led(None, None)

        # Pulsing LED green
        connected_die.pulse_led(3, 40, 50, [0, 255, 0])

        # Requesting battery level
        connected_die.send_battery_request()

        # Requesting color
        connected_die.send_color_request()

        # Change die to D20 (example)
        #connected_die.set_die_type(DieType.D20)

    # Main die loop
    while True:
        # Iterating through each connected die
        for go_dice in connected_dice:
            # Checking each die's queue
            while not go_dice.result_queue.empty():
                index = connected_dice.index(go_dice)
                result = go_dice.result_queue.get()

                # Rolling event
                if result[0] == "R":
                    print("Index " + str(index) + " - Rolling...")
                    
                # Move stable event
                elif "MS" in result[0]:
                    print("Index " + str(index) + " - Move Stable: " + str(result[1]))
                    
                # Stable event
                elif "S" in result[0]:
                    print("Index " + str(index) + " - Stable, Rolled: " + str(result[1]))
                    
                # Tilt Stable event
                elif "TS" in result[0]:
                    print("Index " + str(index) + " - Tilt, Rolled: " + str(result[1]))
                    
                # Fake Stable event
                elif "FS" in result[0]:
                    print("Index " + str(index) + " - Fake, Rolled: " + str(result[1]))
                    
                # Battery level event
                elif "B" in result[0]:
                    print("Index " + str(index) + " - Battery Level: ", str(result[1]))
                    
                # Die Color event
                elif "C" in result[0]:
                    print("Index " + str(index) + " - Color: ", str(result[1]))


if __name__ == '__main__':
    main()
