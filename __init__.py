# -*- coding: utf-8 -*-
"""
/***************************************************************************
 getLSSplugin
                                 A QGIS plugin
 Download Lidar Slovenia
                             -------------------
        begin                : 2016-11-12
        copyright            : (C) 2016 by Nejc Dougan
        email                : nejc.dougan@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load getLSSplugin class from file getLSSplugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .getLSSplugin import getLSSplugin
    return getLSSplugin(iface)
