import os, sys, argparse, logging
from src.slides import markdown_presentation

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Command-line parse
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

desc = '''
Transforms markdown (with LaTeX) into a webpage that can be opened with 
reveal.js
'''.strip()

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('markdown', help='Input Markdown file')
parser.add_argument('--html_title',  default="")
parser.add_argument('--html_author', default="")
parser.add_argument('--html_desc',   default="")
parser.add_argument('--verbose', '-v', action='store_true', 
                    default=False, dest='verbose',
                    help='Logging information')
parser.add_argument('--prettify', action='store_true', 
                    default=False, help="html output is prettified")
msg = "Output html file, if none defaults to [markdown input].html"
parser.add_argument('--output',help=msg, default="")
cmdline_args = parser.parse_args()

# Start the logger
if cmdline_args.verbose: 
    logging.root.setLevel(logging.INFO)

# See README.md in the reveal.js folder for what these options do 
# (default values); note the transition value needs to be in quotes ""

reveal_init={
    'width':960,
    'height':700,
    #'width':400,
    #'height':900,
    'margin': 0.05,
    'minScale': 0.2,
    'maxScale': 1.2,

    'controls': 'true', 
    'progress': 'true', 

    'history': 'true', 

    'keyboard': 'true',
    'overview': 'true', 
    'center': 'true', 
    'touch' : 'true',
    'loop': 'false', 
    'rtl': 'false',
    'fragments':'true',
    'embedded':'true',   
    'autoSlide':0,
    'autoSlideStoppable':'true',
    'mouseWheel':'false', 
    'hideAddressBar':'true',
    'previewLinks':'false',
    'transition': '"default"',
    'transitionSpeed': '"default"',
    'backgroundtransition': '"default"',
    'viewDistance':3,
    'rollingLinks': 'false'
    }

# Load reveal arguments if present
f_reveal_json_args = "reveal_options.json"
if os.path.exists(f_reveal_json_args):
    import json

    with open(f_reveal_json_args) as FIN:
        js = json.load(FIN)
    reveal_init.update(js)

if not cmdline_args.output:
    cmdline_args.output = cmdline_args.markdown.split('.')[0] + '.html'
        
script_name = __file__
script_dir  = os.path.dirname(os.path.realpath(script_name))
local_dir   = os.getcwd()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Header read
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

print script_dir

fin_header = os.path.join(script_dir, "org", "header.html")
with open(fin_header) as FIN: header = FIN.read()

with open(cmdline_args.markdown) as FIN:
    raw = FIN.read()

markdown_parser = markdown_presentation()
slide_html = markdown_parser(raw)

reveal_init_val=''
for i,j in reveal_init.iteritems():
    reveal_init_val += '%s: %s, ' % (i,j)

# Give a bit more control over the initalize params
header_args = vars(cmdline_args)
header_args["reveal_init_args"] = reveal_init_val
header_args["html_content"]     = slide_html

f_dependencies = os.path.join(script_dir, "org", "dependencies.js")
with open(f_dependencies) as FIN:
    header_args["reveal_dependencies"] = FIN.read()

final_html = header.format(**header_args)

with open(cmdline_args.output, 'w') as FOUT:
    if not cmdline_args.prettify:
        FOUT.write(final_html)
    else:
        import bs4
        soup = bs4.BeautifulSoup(final_html)
        encoded_html = soup.prettify().encode('utf8')
        FOUT.write(encoded_html)

logging.info("{} created".format(cmdline_args.output))


# Copy dependencies
import shutil
target_directories = ["css"]
for T in target_directories:

    if not os.path.exists(T):
        local_target    = os.path.join(local_dir, T)    
        absolute_target = os.path.join(script_dir,T)
        
        print "# Copying {} to local directory {}".format(T, local_dir)
        shutil.copytree(absolute_target, local_target)