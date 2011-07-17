"""Generic database measurement

General purpose measures on numerical databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2011 Jouke Witteveen
"""

import hint_tools
from sys import float_info


def measure_init( db, sample ):
  """Establish a bounding box around the database and normalizing factors for
     all columns, so that distances become comparable."""
  global db_scale
  db_lb, db_ub = hint_tools.bounding_hint( *db )
  db_scale = tuple( map( lambda x, y: abs( x - y ), db_lb, db_ub ) )
  volume.epsilon = float_info.epsilon**( 1 / len( db[0] ) )
  # Runtime is quadratic in the sample size. That is slow.
  hint_init.candidates = sorted( [ ( a, b ) for a in sample for b in sample
                                                            if not a is b ],
                                 key = lambda ab: distance( *ab ) )
  return db_lb, db_ub


def distance( a, b ):
  """The distance between two database records."""
  # A rectilinear distance suits the model
  return sum( map( lambda x, y, z: abs( ( x - y ) / z ), a, b, db_scale ) )


def volume( a, b ):
  """The volume of the hyperinterval between two database records.

     Subspaces are given a 'thickness' of epsilon.
     A record with itself yields a hyperinterval of volume 0.
     Two identical records yield a hyperinterval of strictly positive volume.
     The volume of the bounding box around the database is normalized to 1."""
  if a is b: return 0
  V = 1
  for side in map( lambda x, y, z: abs( ( x - y ) / z ), a, b, db_scale ):
    V *= ( side or volume.epsilon )
  return max( V, float_info.min )


def hint_init( sample, *exclude ):
  """The hyperinterval is initialized as the region between the two sampled
     points that are closest together.

     Points in excluded intervals are not considered."""
  global hint_origin
  exclude = [ a for a in exclude if a not in hint_init.excluded ]
  hint_init.candidates = [ ( x, y )
                           for x, y in hint_init.candidates
                           if not hint_tools.is_covered( x, *exclude )
                              and not hint_tools.is_covered( y, *exclude ) ]
  hint_init.excluded.extend( exclude )
  if len( hint_init.candidates ) == 0:
    print( "Sample exhausted." )
    return None
  hint_origin = tuple( map( lambda x, y: ( x + y ) / 2,
                            *hint_init.candidates[0] ) )
  return hint_tools.bounding_hint( *hint_init.candidates[0] )
hint_init.excluded = list()
