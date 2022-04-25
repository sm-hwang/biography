import os

DELIM = "\n\n"
RUNIC_DIRECTORY = "."
PAGES_DIRECTORY = "."
FILETYPE = ".runic"

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

BLOCK_CODE = """<pre>
    <code>
        {}
    </code>
</pre>
"""

# TODO: Escape all reserved chars e.g. >, <, &, "

def isRunic(fn):
    return fn[-len(FILETYPE):] == FILETYPE

def htmlify(t, b):
    # print(t, b)
    block = ""
    if t == "&":
        block = PARAGRAPH.format(b)
    elif t == ">":
        block = BLOCKQUOTE.format(b)
    elif t == "#":
        block = HEADER.format(b)
    elif t == "!":
        block = BLOCK_CODE.format(b)
    elif t == "%":
        pass
    else: # throw a fit 
        pass
    return block

def parse(fn):
    # print(f'{RUNIC_DIRECTORY}/{fn}')
    content = []
    with open(f'{RUNIC_DIRECTORY}/{fn}', 'r') as f:
        rawContent = map(lambda x: x.strip(), f.read().split(DELIM))
        for block in rawContent:
            if not block:
                continue
             
            # check type, remove rune 
            content.append(htmlify(block[0], block[1:].replace("\n"," ").strip()))        
    return DELIM.join(content)

def writeHtml(p,c):
    fn = "".join([p[:-len(FILETYPE)], ".html"])
    with open(f'{PAGES_DIRECTORY}/{fn}', 'w') as f:
        f.write(c)
    

def main():
    # read directory
    pages = list(filter(isRunic, os.listdir(RUNIC_DIRECTORY)))
    for p, c in zip(pages, map(parse, pages)):
        writeHtml(p,c)
    print("Finished!")
    

main()
