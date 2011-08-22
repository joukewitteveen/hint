#! /usr/bin/env python
"""Hyperinterval finder

Finds hyperintervals in a (numerical) database that have high density.

(c) 2011 Jouke Witteveen
"""

import argparse, random
import hint_tools
# Units are nats when using natural logarithms
from math import log
# Customize the database measure by
#   import <custom_db_measure> as db_measure
# before importing this file
try:
  from __main__ import db_measure
except ImportError:
  import db_measure


### ARGUMENT PARSING AND VALIDATION ###

parser = argparse.ArgumentParser( description = "Hyperinterval finder." )
parser.add_argument( '-s', '--sample', metavar = 'SIZE', type = int,
  required = True, help = "sample size to determine hyperinterval boundaries" )
parser.add_argument( 'database', type = argparse.FileType( 'r' ),
  help = "database file containing one line per entry" )
parser.add_argument( '-p', '--perseverance', type = int, default = 0,
  help = "eagerness to not end up in local minima" )
parser.add_argument( '-t', '--thoroughness', type = int, default = 0,
  help = "tolerated consecutive non-compressing hyperintervals" )
parser.add_argument( '-l', '--log', metavar = 'FILE',
  type = argparse.FileType( 'w' ), required = False,
  help = "log file to record all considered hyperintervals" )
args = parser.parse_args()

db = tuple( tuple( map( float, row.split() ) ) for row in args.database )
if not ( 3 <= args.sample <= len( db ) ):
  parser.error( "SIZE should be between 3 and the size of the database." )
if not ( 0 <= args.perseverance <= args.sample - 3 ):
  parser.error( "PERSEVERANCE should be between 0 and SIZE-3." )
if args.thoroughness < 0:
  parser.error( "THOROUGHNESS should not be negative." )
sample = random.sample( db, args.sample )
debug = args.log


### COMPLEXITY RELATED MACHINERY ###

def comp_hint_comp( hint ):
  """Comparative hint complexity calculation."""
  inside_count = hint_tools.covered( hint, db )
  outside_count = len( db ) - inside_count
  hint_volume = db_measure.volume( hint[0], hint[1] )
  complexity = inside_count * log( hint_volume / inside_count )
  if outside_count != 0:
    complexity += \
      outside_count * log( ( db_volume - hint_volume ) / outside_count )
  if debug:
    debug.write( "{}\t{}\t{}\t{}\t{}\n".format(
      -db_measure.distance( hint[0], db_measure.hint_origin ),
      db_measure.distance( hint[1], db_measure.hint_origin ),
      hint_volume, inside_count / len( db ), complexity ) )
  return complexity


# BUG: The boundaries are often found in low density regions. The sample is not
#      the most accurate source of coordinates in those situations.
def grow_hint( hint, sample ):
  """Grow the hyperinterval to its maximal informativeness."""
  complexity = comp_hint_comp( hint )
  sample_out = [ row for row in sample
                     if not hint_tools.is_covered( row, hint ) ]
  perseverance = args.perseverance
  while sample_out:
    candidate = sample_out.pop(
      min( range( len( sample_out ) ),
           key = lambda i: db_measure.distance( sample_out[i], hint[0] )
                           + db_measure.distance( sample_out[i], hint[1] ) ) )
    hint_candidate = tuple( map( min, candidate, hint[0] ) ), \
                     tuple( map( max, candidate, hint[1] ) )
    complexity_candidate = comp_hint_comp( hint_candidate )
    if complexity_candidate < complexity:
      complexity, hint = complexity_candidate, hint_candidate
      perseverance = args.perseverance
    else:
      perseverance -= 1
      if perseverance < 0: break
  else:
    print( "Sample exhausted. "
           "Try a larger sample, or lower your perseverance." )
  return hint, complexity


### ENTRANCE HOOKS ###

def hints( sample = sample ):
  global db_volume
  db_volume = db_measure.volume( *db_measure.measure_init( db, sample ) )
  if debug: debug.write( "#left\tright\tsize\tcoverage\tcomplexity\n" )
  db_comp_comp = len( db ) * log( db_volume / len( db ) ) \
                 - ( 2 * log( db_volume ) - log( 2 )
                     - 2 * log( db_measure.discretization_constant ) )
  hint = db_measure.hint_init()
  thoroughness = args.thoroughness
  while hint:
    hint, complexity = grow_hint( hint, sample )
    if debug: debug.write( "\n\n" )
    if complexity < db_comp_comp:
      thoroughness = args.thoroughness
      yield hint, complexity, 1
    else:
      thoroughness -= 1
      yield hint, complexity, 0
      if thoroughness < 0: break
    hint = db_measure.hint_init( hint )


if __name__ == "__main__":
  try:
    for run, ( hint, complexity, keep ) in enumerate( hints() ):
      print( "Hyperinterval {}:".format( run ), hint, complexity,
             "KEPT" if keep else "DISCARDED" )
  except KeyboardInterrupt:
    print( "Interrupted" )
  # If the volume is normalized to 1, the following prints 0.
  # This is not a bug.
  print( "Single uniform data complexity:             ",
         len( db ) * log( db_volume ) )
  print( "Comparative single uniform data complexity: ",
         len( db ) * log( db_volume / len( db ) ) )
  print( "Discretized double uniform model complexity:",
         2 * log( db_volume ) - log( 2 )
         - 2 * log( db_measure.discretization_constant ) )

