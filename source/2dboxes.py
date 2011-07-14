#! /usr/bin/env python
"""Hyperinterval mapping

Repeated hyperinterval finding.

(c) 2011 Jouke Witteveen
"""

from hint import *

fh = open( '2dboxes', 'w' )

for _ in range( 20 ):
  run()
  xdelta, ydelta = map( lambda a, b: ( b - a ) / 2, *hint_history[-1] )
  x = hint_history[-1][0][0] + xdelta
  y = hint_history[-1][0][1] + ydelta
  fh.write( "{}\t{}\t{}\t{}\n".format( x, y, xdelta, ydelta ) )
