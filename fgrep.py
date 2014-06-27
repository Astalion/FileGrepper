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
#   FileCommand class
#
class FileCommand:
    def __init__(self, doFunc, pFunc, hasOutput):
        self.doFunc = FileCommand.filterFunc(doFunc)
        self.prevFunc = FileCommand.previewFunc(pFunc)
        self.hasOutput = hasOutput

    #
    # Class functions
    #
    def filterFunc(dofunc):
        def f(self, fname):
            newname = self.newName(fname)
            if(newname is not None):
                if not self.overwrite and os.path.isfile(newname): return
                try:
                    os.remove(newname)
                except:
                    pass
                dofunc(fname, newname)
        return f

    def previewFunc(pfunc):
        def preview(self, fname):        
            outname = self.newName(fname)
            if(outname is not None):
                exists = os.path.isfile(outname)
                if exists and not self.overwrite: return
                self.change = True # Mark that something would be changed
                pfunc(fname, outname, exists)
        return preview

#
#   FileGrepper class
#
class FileGrepper:
    def __init__(self, command, restring, fmtstring, recursive, overwrite):
        self.regex = re.compile(restring)
        self.fmtstring = fmtstring
        self.files = list(recursiveFiles()) if recursive else os.listdir(".")
        self.overwrite = overwrite
        self.change = False

        self.command = FileGrepper.commands[command]
        self.prevFunc = self.command.prevFunc
        self.doFunc = self.command.doFunc

    #
    # Member functions
    #
    def newName(self, path):
        folder, fname = os.path.split(path)
        match = self.regex.match(fname)
        if(match is not None):
            if self.fmtstring is None: return True
            return os.path.join(folder, self.fmtstring.format(*match.groups()))
        return None

    def showPreview(self):
        runOnFiles(self.files, self.prevFunc, self)

    def run(self):
        runOnFiles(self.files, self.doFunc, self)

    #
    # Class variables
    #
    commands = {
        "m": FileCommand(
                os.rename,
                lambda orig, new, exists:
                    print(colourText("Move:", "yellow"), orig, "->", new,
                        colourText("(Overwrite)", "red") if exists else ""),
                True
            ),
        "c": FileCommand(
                shutil.copy,
                lambda orig, new, exists:
                    print(colourText("Copy:","green"), orig, "->", new,
                        colourText("(Overwrite)", "red") if exists else ""),
                True
            ),
        "d": FileCommand(
                lambda x, y: os.remove(x),
                lambda orig, new, exists:
                    print(colourText("Delete:", "red"), orig),
                False
            ),
        "l": FileCommand(
                lambda *args: None,
                lambda orig, new, exists: print(orig),
                False
            )
    }

#
# Helper functions
#

# Essentially just map(), but (1): passes on any positional and keyword args,
# with the iterated value passed as keyword fname, and (2): does not save the
# list of returned values
def runOnFiles(files, command, *args, **kwargs):
    for fname in files:
        command(*args, fname=fname, **kwargs)

def recursiveFiles():
    for root, _, files in os.walk("."):
        for fname in files:
            yield os.path.relpath(os.path.join(root, fname))

#
# Function
#
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
parser_m.add_argument("-n", action='store_false', help="No overwriting of files")
# -a for "absolute" path when doing recursion?

parser_c = subparsers.add_parser("c", help="Copy files", parents=[dummyparser],
    description=descstr.format("Copy"))
parser_c.add_argument("input", metavar="from", 
    type=str, help="Input Regexp string")
parser_c.add_argument("output", metavar="to",
    type=str, help="Output format string (python-style)")
parser_c.add_argument("-n", action='store_false', help="No overwriting of files")

parser_d = subparsers.add_parser("d", help="Delete files", parents=[dummyparser])
parser_d.add_argument("input", metavar="file",
    type=str, help="Input Regexp string to delete")

parser_l = subparsers.add_parser("l", help="List files", parents=[dummyparser])
parser_l.add_argument("input", metavar="file",
    type=str, help="Input Regexp string to find")

#
# Get parsed arguments
#
args = parser.parse_args()

command = args.command
if(command is None):
    parser.parse_args(["-h"])

hasOutput = FileGrepper.commands[command].hasOutput

restring = args.input
fmtstring = args.output if hasOutput else None
recursive = args.r
overwrite = args.n if hasOutput else None
force = args.f

fg = FileGrepper(command, restring, fmtstring, recursive, overwrite)

#
# Do things
#

fg.showPreview()
if not fg.change:
    print("No matches found")
    sys.exit()

if command == "l": sys.exit()

confirm = True if force else previewConfirm()

if confirm:
    fg.run()
    print("Done")