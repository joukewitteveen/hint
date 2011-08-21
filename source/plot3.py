#! /usr/bin/env python
"""Hyperinterval mapping

Seperates the database in items inside and items outside the hyperinterval.

(c) 2011 Jouke Witteveen
"""

import hint, hint_tools

fh = open( 'py2to3', 'w' )
keys = []
for _ in hint.db: keys.append( tuple( map( float, input().split() ) ) )

for hinterval, complexity, keep in hint.hints():
  print( "Found:", hinterval, "KEPT" if keep else "DISCARDED" )
  if not keep: continue
  inside = []
  outside = []
  for i, row in enumerate( hint.db ):
    if hint_tools.is_covered( row, hinterval ):
      inside.append( keys[i] )
    else:
      outside.append( keys[i] )
  fh.write( "{}\n".format( repr( ( inside, outside ) ) ) )
