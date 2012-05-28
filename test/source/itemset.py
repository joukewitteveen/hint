#! /usr/bin/env python

import db_binary as db_measure
import hint

hint.cli_args()
try:
  for n, ( h, c, k ) in enumerate( hint.hints() ):
    print( "Itemset {}:".format( n ),
           [ int( h[0][i] ) if h[0][i] == h[1][i] else None
             for i in range( len( h[0] ) ) ],
           c, "KEPT" if k else "DISCARDED" )
except KeyboardInterrupt:
  print( "Interrupted" )
print( "Comparative single uniform data complexity: ", hint.db_base_comp )
print( "Discretized double uniform model complexity:", hint.model_comp )

