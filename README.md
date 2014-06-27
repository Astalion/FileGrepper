FileGrepper
===========

Simple tool for grep-like file manipulation (copy, move, delete, list)

Usage:
  fgrep {c/m/d/l} from {c/m: to} [-rfn]
  
  *c* copies, *m* moves, *d* deletes, and *l* lists files that match the regular expression *from*.
  For copy/move, *to* defines the new file name. Capture groups in *from* can be referred
  to using Python string formatting (i.e. {} for the next group and {n} for the n-th group).
  
  *-r*: Affects files in folders recursively.
  
  *-f*: Skips the confirmation prompt before applying changes.

  *-n*: Don't overwrite files when moving/copying