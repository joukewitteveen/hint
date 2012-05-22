"""Generic database measurement

General purpose measures on numerical databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2011 Jouke Witteveen
"""

import hint_tools
from sys import float_info

discretization_const = None


def measure_init( _db, sample ):
  """Establish a bounding box around the database and normalizing factors for
     all columns, so that distances become comparable."""
  global db, db_scale, discretization_const
  db = _db
  db_lb, db_ub = hint_tools.bounding_hint( *db )
  db_scale = tuple( map( lambda x, y: abs( x - y ), db_lb, db_ub ) )
  discretization_const = len( db_scale ) * hint_tools.log( len( db ) )
  volume.epsilon = float_info.epsilon ** ( 1 / len( db_scale ) )
  # Runtime is quadratic in the sample size. That is slow.
  hint_init.queue = sorted( [ ( sample[i], sample[j] )
                              for i in range( len( sample ) )
                              for j in range( i ) ],
                            key = lambda ij: distance( db[ij[0]], db[ij[1]] ) )
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


def hint_init( exclude = None ):
  """The hyperinterval is initialized as the region between the two sampled
     points that are closest together.

     Points in an excluded interval are not considered."""
  global hint_origin
  if exclude:
    hint_init.queue = [ ( i, j )
                        for i, j in hint_init.queue
                        if not hint_tools.is_covered( db[i], exclude )
                           and not hint_tools.is_covered( db[j], exclude ) ]
  if len( hint_init.queue ) == 0:
    print( "Sample exhausted." )
    return None
  a, b = db[hint_init.queue[0][0]], db[hint_init.queue[0][1]]
  hint_origin = tuple( map( lambda x, y: ( x + y ) / 2, a, b ) )
  return hint_tools.bounding_hint( a, b )


def fullness( hint ):
  """Coverage per dimension"""
  return [ ( hint[1][i] - hint[0][i] ) / scale
           for i, scale in enumerate( db_scale ) ]

