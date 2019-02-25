# -*- coding: utf-8 -*-

import urllib.request
from builtins import object
import json
from qgis.core import QgsPointXY

class Web(object):

    def __init__(self, iface, utils):
        super(Web, self).__init__()
        self.iface = iface
        self.utils = utils

    def send_request(self, url):
        try:
            req = urllib.request.urlopen(url).read()
            return json.loads(req.decode('utf-8'))
        except Exception as e:
            self.iface.messageBar().pushCritical('Error', 'Servicio WFS no disponible')

    def get_request(self, cql_filter='', layer='Parcela'):
        url = "http://geo.arba.gov.ar/geoserver/idera/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=idera:{}&maxFeatures=50&outputFormat=application%2Fjson&CQL_filter={}".format(layer, cql_filter)
        return self.send_request(url)

    def get_layer(self, idx):
        layers = ["Departamento", "Circunscripcion", "Seccion%20catastral", "Chacra", "Quinta", "Fraccion", "Manzana", "Parcela", "Subparcela"]
        return layers[idx]

    def get_by_nomencla(self, nomencla, idx):
        if nomencla == '':
            return {}

        cql_filter = "cca=%27{}%27".format(nomencla)
        layer = self.get_layer(idx)
        geojson = self.get_request(cql_filter, layer)

        return self.proccess(geojson)

    def get_by_partida(self, pdopda):
        if pdopda == '0'*9:
            return {}

        cql_filter = "pda=%27{}%27".format(pdopda)
        geojson = self.get_request(cql_filter)

        return self.proccess(geojson)

    def proccess(self, geojson):
        result = []
        if geojson:
            features = geojson['features']
            for feature in features:
                geom = [[[QgsPointXY(pt[0],pt[1]) for pt in feature['geometry']['coordinates'][0] [0]]]]

                properties = feature['properties']

                (layer, __) = feature['id'].split('.')
                cca = properties['cca']
                partido = int(cca[:3])

                if layer == 'Departamento':
                    nomenclatura = properties['nam']
                else:
                    nomenclatura = self.utils.format_nomenclatura(cca)

                partida = properties.get('pda')
                if partida:
                    partida = int(partida[3:])

                feat = {
                    "id": feature['id'],
                    "partido": partido,
                    "partida": partida,
                    "nomenclatura": nomenclatura,
                    "codigo": cca,
                    "geom": geom,
                    "layer": layer
                }
                result.append(feat)

        return result
