FileGrepper
===========

Simple tool for grep-like file manipulation (copy, move, delete, list)

Usage:
  fgrep {c/m/d/l} FROM {c/m: TO} [-rfn]
  
  *c* copies, *m* moves, *d* deletes, and *l* lists files that match the regular expression *FROM*.
  For copy/move, *TO* defines the new file name. Capture groups in *FROM* can be referred
  to using Python string formatting (i.e. {} for the next group and {n} for the n-th group).
  
  *-r*: Affects files in folders recursively.
  
  *-f*: Skips the confirmation prompt before applying changes.

  *-n*: Don't overwrite files when moving/copying