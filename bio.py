#!/usr/bin/env python3
# TODO: need to eventually remove json dependency

import sys, os
from prepress import print_biography, DRAFT_DIR, DRAFT_EXT

# bio print 
# bio burn
# bio pub

# Command constants
CMD_PUBLISH = 'pub'
CMD_BURN = 'burn'
CMD_PRINT = 'print'

# Directory constants
BURN_DIR = "public"
PRESERVED_FILES = {'404.html'}  # Files that should not be deleted

def main():

    if len(sys.argv) < 2:
        print("Usage: bio <command> [args...]")
        return

    _, command = sys.argv
    if command == CMD_PRINT:
        # Get all .md files in the content directory
        page_names = [p[:-len(DRAFT_EXT)] for p in os.listdir(DRAFT_DIR)
                    if p.endswith(DRAFT_EXT)]

        print_biography(page_names)
        print("Finished printing pages!")
    elif command == CMD_BURN:
        # Get all HTML files except preserved ones
        html_files = [f for f in os.listdir(BURN_DIR)
                     if f.endswith('.html') and f not in PRESERVED_FILES]

        if not html_files:
            print("No HTML files to burn")
            return

        # Show files to be deleted and ask for confirmation
        print(f"Found {len(html_files)} HTML files to burn:")
        for filename in html_files:
            print(f"  - {filename}")

        confirm = input("\nAre you sure you want to burn these files? [y/N] ").lower()
        if confirm != 'y':
            print("Burn cancelled")
            return

        # Delete the files
        for filename in html_files:
            try:
                file_path = os.path.join(BURN_DIR, filename)
                os.remove(file_path)
                print(f"Burned {filename}")
            except OSError as e:
                print(f"Could not burn {filename}: {e}")
        
        print(f"Finished burning {len(html_files)} files")

if __name__ == "__main__":
    main()
