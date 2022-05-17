import os


RUNIC_DIRECTORY = "pages"
FILETYPE = ".runic"
PAGES_DIRECTORY = "public"


def isRunic(fn):
    return fn[-len(FILETYPE):] == FILETYPE


def readRunic(pages):
    if not pages:
        pages = (p[:-len(FILETYPE)] for p in filter(isRunic, os.listdir(RUNIC_DIRECTORY)))
    runic = []
    for pn in pages:
        try: 
            pc = readRunicFile(pn)
            runic.append((pn, pc))
        except: 
            print(f'Failed to read "{pn}{FILETYPE}"')

    return runic


def readRunicFile(pn):
    rawContent = ''
    with open(f'{RUNIC_DIRECTORY}/{pn}{FILETYPE}', 'r') as f:
        rawContent = f.read()
    return rawContent


def writeHtml(toWrite):
    for (p, c) in toWrite:
        fn = p + ".html"
        with open(f'{PAGES_DIRECTORY}/{fn}', 'w') as f:
            f.write(c)

