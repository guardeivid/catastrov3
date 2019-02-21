# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import range
from builtins import object
import os
import pickle
from qgis.PyQt.QtCore import QVariant, QSettings
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsRectangle, QgsFeatureRequest, QgsExpression, QgsCoordinateTransform)
#from qgis.utils import iface

class Utils(object):

    def __init__(self, iface):
        super(Utils, self).__init__()
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.file = os.path.join(os.path.dirname(__file__), 'settings.db')
        self.cfg = self.get_config()

    def get_config(self):
        return pickle.load(open(self.file, 'rb'))

    def set_config(self, config):
        pickle.dump(config, open(self.file, 'wb'), 2)

    def getPartidos(self):
        return self.cfg.get('partidos', [])

    def initPdos(self, combobox, partidos):
        if partidos:
            for i in range(0, len(partidos)):
                combobox.addItem(partidos[i][0], partidos[i][1])
        else:
            self.iface.messageBar().pushWarning(u'Advertencia', u'No se encontraron registros')

    def createFields(self, layer):
        fields = [
            QgsField('id', QVariant.String),
            QgsField('partido', QVariant.Int),
            QgsField('partida', QVariant.Int),
            QgsField('nomenclatura', QVariant.String),
            QgsField('codigo', QVariant.String),
            QgsField('layer', QVariant.String)
        ]
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

    def addLayerToMap(self, radiobuttonDefaultLayer, defaultLayer, baseName, path, provider, checkeboxDefaultStyle, qml):
        QgsProject.instance().layersAdded.connect( self.changeLayerAdditionMode )
        if radiobuttonDefaultLayer.isChecked():
            try:
                if QgsProject.instance().mapLayer(defaultLayer.id()) == None:
                    QgsProject.instance().addMapLayer(defaultLayer)
            except:
                defaultLayer = QgsVectorLayer(path, baseName, provider)
                defaultLayer.loadNamedStyle(os.path.join(os.path.dirname(__file__), qml))
                self.createFields(defaultLayer)
                QgsProject.instance().addMapLayer(defaultLayer)
            QgsProject.instance().layersAdded.disconnect( self.changeLayerAdditionMode )
            return {"layer":defaultLayer, "lyrDefault": True}
        else:
            layer = self.iface.addVectorLayer(path, baseName, provider)
            #layer.featureAdded.connect(lambda: self.featureAdded(layer))
            if checkeboxDefaultStyle.isChecked():
                layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), qml))
            self.createFields(layer)
            QgsProject.instance().layersAdded.disconnect( self.changeLayerAdditionMode )
            return {"layer":layer, "lyrDefault": False}

    def addResultToLayer(self, layer, result, lyrDefault, mode):
        if len(result) > 0:
            layer.startEditing()
            feats = []

            if lyrDefault is True:
                bbox = QgsRectangle()
                bbox.setMinimal()

            for res in result:
                feat = QgsFeature()
                if mode == 'web':
                    feat.setGeometry(QgsGeometry.fromMultiPolygonXY(res["geom"]))
                else:
                    feat.setGeometry(QgsGeometry.fromWkt(res["wkt"]))

                feat.setAttributes([res["id"], res["partido"], res["partida"], res["nomenclatura"], res["codigo"], res["layer"]])
                feats.append(feat)
                if lyrDefault is True:
                    bbox.combineExtentWith(feat.geometry().boundingBox())

            layer.dataProvider().addFeatures(feats)
            layer.commitChanges()
            layer.updateExtents()

            if lyrDefault is True:
                self.canvas.setExtent(self.setBboxMap(bbox, layer))
            else:
                self.canvas.setExtent(self.setBboxMap(layer.extent(), layer))

    def removeLayer(self, baseName, pdo, pda=None, cir=None, sec=None, chn=None, chl=None, qtn=None, qtl=None, frn=None, frl=None, mzn=None, mzl=None, pcn=None, pcl=None):
        layers = QgsProject.instance().mapLayersByName(baseName)
        for lyr in layers:
            QgsProject.instance().removeMapLayer(lyr.id())

        pdo.setCurrentIndex(0)
        if pda != None:
            pda.setText("")
        if cir != None:
            cir.setText("")
        if sec != None:
            sec.setText("")
        if chn != None:
            chn.setText("")
        if chl != None:
            chl.setText("")
        if qtn != None:
            qtn.setText("")
        if qtl != None:
            qtl.setText("")
        if frn != None:
            frn.setText("")
        if frl != None:
            frl.setText("")
        if mzn != None:
            mzn.setText("")
        if mzl != None:
            mzl.setText("")
        if pcn != None:
            pcn.setText("")
        if pcl != None:
            pcl.setText("")

    def getFeatureByAttributtes(self, layer, pdo_or_omencla, pda=None):
        try:
            if pda != None:
                result = layer.getFeatures(QgsFeatureRequest(QgsExpression('"partido" = {} and "partida" = {}'.format(pdo_or_omencla, pda))))
                result = list(result)
                if len(result) == 0:
                    return False
            else:
                result = layer.getFeatures(QgsFeatureRequest(QgsExpression('"codigo" = \'{}\''.format(pdo_or_omencla))))
                result = list(result)
                if len(result) == 0:
                    return False

            bbox = QgsRectangle()
            bbox.setMinimal()

            for feat in result:
                bbox.combineExtentWith(feat.geometry().boundingBox())

            layer.updateExtents()
            self.canvas.setExtent(bbox)
            layer.triggerRepaint()
            #canvas.refresh()
            return True
        except Exception as e: #en caso que la capa haya sido eliminada
            # fix_print_with_import
            print(str(e))
            return False

    def changeLayerAdditionMode( self, layers ):
        QgsProject.instance().layerTreeRegistryBridge().setLayerInsertionPoint( QgsProject.instance().layerTreeRoot(), 0 )

    def setBboxMap(self, bbox, layer):
        crs_layer = layer.crs()
        crs_canvas = self.canvas.mapSettings().destinationCrs()
        if crs_canvas.authid() != crs_layer.authid():
            try:
                xform = QgsCoordinateTransform(crs_layer, crs_canvas) #agregsr contexto en v3
                bbox = xform.transform(bbox)
            except Exception as e:
                print(str(e))
        return bbox

    def format_nomenclatura(self, nomencla):
        n = len(nomencla)
        res = ''
        bol_mac = False
        bol_pc = False

        if n > 3:
            cir = int(nomencla[3:5])
            if cir > 0:
                bol_mac = True
                res += 'Cir. ' + self.arabigo_to_romano(cir) + ' - '
        if n > 5:
            sec = nomencla[5:7].lstrip('0')
            if sec != '':
                bol_mac = True
                res += 'Sec. ' + sec + ' - '
        if n > 12:
            cha = int(nomencla[7:11])
            chal = nomencla[11:14].lstrip('0')
            if cha > 0:
                bol_mac = True
                res += 'Ch. ' + str(cha) + chal + ' - '
        if n > 19:
            qta = int(nomencla[14:18])
            qtal = nomencla[18:21].lstrip('0')
            if qta > 0:
                bol_mac = True
                res += 'Qt. ' + str(qta) + qtal + ' - '
        if n > 26:
            fra = int(nomencla[21:25])
            fral = nomencla[25:28].lstrip('0')
            if fra > 0:
                bol_mac = True
                res += 'Fr. ' + str(fra) + fral + ' - '
        if n > 33:
            maz = int(nomencla[28:32])
            mazl = nomencla[32:35].lstrip('0')
            if maz > 0:
                bol_mac = True
                res += 'Mz. ' + str(maz) + mazl + ' - '
        if n > 40:
            pac = int(nomencla[35:39])
            pacl = nomencla[39:42].lstrip('0')
            if pac > 0:
                bol_pc = True
                res += 'Pc. ' + str(pac) + pacl

        if bol_mac is True and  bol_pc is False:
            res = res[:-3]

        return res

    def arabigo_to_romano(self, num):
        romanos = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        arabigos = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        roman = ''

        if num <= 4000:
            for (i, romano) in enumerate(romanos):
                while num >= arabigos[i]:
                    roman += romano
                    num -= arabigos[i]

        return roman
