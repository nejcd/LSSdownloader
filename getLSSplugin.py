# -*- coding: utf-8 -*-
"""
/***************************************************************************
 getLSSplugin
                                 A QGIS plugin
 Download Lidar Slovenia
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsMapLayerRegistry
import qgis


# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from getLSSplugin_dockwidget import getLSSpluginDockWidget
import os.path
import os
import getLSS as lss

class getLSSplugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'getLSSplugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Get Lidar Slovenia')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'getLSSplugin')
        self.toolbar.setObjectName(u'getLSSplugin')

        #print "** INITIALIZING getLSSplugin"

        self.pluginIsActive = False
        self.dockwidget = None

        #Constants
        self.crs = ['D96TM', 'D48GK']
        self.product =['OTR', 'GKOT', 'DMR']


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('getLSSplugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/getLSSplugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Download LSS'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING getLSSplugin"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD getLSSplugin"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Get Lidar Slovenia'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------
    def unloadGrid(self, layername):
        """Unload Grid"""
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == layername:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())


    def getLayerNames(self):
        """"Get layer names"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        return layer_list

    def loadGrid(self):
        """"Load vector layer"""
        layer_names = ['Tiles LIDAR D96', 'Tiles LIDAR D48']

        #Check if grid already loaded
        layerlist = []
        layerlist = self.getLayerNames()
        for layer in layerlist:
            if layer == layer_names[0]:
                self.unloadGrid(layer_names[0])
            elif layer == layer_names[1]:
                self.unloadGrid(layer_names[1])

        #Load grid

        grid_layer_path = [os.path.dirname(__file__) + "/data/LIDAR_FISHNET_D96.shp",
                           os.path.dirname(__file__) + "/data/LIDAR_FISHNET_D48GK.shp"]
        index = self.dockwidget.comboBoxGridLayer.currentIndex()
        layer = self.iface.addVectorLayer(grid_layer_path[index], layer_names[index], "ogr")
        if not layer:
            print "Layer failed to load!"

    def getTileNames(self):
        tileNames = []
        layer = qgis.utils.iface.activeLayer()
        selected_features = layer.selectedFeatures()
        for feature in selected_features:
            tile_name = feature['NAME']
            tile_block = feature['BLOK']
            [tileE, tileN] = tile_name.split("_")
            [blok, number] = tile_block.split("_")
            tileNames.append([int(tileE), int(tileN)])
        return tileNames



    def download(self):
        tileNames = self.getTileNames()
        indexCRS = self.dockwidget.comboBoxGridLayer.currentIndex()
        indexProduct = self.dockwidget.comboBoxProduct.currentIndex()

        if self.dockwidget.lineOutput.text():
            destination = self.dockwidget.lineOutput.text()
        else:
            self.select_output_folder()
            destination = self.dockwidget.lineOutput.text()

        lss.getLSS(tileNames, self.crs[indexCRS], self.product[indexProduct], destination)

    def select_output_folder(self):
        """Select output folder"""
        folder = QFileDialog.getExistingDirectory(self.dockwidget, "Select folder")
        self.dockwidget.lineOutput.setText(folder)

    def run(self):
        """Run method that loads and starts the plugin"""
        grid_layer_name = ['Lidar D96/TM', 'Lidar D48/GK']

        if not self.pluginIsActive:
            self.pluginIsActive = True



            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = getLSSpluginDockWidget()
                self.dockwidget.comboBoxGridLayer.clear()


                self.dockwidget.comboBoxGridLayer.addItems(grid_layer_name)
                self.dockwidget.comboBoxProduct.addItems(self.product)
                self.dockwidget.loadLayer.clicked.connect(self.loadGrid)

                self.dockwidget.pushButtonOutput.clicked.connect(self.select_output_folder)
                self.dockwidget.pushButtonDownload.clicked.connect(self.download)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

