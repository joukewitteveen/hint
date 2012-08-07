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
  sample = tuple( random.sample( range( len( db ) ), args.sample ) )
  debug = args.log
  params['perseverance'] = args.perseverance
  params['thoroughness'] = args.thoroughness


### COMPLEXITY RELATED MACHINERY ###

def comp_hint_comp( hint ):
  """Comparative hint complexity calculation."""
  inside_count = hint_tools.covered( hint, db )
  outside_count = len( db ) - inside_count
  hint_lvolume = db_measure.lvolume( hint )
  complexity = inside_count * ( hint_lvolume - log( inside_count ) )
  #complexity = inside_count * ( hint_lvolume - log( len( db ) / 2 ) )
  if outside_count != 0:
    # We approximate the outside volume.
    complexity += outside_count * ( db_dim - log( outside_count ) )
    #complexity += outside_count * ( db_dim - log( len( db ) / 2 ) )
  if debug:
    debug.write( "{}\t{}\t{}\n".format(
      hint_lvolume, inside_count / len( db ), complexity ) )
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
      lambda i: db_measure.distance( db[sample_out[i]], hint ) ) )]
    candidate_hint = tuple( map( min, candidate, hint ) )
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
  global db_dim, db_base_comp, model_comp
  db_dim = db_measure.measure_init( db )
  db_base_comp = len( db ) * ( db_dim - log( len( db ) ) )
  model_comp = db_dim * log( 2 )
  hint_tools.queue_init( db, sample, db_measure.distance )
  if debug: debug.write( "#size\tcoverage\tcomplexity\n" )
  thoroughness = params['thoroughness']
  hint = hint_tools.next_hint()
  while hint:
    hint, complexity = grow_hint( hint, sample )
    keep = complexity < db_base_comp - model_comp
    yield hint, complexity, keep
    if keep:
      thoroughness = params['thoroughness']
    else:
      thoroughness -= 1
      if thoroughness < 0: break
    if debug: debug.write( "\n\n" )
    hint = hint_tools.next_hint( hint )


if __name__ == "__main__":
  cli_args()
  try:
    for run, ( hint, complexity, keep ) in enumerate( hints() ):
      which = tuple( i for i, x in enumerate( hint ) if x )
      print( "Hyperinterval {}:".format( run ), which, complexity,
             "KEPT" if keep else "DISCARDED" )
  except KeyboardInterrupt:
    print( "Interrupted" )
  print( "Single uniform data complexity:",
         len( db ) * db_dim )
  print( "Comparative data complexity:   ", db_base_comp )
  print( "Model complexity:              ", model_comp )

