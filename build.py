# TODO: need to eventually remove json dependency
import os, json, re
from datetime import datetime

DELIM = "\n\n"
RUNIC_DIRECTORY = "./pages"
PAGES_DIRECTORY = "./public"
FILETYPE = ".runic"

TITLE = "title"
START = "start"

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
<head>
  <title>smh.bio</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <ul>
    {elements}
  </ul>
</body>
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

def merge(*iterators):
  empty = {}
  for values in itertools.zip_longest(*iterators, fillvalue=empty):
    for value in values:
      if value is not empty:
        yield value

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

def readMeta(b, fn):
    temp = json.loads(b)
    temp[START] = datetime.strptime(temp[START], '%Y-%m-%d')
    temp["filename"] = fn
    if temp["type"] == "p":
        projects.append(temp)
    else: # type is essay
        essays.append(temp)

    
# image, title, description
# Need to map projects to image, title, description
# standardize logo picture format 
def portfolio():
    projects.sort(key=lambda x: x[START], reverse=True) 
    gallery = []
    for p in projects:
        gallery.append(PIECE.format(
            logo=f'public/logo/{p["filename"]}.png', 
            title=p['title'], 
            desc=p['description'])) 

    with open(GALLERY_PATH, 'w') as f:
        f.write(PORTFOLIO.format(body="\n".join(gallery)))

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

def parse(fn):
    content = []
    with open(f'{RUNIC_DIRECTORY}/{fn}{FILETYPE}', 'r') as f:
        rawContent = iter(map(lambda x: x.strip(), f.read().split(DELIM)))
        meta = next(rawContent)

        readMeta(meta, fn)     
        rawContent = list(rawContent)

        for block in rawContent:
            if not block:
                continue
            # check type, remove rune 
            content.append(htmlify(block[0], block[1:].replace("\n"," ").strip()))        

    return HTML.format(title=fn, content=DELIM.join(content))

def writeHtml(p,c):
    fn = p + ".html"
    with open(f'{PAGES_DIRECTORY}/{fn}', 'w') as f:
        f.write(c)
    

def main():
    # read directory
    pages = list(p[:-len(FILETYPE)] for p in filter(isRunic, os.listdir(RUNIC_DIRECTORY)))
    for p, c in zip(pages, map(parse, pages)):
        writeHtml(p,c)

    # for later
    # portfolio()
    home() 
    print("Finished!")

main()
