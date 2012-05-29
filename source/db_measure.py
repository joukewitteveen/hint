"""Generic database measurement

General purpose measures on numerical databases of arbitrary dimension.
This file is part of Hint, the hyperinterval finder.

(c) 2011-2012 Jouke Witteveen
"""

import hint_tools
from sys import float_info

discretization_const = None


def measure_init( db ):
  """Establish a bounding box around the database and normalizing factors for
     all columns, so that distances become comparable."""
  global db_scale, discretization_const, distance1d
  def distance1d( x, y, z ): return abs( ( x - y ) / z )
  db_lb, db_ub = hint_tools.bounding_hint( *db )
  db_scale = tuple( map( lambda x, y: abs( x - y ), db_lb, db_ub ) )
  discretization_const = len( db_scale ) * hint_tools.log( len( db ) )
  volume.epsilon = float_info.epsilon ** ( 1 / len( db_scale ) )
  return db_lb, db_ub


def distance( a, b ):
  """The distance between two database records."""
  # A rectilinear distance suits the model
  return sum( map( distance1d, a, b, db_scale ) )


def volume( a, b ):
  """The volume of the hyperinterval between two database records.

     Subspaces are given a 'thickness' of epsilon.
     A record with itself yields a hyperinterval of volume 0.
     Two identical records yield a hyperinterval of strictly positive volume.
     The volume of the bounding box around the database is normalized to 1."""
  if a is b: return 0
  V = 1
  for side in map( distance1d, a, b, db_scale ):
    V *= ( side or volume.epsilon )
  return max( V, float_info.min )


def fullness( hint ):
  """Coverage per dimension"""
  return [ ( hint[1][i] - hint[0][i] ) / scale
           for i, scale in enumerate( db_scale ) ]

