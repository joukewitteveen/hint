#! /usr/bin/env python
"""Hyperinterval mapping

Seperates the database in items inside and items outside the hyperinterval.

(c) 2011 Jouke Witteveen
"""

import hint, hint_tools

iterations = 100
fh = open( 'py2to3', 'w' )
keys = []
for _ in hint.db: keys.append( tuple( map( float, input().split() ) ) )

for _ in range( iterations ):
  hint.run()
  inside = []
  outside = []
  for i, row in enumerate( hint.db ):
    if hint_tools.is_covered( row, hint.hint_history[-1] ):
      inside.append( keys[i] )
    else:
      outside.append( keys[i] )
  fh.write( "{}\n".format( repr( ( inside, outside ) ) ) )
