# TODO: need to eventually remove json dependency
import json
from datetime import datetime
from pages import readMeta, htmlify

DELIM = "\n\n"

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

GALLERY_PATH = "./public/gallery/index.html"
HOME_PATH = "./public/index.html"

HEADER = '<h2>{}</h2>'

BLOCKQUOTE = """<blockquote>
    <p>
        {}
    </p>
</blockquote>
"""

PARAGRAPH = """<p>
    {}
</p>"""

BLOCK_CODE = """<pre><code>{}</code></pre>"""

PIECE = '''
<div class="piece">
    <picture>
        <img class="art" src="{logo}">
    </picture>
    <div class="didactic">
        <h3 class="title">
            {title}
        </h3>
        <p class="description">
            {desc}
        </p>
    <!-- <div class="brush"><div> -->
    </div>
</div>
'''

PORTFOLIO = '''
<head>
    <title>Portfolio</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    {body}
</body>
'''

HOME = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="smh">
  <title>smh.bio</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="16x16.ico" type"image/ico" sizes="16x16">
  <link rel="icon" href="32x32.ico" type"image/ico" sizes="16x16">
</head>
<body>
  <ul>
    {elements}
  </ul>
</body>
</html>
'''

LINK = '''
<a href="{link}">{text}</a>
'''

ESSAY = '''
<li><a href="{link}">{title}</a><span class="date">{date}</span></li>
'''

PROJECT = '''
<li><span><a href="{link}">{title}</a><span class="description">{desc}</span></span><span class="date">{date}</span></li>
'''

# TODO: CHANGE SO NO GLOBAL VARS
projects = []
essays = []

# TODO: Escape all reserved chars e.g. >, <, &, "
def isRunic(fn):
    return fn[-len(FILETYPE):] == FILETYPE

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
        raise Exception("Missing matching inline code!")

    result = []
    for i in range(len(temp)):
        if i % 2:
            result.append(f'<code>{temp[i]}</code>')
        else:
            result.append(checkLink(temp[i]))

    return "".join(result)

IMAGE = '''
<figure>
<picture>
<img src={}>
</picture>
<figcaption></figcaption
</figure>
'''

def htmlify(t, b):
    block = ""
    if t == "&":
        block = PARAGRAPH.format(processParagraph(b))
    elif t == ">":
        block = BLOCKQUOTE.format(b)
    elif t == "#":
        block = HEADER.format(b)
    elif t == "!":
        block = BLOCK_CODE.format(b)
    elif t == "|":
        block = IMAGE.format(b)
    elif t == "%":
        pass
    else: # throw a fit 
        pass
    return block

# TODO: replace with constants
def home():
    allpages = projects + essays
    allpages.sort(key=lambda x: x[START], reverse=True)
    pagesList = []

    for a in allpages:
        element = ""
        timeStr = a[START].strftime('%b %d, %Y')
        if a['type'] == 'p':
            element = PROJECT.format(
                    date=timeStr,
                    title=a[TITLE], 
                    link=f"{a['filename']}.html",
                    desc=", " + a['description']
                    )
        else:
            element = ESSAY.format(
                    date=timeStr,
                    link= f"{a['filename']}.html",
                    title=a[TITLE])
        pagesList.append(element)

    with open(HOME_PATH, 'w') as f:
        f.write(HOME.format(elements='\n'.join(pagesList)))


def runicToPages(runics):
    pages = []
    for r in runics:
        pn, pc = r
        first, other = pc.split(DELIM, 1)
        try: 
            meta = readMeta(first)
            pages.append(htmlify(pn, meta, other))
        except json.decoder.JSONDecodeError: 
            print(f'Failed to read meta-data of {pn}{FILETYPE}')
        except ValueError as ve:
            print(f'{ve} in {pn}{FILETYPE}')
        except Exception as e:
            print(f'Keys {", ".join(e.args)} not found in meta-data for {pn}{FILETYPE}')
    return pages

def main():



    # portfolio()
    home() 
    print("Finished!")

main()
