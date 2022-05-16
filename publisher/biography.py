# TODO: need to eventually remove json dependency
# TODO: CHANGE SO NO GLOBAL VARS
# TODO: Escape all reserved chars e.g. >, <, &, "

import sys, os
from pages import printBio

# bio print 
# bio burn
# bio pub

PUBLISH = 'pub'
BURN = 'burn'
PRINT = 'print'

DIR_TO_BURN = '../public'

def main():
    _, inst, *pages = sys.argv
    if inst == PRINT:
        printBio(pages)
        print("Finished printing pages!")
    elif inst == BURN:
        files = os.listdir(DIR_TO_BURN)
        for file in filter(lambda x: x.endswith('.html'), files):
            try: 
                path = os.path.join(DIR_TO_BURN, file)
                os.remove(path)
            except OSError:
                print(f'Could not burn {file}')


main()
