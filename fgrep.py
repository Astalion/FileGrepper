#!/usr/bin/env python3
import sys, os, re, argparse, shutil

try:
    from colorama import init, Fore
    init()
    colours = {
        'red': Fore.RED,
        'cyan': Fore.CYAN,
        'black': Fore.BLACK,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'white': Fore.WHITE
    }
    def colourText(text, colour):
        return colours[colour] + text + Fore.RESET
except (ImportError, ValueError):
    colourText = lambda text: text


#
# Functions
#
def runOnFiles(files, command, *args, **kwargs):
    for fname in files:
        command(fname, *args, **kwargs)

def recursiveFiles():
    for root, _, files in os.walk("."):
        for fname in files:
            yield os.path.relpath(os.path.join(root, fname))

def newName(path, regex, fmtstring):
    folder, fname = os.path.split(path)
    match = regex.match(fname)
    if(match is not None):
        if fmtstring is None: return True
        return os.path.join(folder, fmtstring.format(*match.groups()))
    return None

# Preview function maker
def previewFunc(pfunc):
    def preview(fname, regex, fmtstring):        
        outname = newName(fname, regex, fmtstring)
        if(outname is not None):
            exists = os.path.isfile(outname)
            pfunc(fname, outname, exists)
    return preview

def filterFunc(dofunc):
    def f(fname, regex, fmtstring):
        newname = newName(fname, regex, fmtstring)
        if(newname is not None):
            try:
                os.remove(newname)
            except:
                pass
            dofunc(fname, newname)
    return f

def showPreview(files, prevFunc, *args):
    runOnFiles(files, prevFunc, *args)

def previewConfirm():
    print()
    while True:
        ans = input("Would you like to perform these changes (y/n)? ")
        if(ans == "y"):
            return True
        elif(ans == "n"):
            return False

#
# Global constants
#
descstr = "{} files matching the input regex to the position\
        denoted by the format string. Any capture groups are passed to\
        the output string, as a python-style format string (i.e. {{}} for\
        the next group, or {{n}} for the n-th group)."
doFuncs = {
    "m": filterFunc(os.rename),
    "c": filterFunc(shutil.copy),
    "d": filterFunc(lambda x, y: os.remove(x)),
    "l": lambda *args: None
}
prevFuncs = {
    "m": previewFunc(lambda orig, new, exists:
        print(colourText("Move:", "yellow"), orig, "->", new,
            colourText("(Overwrite)", "red") if exists else "")),
    "c": previewFunc(lambda orig, new, exists:
        print(colourText("Copy:","green"), orig, "->", new,
            colourText("(Overwrite)", "red") if exists else "")),
    "d": previewFunc(lambda orig, new, exists:
        print(colourText("Delete:", "red"), orig)),
    "l": previewFunc(lambda orig, new, exists: print(orig))
}
hasoutput = {
    "m": True,
    "c": True,
    "d": False,
    "l": False    
}

#
# Set up argument parser
#
parser = argparse.ArgumentParser(prog="fgrep")
parser.add_argument("-r", action='store_true', help="Recursive")
parser.add_argument("-f", action='store_true', help="Skip confirmation")
subparsers = parser.add_subparsers(dest="command")

# Dummy for showing parent arguments in children
dummyparser = argparse.ArgumentParser(prog="fgrep", add_help=False)
dummyparser.add_argument("-r", action='store_true', help="Recursive")
dummyparser.add_argument("-f", action='store_true', help="Skip confirmation")

parser_m = subparsers.add_parser("m", help="Move files", parents=[dummyparser],
    description=descstr.format("Move"))
parser_m.add_argument("input", metavar="from",
    type=str, help="Input regex string")
parser_m.add_argument("output", metavar="to",
    type=str, help="Output format string (python-style)")
# -a for "absolute" path when doing recursion?

parser_c = subparsers.add_parser("c", help="Copy files", parents=[dummyparser],
    description=descstr.format("Copy"))
parser_c.add_argument("input", metavar="from", 
    type=str, help="Input Regexp string")
parser_c.add_argument("output", metavar="to",
    type=str, help="Output format string (python-style)")

parser_d = subparsers.add_parser("d", help="Delete files", parents=[dummyparser])
parser_d.add_argument("input", metavar="file",
    type=str, help="Input Regexp string to delete")

parser_l = subparsers.add_parser("l", help="List files", parents=[dummyparser])
parser_l.add_argument("input", metavar="file",
    type=str, help="Input Regexp string to find")

args = parser.parse_args()

#
# Get parsed arguments
#
command = args.command
if(command is None):
    parser.parse_args(["-h"])

recursive = args.r
force = args.f
regex = re.compile(args.input)
fmtstring = args.output if hasoutput[command] else None
doFunc = doFuncs[command]
prevFunc = prevFuncs[command]

#
# Do things
#

files = list(recursiveFiles()) if recursive else os.listdir(".")

showPreview(files, prevFunc, regex, fmtstring)
if command == "l": sys.exit()

confirm = True if force else previewConfirm()

if confirm:
    runOnFiles(files, doFunc, regex, fmtstring)
    print("Done")