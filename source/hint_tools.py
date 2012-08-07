"""Generic database measurement

General purpose hyperinterval tools.
This file is part of Hint, the hyperinterval finder.

(c) 2011-2012 Jouke Witteveen
"""

# Units are nats when using natural logarithms
from math import log as _log
def log( x ): return _log( x, 2 )


def is_covered( a, hint ):
  """Whether record a is covered by the hyperinterval."""
  return all( hint[i] <= x for i, x in enumerate( a ) )


def covered( hint, db ):
  """The number of records covered by the hyperinterval."""
  count = 0
  for row in db:
    if is_covered( row, hint ): count += 1
  return count


def queue_init( db, sample, key ):
  """Initialize the internal queue of next_hint."""
  def _key( i ): return key( db[i], ( 0, ) * len( db[0] ) )
  next_hint.db = db
  next_hint.queue = sorted( sample, key = _key )


def next_hint( exclude = None ):
  """The next hyperinterval to expand.

     Points in an excluded interval are not considered."""
  if exclude:
    next_hint.queue = [ i for i in next_hint.queue
                          if not is_covered( next_hint.db[i], exclude ) ]
  if len( next_hint.queue ) == 0:
    print( "Sample exhausted." )
    return None
  return next_hint.db[next_hint.queue.pop()]

