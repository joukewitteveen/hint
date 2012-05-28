"""Binary database measurement

Counting measures on binary databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2012 Jouke Witteveen
"""

import operator
import hint_tools

discretization_const = 0


def measure_init( _db, sample ):
  global db
  db = _db
  # Runtime is quadratic in the sample size. That is slow.
  def overlap( ij ): return sum( map( operator.mul, db[ij[0]], db[ij[1]] ) )
  hint_init.queue = sorted( [ ( sample[i], sample[j] )
                              for i in range( len( sample ) )
                              for j in range( i ) ],
                            key = overlap, reverse = True )
  return ( 0, ) * len( db[0] ), ( 1, ) * len( db[0] )


def distance( a, b ):
  """The distance between two database records."""
  return sum( map( operator.ne, a, b ) )


def volume( a, b ):
  """The volume of the hyperinterval between two database records.

     This is a counting measure."""
  return 2 ** distance( a, b )


def hint_init( exclude = None ):
  """The hyperinterval is initialized as the region between the two sampled
     points that are closest together.

     Points in an excluded interval are not considered."""
  if exclude:
    hint_init.queue = [ ( i, j )
                        for i, j in hint_init.queue
                        if not hint_tools.is_covered( db[i], exclude )
                           and not hint_tools.is_covered( db[j], exclude ) ]
  if len( hint_init.queue ) == 0:
    print( "Sample exhausted." )
    return None
  return hint_tools.bounding_hint( db[hint_init.queue[0][0]],
                                   db[hint_init.queue[0][1]] )


def fullness( hint ):
  """Coverage per dimension"""
  return list( map( float, map( operator.ne, hint[0], hint[1] ) ) )

