# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CatastroV3DockWidget
                                 A QGIS plugin
 Search catastro
                             -------------------
        begin                : 2019-02-18
        git sha              : $Format:%H$
        copyright            : (C) 2018 by David Orellano
        email                : guardeivid@yahoo.com.ar
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
import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDockWidget
from qgis.PyQt.QtGui import QIntValidator, QRegExpValidator
from qgis.PyQt.QtCore import pyqtSignal, QRegExp, QSettings
from qgis.core import QgsVectorLayer
from .db import Db
from .web import Web
from .utils import Utils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'catastrov3_dockwidget_base.ui'))


class CatastroV3DockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(CatastroV3DockWidget, self).__init__(parent)
        self.setupUi(self)

        self.cir.setValidator(QIntValidator())
        self.chn.setValidator(QIntValidator())
        self.qtn.setValidator(QIntValidator())
        self.frn.setValidator(QIntValidator())
        self.mzn.setValidator(QIntValidator())
        self.pcn.setValidator(QIntValidator())
        validar_cadena = QRegExpValidator(QRegExp('^[0-9a-zA-Z]*$'))
        self.sec.setValidator(validar_cadena)
        self.chl.setValidator(validar_cadena)
        self.qtl.setValidator(validar_cadena)
        self.frl.setValidator(validar_cadena)
        self.mzl.setValidator(validar_cadena)
        self.pcl.setValidator(validar_cadena)

        self.pda.setValidator(QIntValidator())

        self.iface = iface
        self.mode = self.getMode()
        self.utils = Utils(iface)
        self.web = Web(iface, self.utils)
        self.db = Db(iface, self.utils)

        self.path = "MultiPolygon?crs=EPSG:22185&index=yes"
        self.provider = "memory"

        self.baseName = ["Resultados Partida Inmobiliaria", "Resultados Nomenclatura Catastral"]
        self.qml = ['estilo_pda.qml', 'estilo_nom.qml']

        self._layer1 = self.createLayerDefault(self.baseName[0], self.qml[0], self.pdo1)
        self._layer2 = self.createLayerDefault(self.baseName[1], self.qml[1], self.pdo2)

        self.pdopda = ""
        self.result1 = None

        self.nomencla = ""
        self.result2 = None

        self.initSetting()

        #eventos
        self.search1.clicked.connect(self.getPartida)
        self.clean1.clicked.connect(lambda: self.utils.removeLayer(self.baseName[0], self.pdo1, self.pda))

        self.search2.clicked.connect(self.getNomencla)
        self.clean2.clicked.connect(lambda: self.utils.removeLayer(self.baseName[1], self.pdo2, self.cir, self.sec, self.chn, self.chl, self.qtn, self.qtl, self.frn, self.frl, self.mzn, self.mzl, self.pcn, self.pcl))

        self.rbNew.toggled.connect(self.toggleButton)
        self.settingOk.clicked.connect(self.setSettings)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def getMode(self):
        qset = QSettings()
        return qset.value("/catastrov3/mode", "web", type=str)

    def setMode(self, mode):
        qset = QSettings()
        qset.setValue("/catastrov3/mode", mode)
        self.mode = mode

    def createLayerDefault(self, baseName, qml, cmboxpdo):
        layer = QgsVectorLayer(self.path, baseName, self.provider)
        layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), qml))
        self.utils.createFields(layer)
        self.utils.initPdos(cmboxpdo, self.utils.getPartidos())
        return layer

    def toggleButton(self):
        if self.rbNew.isChecked():
            self.repeat_searchs.setEnabled(False)
            self.estilo_defecto.setEnabled(True)
        else:
            self.repeat_searchs.setEnabled(True)
            self.estilo_defecto.setEnabled(False)

    def getPartida(self):
        pda = self.pda.text()
        if pda == "":
            self.iface.messageBar().pushWarning(u"Error", u"La partida no puede estar vacía")
            return None
        if self.pdo1.currentIndex() == -1:
            self.iface.messageBar().pushWarning(u'Error', u'Debe seleccionar un Partido')
            return None

        pdo = self.pdo1.itemData(self.pdo1.currentIndex())

        pdopda = pdo.zfill(3) + pda.zfill(6)

        if pdopda != self.pdopda:
            self.pdopda = pdopda
            if self.rbDefault.isChecked() and self.repeat_searchs.isChecked() is False:
                ok = self.utils.getFeatureByAttributtes(self._layer1, pdo, pda)
                if ok is True:
                    return
                else:
                    if self.mode == 'web':
                        self.result1 = self.web.get_by_partida(pdopda)
                    else:
                        self.result1 = self.db.get_by_partida(pdopda)
            else:
                if self.mode == 'web':
                    self.result1 = self.web.get_by_partida(pdopda)
                else:
                    self.result1 = self.db.get_by_partida(pdopda)
        else:
            if self.rbDefault.isChecked() and self.repeat_searchs.isChecked() is False:
                ok = self.utils.getFeatureByAttributtes(self._layer1, pdo, pda)
                if ok is True:
                    return

        if isinstance(self.result1, list):
            if len(self.result1) > 0:
                layer = self.utils.addLayerToMap(self.rbDefault, self._layer1, self.baseName[0], self.path, self.provider, self.estilo_defecto, self.qml[0])
                self.utils.addResultToLayer(layer["layer"], self.result1, layer["lyrDefault"], self.mode)
            else:
                self.iface.messageBar().pushInfo(u'Resultado', u'No se encontró la Partida Inmobiliaria')
        else:
            self.pdopda = ''

    def getNomencla(self):
        if self.pdo2.currentIndex() == -1:
            self.iface.messageBar().pushWarning(u'Error', u'Debe seleccionar un Partido')
            return None

        pdo = (self.pdo2.itemData(self.pdo2.currentIndex())).zfill(3)
        cir = self.cir.text().zfill(2)
        sec = self.sec.text().zfill(2).upper()
        chn = self.chn.text().zfill(4)
        chl = self.chl.text().zfill(3).upper()
        qtn = self.qtn.text().zfill(4)
        qtl = self.qtl.text().zfill(3).upper()
        frn = self.frn.text().zfill(4)
        frl = self.frl.text().zfill(3).upper()
        mzn = self.mzn.text().zfill(4)
        mzl = self.mzl.text().zfill(3).upper()
        pcn = self.pcn.text().zfill(4)
        pcl = self.pcl.text().zfill(3).upper()

        if pcn != '0'*4 or pcl != '0'*3:
            self.idxlayer = 7
            nomencla = pdo + cir + sec + chn + chl + qtn + qtl + frn + frl + mzn + mzl + pcn + pcl
        elif mzn != '0'*4 or mzl != '0'*3:
            self.idxlayer = 6
            nomencla = pdo + cir + sec + chn + chl + qtn + qtl + frn + frl + mzn + mzl
        elif frn != '0'*4 or frl != '0'*3:
            self.idxlayer = 5
            nomencla = pdo + cir + sec + chn + chl + qtn + qtl + frn + frl
        elif qtn != '0'*4 or qtl != '0'*3:
            self.idxlayer = 4
            nomencla = pdo + cir + sec + chn + chl + qtn + qtl
        elif chn != '0'*4 or chl != '0'*3:
            self.idxlayer = 3
            nomencla = pdo + cir + sec + chn + chl
        elif sec != '00':
            self.idxlayer = 2
            nomencla = pdo + cir + sec
        elif cir != '00':
            self.idxlayer = 1
            nomencla = pdo + cir
        else:
            self.idxlayer = 0
            nomencla = pdo

        if nomencla != self.nomencla:
            self.nomencla = nomencla
            if self.rbDefault.isChecked() and self.repeat_searchs.isChecked() is False:
                ok = self.utils.getFeatureByAttributtes(self._layer2, nomencla)
                if ok is True:
                    return
                else:
                    if self.mode == 'web':
                        self.result2 = self.web.get_by_nomencla(nomencla, self.idxlayer)
                    else:
                        self.result2 = self.db.get_by_nomencla(nomencla, self.idxlayer)
            else:
                if self.mode == 'web':
                    self.result2 = self.web.get_by_nomencla(nomencla, self.idxlayer)
                else:
                    self.result2 = self.db.get_by_nomencla(nomencla, self.idxlayer)
        else:
            if self.rbDefault.isChecked() and self.repeat_searchs.isChecked() is False:
                ok = self.utils.getFeatureByAttributtes(self._layer2, nomencla)
                if ok is True:
                    return

        if isinstance(self.result2, list):
            if len(self.result2) > 0:
                layer = self.utils.addLayerToMap(self.rbDefault, self._layer2, self.baseName[1], self.path, self.provider, self.estilo_defecto, self.qml[1])
                self.utils.addResultToLayer(layer["layer"], self.result2, layer["lyrDefault"], self.mode)
            else:
                self.iface.messageBar().pushInfo(u'Resultado', u'No se encontró la Nomenclatura Catastral')
        else:
            self.nomencla = ''

    def initSetting(self):
        if self.mode == 'web':
            self.rbWeb.setChecked(True)
        else:
            self.rbDB.setChecked(True)

        self.host.setText(self.utils.cfg.get('host', 'localhost'))
        self.port.setText(str(self.utils.cfg.get('port', 5432)))
        self.dbname.setText(self.utils.cfg.get('dbname', ''))
        self.user.setText(self.utils.cfg.get('user', ''))
        self.pswd.setText(self.utils.cfg.get('pswd', ''))

        self.schema.setText(self.db.schema)
        self.departamento.setText(self.db.layers[0])
        self.circunscripcion.setText(self.db.layers[1])
        self.seccion.setText(self.db.layers[2])
        self.chacra.setText(self.db.layers[3])
        self.quinta.setText(self.db.layers[4])
        self.fraccion.setText(self.db.layers[5])
        self.manzana.setText(self.db.layers[6])
        self.parcela.setText(self.db.layers[7])

    def setSettings(self):
        mode = 'web'
        if self.rbDB.isChecked():
            mode = 'local'
            cfg = self.utils.cfg
            schema = self.schema.text()
            layers = [
                self.departamento.text(),
                self.circunscripcion.text(),
                self.seccion.text(),
                self.chacra.text(),
                self.quinta.text(),
                self.fraccion.text(),
                self.manzana.text(),
                self.parcela.text(),
                "subparcela"
            ]

            cfg['host'] = self.host.text()
            cfg['port'] = int(self.port.text())
            cfg['dbname'] = self.dbname.text()
            cfg['user'] = self.user.text()
            cfg['pswd'] = self.pswd.text()
            cfg['schema'] = schema
            cfg['layers'] = layers

            self.db.set_schema(schema)
            self.db.set_layers(layers)
            self.db.get_db(cfg)
            self.utils.set_config(cfg)
            self.utils.cfg = cfg

        self.setMode(mode)
        self.iface.messageBar().pushInfo(u'Configuración', u'Cambiada la configuración')
