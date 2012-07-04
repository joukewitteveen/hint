"""Generic database measurement

General purpose hyperinterval tools.
This file is part of Hint, the hyperinterval finder.

(c) 2011-2012 Jouke Witteveen
"""

# Units are nats when using natural logarithms
from math import log


def bounding_hint( *a ):
  """The smallest hyperinterval covering all arguments."""
  return tuple( map( min, *a ) ), tuple( map( max, *a ) )


def is_covered( a, hint ):
  """Whether record a is covered by the hyperinterval."""
  return all( hint[0][i] <= x <= hint[1][i] for i, x in enumerate( a )
                                            if hint[0][i] and hint[1][i] )


def covered( hint, db ):
  """The number of records covered by the hyperinterval."""
  count = 0
  for row in db:
    if is_covered( row, hint ): count += 1
  return count


def queue_init( db, sample, key ):
  """Initialize the internal queue of next_hint."""
  # Runtime is in O( len( sample ) ** 2 * log( len( sample ) ) ). That is slow.
  def _key( ij ): return key( db[ij[0]], db[ij[1]] )
  next_hint.db = db
  next_hint.queue = sorted( [ ( sample[i], sample[j] )
                              for i in range( len( sample ) )
                              for j in range( i ) ], key = _key )


def next_hint( exclude = None ):
  """The next hyperinterval to expand.

     Points in an excluded interval are not considered."""
  if exclude:
    next_hint.queue = [ ( i, j )
                        for i, j in next_hint.queue
                        if not is_covered( next_hint.db[i], exclude )
                           and not is_covered( next_hint.db[j], exclude ) ]
  if len( next_hint.queue ) == 0:
    print( "Sample exhausted." )
    return None
  return bounding_hint( next_hint.db[next_hint.queue[0][0]],
                        next_hint.db[next_hint.queue[0][1]] )

