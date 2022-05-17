import re, json
from datetime import datetime
from publisher.fileio import readRunic, writeHtml


FILETYPE = '.runic'
DELIM = '\n\n'

TITLE = 'title'
START = 'start'
TYPE = 'type'
DESC = 'description'
KEYS = [TITLE, START, TYPE, DESC]
        
# Do <meta name="description" content="">
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="smh">
  <title>{title}</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="16x16.ico" type"image/ico" sizes="16x16">
  <link rel="icon" href="32x32.ico" type"image/ico" sizes="16x16">
</head>
<body>
  <main>
{content}
  </main>
</body>
</html>
"""

IMAGE = '<picture><img src={src}></picture>'

HEADER = '<h2>{}</h2>'

BLOCKQUOTE = '<blockquote><p>{}</p></blockquote>'

PARAGRAPH = '<p>{}</p>'

BLOCK_CODE = '<pre><code>{}</code></pre>'

CODE = '<code>{}</code>'

LINK = '<a href="{link}">{text}</a>'

ESSAY = '<li><a href="{link}">{title}</a><span class="date">{date}</span></li>'

PROJECT = '''
<li><span><a href="{link}">{title}</a><span class="description">{desc}</span></span><span class="date">{date}</span></li>
'''

def validateMeta(meta):
    notin = []
    for k in KEYS:
        if k not in meta:
            notin.append(f'"{k}"')
    if notin:
        plural = "s" if len(notin) > 1 else ""
        raise ValueError('Key{plural} {", ".join(notin)} not found in meta-data')


def readMeta(first):
    meta = json.loads(first)
    validateMeta(meta)
    meta[START] = datetime.strptime(meta[START], '%Y-%m-%d')
    return meta


def checkLink(text):
    if '[' not in text: 
        return text

    matches = re.finditer('\[(?P<text>.*?)\]\[(?P<link>.*?)\]', text)
    result = []
    curr = 0
    for m in matches:
        result.append(text[curr:m.start()])
        result.append(LINK.format(text= m.group('text'), link= m.group('link')))
        curr = m.end()
    result.append(text[curr:])

    return ''.join(result)


def processParagraph(b):

    temp = b.split('`')
    if len(temp) % 2 == 0:
        raise ValueError("Missing matching inline code")

    result = []
    for i in range(len(temp)):
        if i % 2:
            result.append(CODE.format(temp[i]))
        else:
            result.append(checkLink(temp[i]))

    return "".join(result)


def parseBlock(rune, block):

    block = block.replace('\n', ' ').strip()
    text = ''
    if rune == "&":
        text = PARAGRAPH.format(processParagraph(block))
    elif rune == ">":
        text = BLOCKQUOTE.format(block)
    elif rune == "#":
        text = HEADER.format(block)
    elif rune == "!":
        text = BLOCK_CODE.format(block)
    elif rune == "|":
        text = IMAGE.format(src=f'images/{block}')
    elif rune == "%":
        pass
    else:  
        raise ValueError(f'Unrecognized rune "{rune}"')
    return text


def runicToPages(runics):
    pages = []
    for r in runics:
        pn, pc = r
        try: 
            first, other = pc.split(DELIM, 1)
            meta = readMeta(first)
            pages.append((pn, htmlify(pn, meta, other), meta))
            # print("printing page")
            # print(pn)
            # print(htmlify(pn, meta, other))
        except json.decoder.JSONDecodeError: 
            print(f'Failed to read meta-data of {pn}{FILETYPE}')
        except ValueError as ve:
            print(f'{ve} in {pn}{FILETYPE}')

    return pages


def htmlify(pn, meta, pc):

    blocks = pc.strip().split(DELIM)
    content = []
    for block in blocks:
        if not block:
            continue
        rune, rest = block[0], block[1:]
        try:
            content.append(parseBlock(rune, rest))
        except ValueError as ve:
            print(ve)

    return HTML.format(title= pn, content= '\n'.join(content))

HOME_TITLE = 'smh'
UL = '''
<ul>
{elements}    
</ul>
'''


def getDate(p):
    _, __, meta = p
    return meta[START]


def home(pages):
    pages.sort(key=getDate, reverse=True)
    toc = []
    for p in pages:
        name, content, meta = p
        time = meta[START].strftime('%b %d, %Y')
        if meta['type'] == 'p':
            element = PROJECT.format(
                    date=time,
                    title=meta[TITLE], 
                    link=f"{name}.html",
                    desc=", " + meta['description'])
        else:
            element = ESSAY.format(
                    date=time,
                    link= f"{name}.html",
                    title=meta[TITLE])
        toc.append(element)
    home = UL.format(elements='\n'.join(toc))

    return HTML.format(title= HOME_TITLE, content= home)

INDEX = 'index'

# writeHtml, takes [(pagename, html content)]
def printBio(runicNames):
    runic = readRunic(runicNames)
    pages = runicToPages(runic)
    content = home(pages)
    pages = [(pn, pc) for (pn, pc, _) in pages]
    pages.append((INDEX, content))
    writeHtml(pages) 
    

# PIECE = '''
# <div class="piece">
#     <picture>
#         <img class="art" src="{logo}">
#     </picture>
#     <div class="didactic">
#         <h3 class="title">
#             {title}
#         </h3>
#         <p class="description">
#             {desc}
#         </p>
#     <!-- <div class="brush"><div> -->
#     </div>
# </div>
# '''

