#! /usr/bin/env python2
"""Plotting the inside and outside of a hyperinterval

This is Python 2 code.

(c) 2012 Jouke Witteveen
"""

import fileinput
from mpl_toolkits.basemap import Basemap
from matplotlib.pyplot import savefig, clf

fh = open( 'mammals.out', 'r' )
db = tuple( tuple( map( float, row.split() ) ) for row in fileinput.input() )


for i, c in enumerate( line.split() for line in fh.readlines() ):
  lat1, lon1 = zip( *[ ( db[j][0], db[j][1] ) for j, x in enumerate( c )
                                              if int( x ) == 1 ] )
  lat0, lon0 = zip( *[ ( db[j][0], db[j][1] ) for j, x in enumerate( c )
                                              if int( x ) == 0 ] )

  m = Basemap( projection='mill', resolution='i',
               llcrnrlon=-13, llcrnrlat=34, urcrnrlon=33, urcrnrlat=72 )
  m.drawlsmask( zorder=-1 )
  m.drawcoastlines( zorder=0 )
  m.drawrivers( zorder=0 )

  x, y = m( lon0, lat0 )
  m.scatter( x, y, s=7, c='b', marker="o", alpha=0.25 )
  x, y = m( lon1, lat1 )
  m.scatter( x, y, s=7, c='r', marker="o", alpha=1 )

  filename = "map{}".format( i )
  savefig( filename, dpi=150, bbox_inches='tight' )
  print( filename )
  clf()
