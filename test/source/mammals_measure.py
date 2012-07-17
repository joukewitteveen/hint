"""Mammals measurement

General purpose measure, combined with a counting measure.

(c) 2012 Jouke Witteveen
"""

import hint_tools
from sys import float_info

discretization_const = None
numeric_cols = 19


def measure_init( db ):
  """Establish a bounding box around the database and normalizing factors for
     all columns, so that distances become comparable."""
  global db_scale, discretization_const, distance1d, entropies
  def distance1d( x, y, z ): return abs( ( x - y ) / z )
  db_lb, db_ub = hint_tools.bounding_hint( *db )
  db_scale = tuple( y - x for x, y in zip( db_lb[:numeric_cols], db_ub[:numeric_cols] ) )
  discretization_const = numeric_cols * hint_tools.log( len( db ) ) + \
                         ( len( db_scale ) - numeric_cols ) * ( hint_tools.log( 6 ) / 2 - hint_tools.log( 2 ) )
  N = len( db )
  entropies = tuple( hint_tools.log( N, 2 ) \
                     - ( n * hint_tools.log( n, 2 ) + ( N - n ) * hint_tools.log( N - n, 2 ) ) / N \
                     for n in map( sum, tuple( zip( *db ) )[numeric_cols:] ) )
  volume.epsilon = float_info.epsilon ** ( 1 / numeric_cols )
  return db_lb, db_ub


def distance( a, b ):
  """The distance between two database records."""
  # A rectilinear distance suits the model
  return sum( map( distance1d, a[:numeric_cols], b[:numeric_cols], db_scale ) ) + \
         sum( entropies[i] for i, ( x, y ) in enumerate( zip( a[numeric_cols:], b[numeric_cols:] ) )
                           if x != y )


def volume( a, b ):
  """The volume of the hyperinterval between two database records.

     Subspaces are given a 'thickness' of epsilon.
     A record with itself yields a hyperinterval of volume 0.
     Two identical records yield a hyperinterval of strictly positive volume.
     The volume of the bounding box around the database is normalized to 1."""
  if a is b: return 0
  V = 1
  for side in map( distance1d, a[:numeric_cols], b[:numeric_cols], db_scale ):
    V *= ( side or volume.epsilon )
  V *= 2 ** sum( x != y for x, y in zip( a[numeric_cols:], b[numeric_cols:] ) )
  return max( V, float_info.min )


def fullness( hint ):
  """Coverage per dimension."""
  return tuple( map( distance1d, hint[0][:numeric_cols], hint[1][:numeric_cols], db_scale ) ) + \
         tuple( float( x != y ) for x, y in zip( hint[0][numeric_cols:], hint[1][numeric_cols:] ) )
