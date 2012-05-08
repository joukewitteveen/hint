#! /usr/bin/env python
"""Hyperinterval mapping

Repeated hyperinterval finding.

(c) 2011 Jouke Witteveen
"""

import hint

fh = open( '2dboxes', 'w' )
judgement = [ [], [] ]

for hinterval, complexity, keep in hint.hints():
  xdelta, ydelta = map( lambda a, b: ( b - a ) / 2, *hinterval )
  x = hinterval[0][0] + xdelta
  y = hinterval[0][1] + ydelta
  print( "Found:", hinterval, "KEPT" if keep else "DISCARDED" )
  judgement[keep].append( "{}\t{}\t{}\t{}\n".format( x, y, xdelta, ydelta ) )

for line in judgement[1]: fh.write( line )
fh.write( "\n\n" )
for line in judgement[0]: fh.write( line )

