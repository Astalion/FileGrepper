FileGrepper
===========

Simple tool for grep-like file manipulation (copy, move, delete)

Usage:
  fgrep {c/m/d} from {c/m: to} [-rf]
  
  *c* copies, *m* moves, and *d* deletes files that match the regular expression *from*.
  For copy/move, *to* defines the new file name. Capture groups in *from* can be referred
  to using Python string formatting (i.e. {} for the next group and {n} for the n-th group).
  
  *-r*: Affects files in folders recursively.
  
  *-f*: Skips the confirmation prompt before applying changes.
