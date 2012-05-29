#! /usr/bin/env python

import db_binary as db_measure
import hint

hint.cli_args()
try:
  for n, ( h, c, k ) in enumerate( hint.hints() ):
    s = [ int( x ) if x == h[1][i] else None for i, x in enumerate( h[0] ) ]
    print( "Itemset {}:".format( n ), s, c, "KEPT" if k else "DISCARDED" )
    print( [ i for i, x in enumerate( s ) if x == None ] )
    fh = open( "itemset{}".format( n ), 'w' )
    for row in hint.db:
      fh.write( '\t'.join( str( int( row[i] ) )
                           for i, x in enumerate( s ) if x == None ) + '\n' )
except KeyboardInterrupt:
  print( "Interrupted" )
print( "Comparative single uniform data complexity: ", hint.db_base_comp )
print( "Discretized double uniform model complexity:", hint.model_comp )

