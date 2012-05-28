#! /usr/bin/env python
"""Hyperinterval finder

Finds hyperintervals in a (numerical) database that have high density.

(c) 2011-2012 Jouke Witteveen
"""

import argparse, random
import hint_tools
# Customize the database measure by
#   import <custom_db_measure> as db_measure
# before importing this file
try:
  from __main__ import db_measure
except ImportError:
  import db_measure

# logarithmic function
log = hint_tools.log

db = None
sample = None
debug = None
params = {}


### ARGUMENT PARSING AND VALIDATION ###

def cli_args( *argv ):
  """Command line interface arguments"""
  global db, sample, debug
  parser = argparse.ArgumentParser( description = "Hyperinterval finder." )
  parser.add_argument( '-s', '--sample', metavar = 'SIZE',
    type = int, required = True,
    help = "sample size to determine hyperinterval boundaries" )
  parser.add_argument( 'database', type = argparse.FileType( 'r' ),
    help = "database file containing one line per entry" )
  parser.add_argument( '-p', '--perseverance', type = int, default = 0,
    help = "eagerness to not end up in local minima" )
  parser.add_argument( '-pc', '--thoroughness', type = int, default = 0,
    help = "tolerated consecutive non-compressing hyperintervals" )
  parser.add_argument( '-pd', '--dim-thoroughness', metavar = 'DIM_THOROUGH',
    type = int, default = -1,
    help = "tolerated consecutive non-discardable dimensions" )
  parser.add_argument( '-l', '--log', metavar = 'FILE',
    type = argparse.FileType( 'w' ), required = False,
    help = "log file to record all considered hyperintervals" )
  args = parser.parse_args( *argv )

  db = tuple( tuple( map( float, row.split() ) ) for row in args.database )
  if not ( 3 <= args.sample <= len( db ) ):
    parser.error( "SIZE should be between 3 and the size of the database." )
  if not ( 0 <= args.perseverance <= args.sample - 3 ):
    parser.error( "PERSEVERANCE should be between 0 and SIZE-3." )
  if args.thoroughness < 0:
    parser.error( "THOROUGHNESS should not be negative." )
  if not ( -1 <= args.dim_thoroughness < len( db[0] ) ):
    parser.error( "DIM_THOROUGH should be between -1 and dimensionality-1." )
  sample = tuple( random.sample( range( len( db ) ), args.sample ) )
  debug = args.log
  params['perseverance'] = args.perseverance
  params['thoroughness'] = args.thoroughness
  params['dim_thorough'] = args.dim_thoroughness


### COMPLEXITY RELATED MACHINERY ###

def comp_hint_comp( hint ):
  """Comparative hint complexity calculation."""
  inside_count = hint_tools.covered( hint, db )
  outside_count = len( db ) - inside_count
  hint_volume = db_measure.volume( *hint )
  complexity = inside_count * ( log( hint_volume ) - log( inside_count ) )
  if outside_count != 0:
    complexity += outside_count \
                  * ( log( db_volume - hint_volume ) - log( outside_count ) )
  if debug:
    debug.write( "{}\t{}\t{}\t{}\t{}\n".format(
      -db_measure.distance( hint[0], hint_origin ),
      db_measure.distance( hint[1], hint_origin ),
      hint_volume, inside_count / len( db ), complexity ) )
  return complexity


# SHORTCOMING: The boundaries are often found in low density regions.
#              The sample is not the most accurate source of coordinates in
#              those situations.
def grow_hint( hint, sample ):
  """Grow the hyperinterval to its maximal informativeness."""
  complexity = comp_hint_comp( hint )
  sample_out = [ i for i in sample
                   if not hint_tools.is_covered( db[i], hint ) ]
  perseverance = params['perseverance']
  while sample_out:
    candidate = db[sample_out.pop( min( range( len( sample_out ) ), key = \
      lambda i: db_measure.distance( db[sample_out[i]], hint[0] ) \
                + db_measure.distance( db[sample_out[i]], hint[1] ) ) )]
    candidate_hint = tuple( map( min, candidate, hint[0] ) ), \
                     tuple( map( max, candidate, hint[1] ) )
    candidate_comp = comp_hint_comp( candidate_hint )
    if candidate_comp < complexity:
      hint, complexity = candidate_hint, candidate_comp
      perseverance = params['perseverance']
    else:
      perseverance -= 1
      if perseverance < 0: break
  else:
    print( "Sample exhausted. "
           "Try a larger sample, or lower your perseverance." )
  return hint, complexity


### ENTRANCE HOOKS ###

def hints():
  """Generate all compressing hyperintervals."""
  global db_bound, db_volume, db_base_comp, model_comp, hint_origin
  db_bound = db_measure.measure_init( db, sample )
  db_volume = db_measure.volume( *db_bound )
  db_base_comp = len( db ) * ( log( db_volume ) - log( len( db ) ) )
  model_comp = 2 * log( db_volume ) - len( db[0] ) * log( 2 ) \
               + 2 * db_measure.discretization_const
  if debug: debug.write( "#left\tright\tsize\tcoverage\tcomplexity\n" )
  thoroughness = params['thoroughness']
  hint = db_measure.hint_init()
  while hint:
    if debug: hint_origin = tuple( map( lambda x, y: ( x + y ) / 2, *hint ) )
    hint, complexity = grow_hint( hint, sample )
    if debug: debug.write( "\n\n" )
    if complexity < db_base_comp - model_comp:
      thoroughness = params['thoroughness']
      yield hint, complexity, True
    else:
      thoroughness -= 1
      yield hint, complexity, False
      if thoroughness < 0: break
    hint = db_measure.hint_init( hint )


def prune( hint, complexity ):
  """Post-process a hyperinterval by pruning superfluous (full) dimensions."""
  dimensions = len( db[0] )
  dim_comp = model_comp / dimensions
  zbound = list( zip( *db_bound ) )
  zhint = list( zip( *hint ) )
  fullness = db_measure.fullness( hint )
  thoroughness = params['dim_thorough']
  for i in sorted( range( len( hint ) ), key = lambda i: fullness[i],
                   reverse = True ):
    zcandidate = zhint[:i] + zbound[i:i + 1] + zhint[i + 1:]
    candidate_comp = comp_hint_comp( tuple( zip( *zcandidate ) ) )
    if candidate_comp <= complexity + dim_comp:
      zhint, complexity = zcandidate, candidate_comp
      dimensions -= 1
      thoroughness = params['dim_thorough']
    else:
      thoroughness -= 1
      if thoroughness < 0: break
  zhint = [ zhint[i] if zhint[i] != zbound[i] else ( None, None )
            for i in range( len( zhint ) ) ]
  return tuple( zip( *zhint ) ), complexity, \
         complexity < db_base_comp - dimensions * dim_comp


if __name__ == "__main__":
  cli_args()
  try:
    for run, ( hint, complexity, keep ) in enumerate( hints() ):
      if params['dim_thorough'] >= 0:
        hint, complexity, keep = prune( hint, complexity )
      print( "Hyperinterval {}:".format( run ), hint, complexity,
             "KEPT" if keep else "DISCARDED" )
  except KeyboardInterrupt:
    print( "Interrupted" )
  # If the volume is normalized to 1, the following prints 0.
  # This is not a bug.
  print( "Single uniform data complexity:             ",
         len( db ) * log( db_volume ) )
  print( "Comparative single uniform data complexity: ", db_base_comp )
  print( "Discretized double uniform model complexity:", model_comp )

