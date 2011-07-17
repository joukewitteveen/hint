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
                     required = True,
                     help = "sample size to determine hyperinterval boundaries" )
parser.add_argument( 'database', type = argparse.FileType( 'r' ),
                     help = "database file containing one line per entry" )
parser.add_argument( '-p', '--perseverance', type = int, default = 0,
                     help = "eagerness to not end up in local minima" )
parser.add_argument( '-l', '--log', metavar = 'FILE',
                     type = argparse.FileType( 'w' ), required = False,
                     help = "log file to record all considered hyperintervals" )
args = parser.parse_args()

db = tuple( tuple( map( float, row.split() ) ) for row in args.database )
if not ( 3 <= args.sample <= len( db ) ):
  parser.error( "SIZE should be between 3 and the size of the database." )
if not ( 0 <= args.perseverance <= args.sample - 3 ):
  parser.error( "PERSEVERANCE should be between 0 and SIZE-3." )
sample = random.sample( db, args.sample )
debug = args.log


### COMPLEXITY RELATED MACHINERY ###

def comp_hint_comp( hint ):
  """Comparative hint complexity calculation."""
  inside_count = hint_tools.covered( hint, db )
  outside_count = len( db ) - inside_count
  hint_volume = db_measure.volume( hint[0], hint[1] )
  complexity = \
    outside_count * log( ( db_volume - hint_volume ) / outside_count ) \
    + inside_count * log( hint_volume / inside_count )
  if debug:
    debug.write( "{}\t{}\t{}\t{}\t{}\n".format(
      -db_measure.distance( hint[0], db_measure.hint_origin ),
      db_measure.distance( hint[1], db_measure.hint_origin ),
      hint_volume, inside_count / len( db ), complexity ) )
  return complexity


# BUG: The hint could potentially cover the entire database (out of the model)!
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
      min( enumerate( db_measure.distance( row, hint[0] )
                      + db_measure.distance( row, hint[1] )
                      for row in sample_out ), key = lambda a: a[1] )[0] )
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
  return hint


### ENTRANCE HOOKS ###

def run():
  global hint_history
  run.iteration += 1
  if __name__ != "__main__":
    print( "=> RUN", run.iteration )
  hint = db_measure.hint_init( sample, *hint_history )
  if not hint: raise SystemExit
  if debug:
    if run.iteration == 1:
      debug.write( "#left\tright\tsize\tcoverage\tcomplexity\n" )
    else: debug.write( "\n\n" )
  print( "Initial hyperinterval:         ", hint )
  hint = grow_hint( hint, sample )
  print( "Most informative hyperinterval:", hint )
  hint_history.append( hint )
run.iteration = 0


hint_history = list()
db_volume = db_measure.volume( *db_measure.measure_init( db, sample ) )


if __name__ == "__main__":
  # If the volume is normalized to 1, the following prints 0.
  # This is not a bug.
  print( "Single uniform complexity:                   ",
         len( db ) * log( db_volume ) )
  """Discretization is completely ignored.
     Partly this can be justified (log(dx) is model independent).
     The cost of specifying the luckiness region is also ignored.
     This can hardly be justified.
     For now: just add a constant C for all this ;-)."""
  # Taking into account model selection cost
  #print( "Comparative single uniform sample complexity:",
  #       len( sample ) * log( db_volume / len( sample ) ) )
  print( "Comparative single uniform complexity:       ",
         len( db ) * log( db_volume / len( db ) ) )
  run()

