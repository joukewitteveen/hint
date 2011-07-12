#! /usr/bin/env python2
"""Plotting the inside and outside of a hyperinterval

This is Python 2 code.

(c) 2011 Jouke Witteveen
"""

from mpl_toolkits.basemap import Basemap
from matplotlib.pyplot import savefig

fh = open( 'py2to3', 'r' )
inside, outside = map( eval, fh.readlines() )
lats1, lons1 = zip( *inside )
lats0, lons0 = zip( *outside )


"""The rest is by Wouter Duivesteijn"""

#m = Basemap(projection='mill',resolution='c',llcrnrlon=-30,llcrnrlat=27,urcrnrlon=32,urcrnrlat=81)
m = Basemap(projection='mill',resolution='l',llcrnrlon=-15,llcrnrlat=33,urcrnrlon=32,urcrnrlat=72,lon_0=1,lat_0=54)

# Optie 1
#m.drawcoastlines()
#m.drawmapboundary()
#m.drawmapboundary(fill_color='aqua')
#m.fillcontinents(color='coral',lake_color='aqua')
m.drawmapboundary(fill_color='white') # fill to edge
m.drawcountries()
m.fillcontinents(color='lightgrey',lake_color='white',zorder=0)

# Optie 2
#m.bluemarble()

x, y = m(lons0,lats0)
#m.scatter(x, y, s=10, c='y')
m.scatter(x,y,s=7,c='b',marker="o",alpha=0.1)

x, y = m(lons1,lats1)
#m.scatter(x, y, s=20, c='r')
#cmap=cm.cool
m.scatter(x,y,s=7,c='r',marker="o",alpha=1)

savefig('chart7')

