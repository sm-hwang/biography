import re, json

DELIM = '\n'

TITLE = 'title'
START = 'start'
TYPE = 'type'
DESC = 'description'
KEYS = [TITLE, START, TYPE, DESC]
        
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

HEADER = '<h2>{}</h2>'

BLOCKQUOTE = '<blockquote><p>{}</p></blockquote>'

PARAGRAPH = '<p>{}</p>'

BLOCK_CODE = 'pre><code>{}</code></pre'

LINK = '<a href="{link}">{text}</a>'

ESSAY = '<li><a href="{link}">{title}</a><span class="date">{date}</span></li>'

PROJECT = '''
<li><span><a href="{link}">{title}</a><span class="description">{desc}</span></span><span class="date">{date}</span></li>
'''

def readMeta(first):
    meta = json.loads(first)
    validateMeta(meta)
    meta[START] = datetime.strptime(meta[START], '%Y-%m-%d')
    return meta

def validateMeta(meta):
    notin = []
    for k in KEYS:
        if k not in meta:
            notin.append(f'"{k}"')
    if notin:
        raise Exception(*notin)


def processParagraph(b):

    temp = b.split('`')
    if len(temp) % 2 == 0:
        raise ValueError("Missing matching inline code")

    result = []
    for i in range(len(temp)):
        if i % 2:
            result.append(f'<code>{temp[i]}</code>')
        else:
            result.append(checkLink(temp[i]))

    return "".join(result)


def parseBlock(block):

    block = block.replace('\n', ' ').strip()
    text = ''
    if t == "&":
        text = PARAGRAPH.format(processParagraph(b))
    elif t == ">":
        text = BLOCKQUOTE.format(b)
    elif t == "#":
        text = HEADER.format(b)
    elif t == "!":
        text = BLOCK_CODE.format(b)
    elif t == "|":
        text = IMAGE.format(b)
    elif t == "%":
        pass
    else: # throw a fit 
        raise ValueError('Unrecognized rune "{ve}"')
    return text

def htmlify(pn, meta, pc):

    blocks = pc.strip().split(DELIM)
    content = []
    for block in blocks:
        if not block:
            continue

        content.append(parseBlock(block))

    return HTML.format(title= pn, content= DELIM.join(content))

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
