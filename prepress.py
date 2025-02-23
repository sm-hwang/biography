import re
import json
import sys, os
import webbrowser
from datetime import datetime
from pathlib import Path
from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from xml.etree.ElementTree import SubElement
import xml.etree as etree

# blocks are separated by a blank line, i.e, ,strip("\n\n")

TITLE = 'title'
START = 'start'
TYPE = 'type'
DESC = 'description'
KEYS = [TITLE, START, TYPE, DESC]
INDEX = 'index'
DRAFT_DIR = "pages"
DRAFT_EXT = ".md"
OUTPUT_DIR = "public"


HOME_TITLE = 'smh'
UL_HOME = '''
<ul class="cover">
    {elements}    
</ul>
'''

PROJECT = '''
<li class="chapter"><span><a href="{link}">{title}</a><span class="description">{desc}</span></span><span class="date">{date}</span></li>
'''

ESSAY = '<li class="chapter"><a href="{link}">{title}</a><span class="date">{date}</span></li>'

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
  <script src="mathjax_config.js" defer></script>
  <script type="text/javascript" id="MathJax-script" defer
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>
</head>
<body>
  <main>
{content}
  </main>
</body>
</html>
"""

class BlockCodeProcessor(BlockProcessor):
    BLOCK_CODE = re.compile(r"^```")
    DELIM = "```"

    def test(self, parent, block):
        return bool(self.BLOCK_CODE.match(block.strip()))

    def run(self, parent, blocks):
        pre = SubElement(parent, "pre")
        code = SubElement(pre, "code")
        # TODO: There is a bug where text delimited by `` will be changed to <code></code>.
        # At this point, it is still `` as desired.
        code.text = blocks.pop(0).strip()[len(self.DELIM):-len(self.DELIM)].lstrip("\n")
        return True

class BlockCodeExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(BlockCodeProcessor(md.parser), 'block_code', 1000)

class ImageProcessor(BlockProcessor):
    IMAGE_PATTERN = re.compile(r'^\!\[(.*?)\]\((.*?)\)$')  # Match full line images

    def test(self, parent, block):
        return bool(self.IMAGE_PATTERN.match(block.strip()))

    def run(self, parent, blocks):
        block = blocks.pop(0).strip()
        match = self.IMAGE_PATTERN.match(block.strip())

        # Extract values
        alt_text = match.group(1)
        content = match.group(2).split(",")

        # Fill with default values for bg_color and title
        content.extend(["", ""])
        src, bg_color, title, *_ = map(lambda x: x.strip(), content)
        if len(bg_color) == 0 or bg_color[0] != "#":
            print("Background color must start with #!")

        div = SubElement(parent, "div", {"class": "center"})
        picture = SubElement(div, "picture")
        img = SubElement(picture, "img", {"src": src, "alt": alt_text})

        if bg_color:
            img.set("style", f"background-color: {bg_color};")
        if title:
            img.set("title", title)

class ImageExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(ImageProcessor(md.parser), "custom_image_block", 175)

def makeExtension(**kwargs):
    return CustomImageExtension(**kwargs)

def read_draft(draft_path):
    try:
        with open(draft_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read \"{draft_path}\": {e}")
        return None

def convert_to_page(draft_content):
    # fenced_code is necessary for ``` `text` ``` to not be interpreted as ```<code>text</code>```
    # there may be a better way to do this
    md = Markdown(extensions=["fenced_code", BlockCodeExtension(), ImageExtension()])
    return md.convert(draft_content)

def print_pages(pages):
    for pn, pc in pages:
        path = f"{OUTPUT_DIR}/{pn}.html"

        if os.path.exists(f"{path}"):
            print(f"Skipping printing to \"{path}\" since it already exists.")
            continue

        try:
            with open(path, 'w') as f:
                f.write(pc)
        except Exception as e:
            print(f"Failed to write to {path}: {e}")

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

def prepress(draft_names):
    to_print = [] 

    for dn in draft_names:
        print(f"Prepressing {DRAFT_DIR}/{dn}{DRAFT_EXT}")
        content = read_draft(f"{DRAFT_DIR}/{dn}{DRAFT_EXT}")

        if not content:
            continue

        try:
            if len(content.split("\n\n", 1)) != 2:
                print(f"{dn}{DRAFT_EXT} malformed metadata (missing or not separated by newline)")
                continue
            metadata, content = content.split("\n\n", 1)
            metadata = readMeta(metadata)
            in_html = HTML.format(title=dn, content=convert_to_page(content))
            to_print.append((dn, in_html, metadata))
        except json.decoder.JSONDecodeError: 
            print(f"Failed to read metadata of {dn}{DRAFT_EXT}")
        except ValueError as ve:
            print(f"Error during prepressing of {dn}{DRAFT_EXT}: {ve}")

    return to_print

def getDate(p):
    _, __, meta = p
    return meta[START]

def get_table_of_contents(pages):
    pages.sort(key=getDate, reverse=True)
    toc = []

    for p in pages:
        name, _, meta = p
        time = meta[START].strftime('%b %d, %Y')
        if meta["type"] == "p":
            element = PROJECT.format(
                    date=time,
                    title=meta[TITLE], 
                    link=f"{name}.html",
                    desc=", " + meta["description"])
        else:
            element = ESSAY.format(
                    date=time,
                    link= f"{name}.html",
                    title=meta[TITLE])
        toc.append(element)
    home = UL_HOME.format(elements='\n'.join(toc))

    return HTML.format(title= HOME_TITLE, content= home)

def print_biography(draft_names):
    pages = prepress(draft_names)
    toc = get_table_of_contents(pages)
    pages = [(pn, pc) for (pn, pc, _) in pages]
    pages.append((INDEX, toc))
    print_pages(pages)
#     proofread([pn for (pn,_) in pages])
# 
# def proofread(page_names):
#     for pn in page_names:
#         path_to_printed = Path(f"{OUTPUT_DIR}/{pn}.html").resolve()
#         path_to_original = Path(f"{TEST_DIR}/{pn}.html").resolve()
#         webbrowser.open(f"file://{path_to_printed}")
#         webbrowser.open(f"file://{path_to_original}")
#         if input("continue? (y/n) ").lower() != "y":
#             break
