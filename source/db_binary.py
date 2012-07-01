"""Binary database measurement

Counting measures on binary databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2012 Jouke Witteveen
"""

from hint_tools import log

discretization_const = None


def measure_init( db ):
  global discretization_const, lfractions
  discretization_const = len( db[0] ) * ( log( 6 ) / 2 - log( 2 ) )
  lfractions = tuple( -log( sum( x ) / len( db ) ) for x in zip( *db ) )
  return ( 0, ) * len( db[0] ), ( 1, ) * len( db[0] )


def distance( a, b ):
  """The correlation distance between two database records."""
  return sum( ( x != y ) * f for x, y, f in zip( a, b, lfractions ) )


def volume( a, b ):
  """The volume of the hyperinterval between two database records.

     This is a counting measure."""
  return 2 ** sum( x != y for x, y in zip( a, b ) )


def fullness( hint ):
  """Coverage per dimension."""
  return tuple( 0.0 if x == y else 1.0 for x, y in zip( *hint ) )

