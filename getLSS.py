#!/usr/bin/env python
"""
/***************************************************************************
 Get Lidar Slovenia data.

                              -------------------
        begin                : 2016-11-12
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Nejc Dougan
        email                : nejc.dougan@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import urllib
import time

def getLSS(tiles, CRS, product, destination):
    """Download LIDAR Slovenia
    :param tiles: Array of tiles (E, N)
    :type tiles: int
    :param CRS: Coordinate system D96TM or D48GK
    :type CRS: string
    :param product: Point Cloud (OTR), Classified Point Cloud (GKOT), Digital Elevation Model (DMR)
    :type product: string
    :param destination: Folder location
    :type destination: string
    """
    blocks = [11, 12, 13, 14, 15, 16, 21, 22, 23, 24, 25, 26, 31, 32, 33, 34, 35, 36, 37]

    fileurl = urllib.URLopener()

    if product == 'OTR':
        extension = 'zlas'
        fileprefix = 'R'
    elif product == 'GKOT':
        extension = 'zlas'
        fileprefix = ''
    elif product == 'DMR':
        extension = 'asc'
        fileprefix = '1'
        product = 'dmr1'
    else:
        print 'Wrong product name'



    [tileE, tileN] = tiles
    filename = '{0}{1}_{2}_{3}.{4}'.format(CRS[-2:], fileprefix, tileE, tileN, extension)
    print 'Downloading: ' + filename
    download = False
    for block in blocks:
        if download:
            time.sleep(1)
            break
        url = 'http://gis.arso.gov.si/lidar/{0}/b_{1}/{2}/{3}'.format(product, block, CRS, filename)
        try:
            fileurl.retrieve(url, destination + '/' + filename)
            download = True
        except:
            next

    if download:
        print 'Done downloading: ' + filename
    else:
        print 'Download failed'

    return


def creatListOfTiles(startE, startN, endE, endN):
    """Create list of tiles from opposite corner tiles.
    :param startE: Upper left Tile Easting E
    :type startE: int
    :param startN: Upper left Tile Northing N
    :type startN: int
    :param endE: Lower right Tile Easting N
    :type endE: int
    :param endN: Lower right Tile Northing N
    :type endN: int
    """
    E = startE
    N = startN
    tiles = []
    while E <= endE:
        N = startN
        while N >= endN:
            tiles.append([E, N])
            N -= 1
        E += 1
    return tiles


