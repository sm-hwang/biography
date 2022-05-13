# TODO: need to eventually remove json dependency
import os, json, re
from datetime import datetime

DELIM = "\n\n"
RUNIC_DIRECTORY = "."
PAGES_DIRECTORY = "."
FILETYPE = ".runic"

TITLE = "title"
START = "start"

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

BLOCK_CODE = """
<pre>
    <code>
        {}
    </code>
</pre>
"""

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
  <link rel="stylesheet" href="home.css">
</head>
<body>
  <p> 
    I dream of a world where the right thing to do is the easy thing to do.
  </p>  
  <ul>
    {elements}
  </ul>
</body>
'''

LINK = '''
<a href="{link}">{text}</a>
'''

ESSAY = '''
<li><span class="date">{date}</span><a href="{link}">{title}</a></li>
'''

PROJECT = '''
<li><span class="date">{date}</span><a href="{link}">{title}</a><span class="description">{desc}</span></li>
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
<picture>
    <img src={}>
</picture>
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
    projects.sort(key=lambda x: x[START]) 
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
    allpages.sort(key=lambda x: x[START])
    pagesList = []

    for a in allpages:
        element = ""
        timeStr = a[START].strftime('%Y %b %d - ')
        if a['type'] == 'p':
            element = PROJECT.format(
                    date=timeStr,
                    title=a[TITLE], 
                    link='./' + a['filename'],
                    desc=", " + a['description']
                    )
        else:
            element = ESSAY.format(
                    date=timeStr,
                    link='./' + a['filename'],
                    title=a[TITLE])
        pagesList.append(element)
    HOME.format(elements='\n'.join(pagesList))

    with open(HOME_PATH, 'w') as f:
        f.write(HOME.format(elements='\n'.join(pagesList)))

def parse(fn):
    content = []
    with open(f'{RUNIC_DIRECTORY}/{fn}{FILETYPE}', 'r') as f:
        rawContent = iter(map(lambda x: x.strip(), f.read().split(DELIM)))
        meta = next(rawContent)

        readMeta(meta, fn)     

        for block in rawContent:
            if not block:
                continue
             
            # check type, remove rune 
            content.append(htmlify(block[0], block[1:].replace("\n"," ").strip()))        
    return DELIM.join(content)

def writeHtml(p,c):
    fn = p + ".html"
    with open(f'{PAGES_DIRECTORY}/{fn}', 'w') as f:
        f.write(c)
    

def main():
    # read directory
    pages = list(p[:-len(FILETYPE)] for p in filter(isRunic, os.listdir(RUNIC_DIRECTORY)))
    for p, c in zip(pages, map(parse, pages)):
        writeHtml(p,c)

    portfolio()
    home() 
    print("Finished!")

main()