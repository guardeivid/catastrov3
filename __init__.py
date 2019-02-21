# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CatastroV3
                                 A QGIS plugin
 Search catastro
                             -------------------
        begin                : 2019-02-18
        copyright            : (C) 2019 by David Orellano
        email                : guardeivid@yahoo.com.ar
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
    """Load CatastroV2 class from file CatastroV3.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .catastrov3 import CatastroV3
    return CatastroV3(iface)
