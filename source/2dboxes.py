#! /usr/bin/env python
"""Hyperinterval mapping

Repeated hyperinterval finding.

(c) 2011 Jouke Witteveen
"""

import hint

fh = open( '2dboxes', 'w' )

for _ in range( 30 ):
  hint.run()
  xdelta, ydelta = map( lambda a, b: ( b - a ) / 2, *hint.hint_history[-1] )
  x = hint.hint_history[-1][0][0] + xdelta
  y = hint.hint_history[-1][0][1] + ydelta
  fh.write( "{}\t{}\t{}\t{}\n".format( x, y, xdelta, ydelta ) )
