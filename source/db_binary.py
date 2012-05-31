"""Binary database measurement

Counting measures on binary databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2012 Jouke Witteveen
"""

import operator
from hint_tools import log

discretization_const = None


def hint_key( a, b ):
  return -sum( map( operator.mul, a, b ) )


def measure_init( db ):
  global discretization_const
  discretization_const = len( db[0] ) * ( log( 6 ) / 2 - log( 2 ) )
  return ( 0, ) * len( db[0] ), ( 1, ) * len( db[0] )


def distance( a, b ):
  """The distance between two database records."""
  return sum( map( operator.ne, a, b ) )


def volume( a, b ):
  """The volume of the hyperinterval between two database records.

     This is a counting measure."""
  return 2 ** distance( a, b )


def fullness( hint ):
  """Coverage per dimension."""
  return list( map( float, map( operator.ne, hint[0], hint[1] ) ) )

