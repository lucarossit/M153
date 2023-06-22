from os import system
# Small file with helper functions I wrote to make life easier, so far only 1 though...

def pause(clearScreen = False):
    """
    Tiny helper function that pauses the console until a dummy input is given by pressing enter.
    """
    print('Press enter to continue...')
    dummy = input()
    if clearScreen == True:
        system('cls')