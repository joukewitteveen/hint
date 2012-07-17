#! /usr/bin/env python
"""Hyperinterval mapping

Repeated hyperinterval finding.

(c) 2012 Jouke Witteveen
"""

import mammals_measure as db_measure
import hint

hint.cli_args()
fh = open( 'mammals.out', 'w' )

try:
  for hinterval, complexity, keep in hint.hints():
    if not keep:
      print( "DISCARDED:", hinterval )
      continue
    print( "KEPT:", hinterval, "complexity:", complexity )
    print( *[ int( hint.hint_tools.is_covered( row, hinterval ) )
              for row in hint.db ], sep='\t', file=fh )
except KeyboardInterrupt:
  print( "Interrupted" )
print( "Reference complexity:", hint.db_base_comp + hint.model_comp )
