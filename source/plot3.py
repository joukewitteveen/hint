#! /usr/bin/env python
"""Hyperinterval mapping

Seperates the database in items inside and items outside the hyperinterval.

(c) 2011 Jouke Witteveen
"""

from hint import *

fh = open( 'py2to3', 'w' )
inside = []
outside = []

for row in db:
  line = input()
  attrib = tuple( map( float, line.split() ) )
  for i, x in enumerate( row ):
    if not ( hint[0][i] <= x <= hint[1][i] ):
      outside.append( attrib )
      break
  else:
    inside.append( attrib )
fh.write( "{}\n{}\n".format( repr( inside ), repr( outside ) ) )
