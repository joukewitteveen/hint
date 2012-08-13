"""Binary database measurement

Counting measures on binary databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2012 Jouke Witteveen
"""

from hint_tools import log


def measure_update( db, sample ):
  global entropies
  N = len( sample )
  if N == 0: return False
  entropies = tuple( log( N ) \
                     - ( n * log( n ) + ( N - n ) * log( N - n ) ) / N \
                     if n > 0 else float( 'inf' ) \
                     for n in map( sum, zip( *[ db[i] for i in sample ] ) ) )
  return any( x < float( 'inf' ) for x in entropies )


def distance( a, b ):
  """The description distance between two database records."""
  return sum( entropies[i] for i, ( x, y ) in enumerate( zip( a, b ) )
                           if x != y )


def lvolume( hint ):
  """The logarithm of the volume inside a hyperinterval.

     This is a counting measure."""
  return len( hint ) - sum( hint )

