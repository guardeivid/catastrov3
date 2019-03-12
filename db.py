# -*- coding: utf-8 -*-

from builtins import str
from builtins import object
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from qgis.utils import iface

class Db(object):

    def __init__(self, iface, utils):
        self.iface = iface
        self.utils = utils
        self.layers = self.get_layers(utils.cfg)
        self.schema = self.get_schema(utils.cfg)
        self.db = None
        self.get_db(utils.cfg)

    def get_schema(self, cfg):
        return cfg.get('schema', 'public')

    def set_schema(self, schema):
        self.schema = schema

    def get_layers(self, cfg):
        return cfg.get('layers', ["departamento", "circunscripcion", "seccion", "chacra", "quinta", "fraccion", "manzana", "parcela", "subparcela"])

    def set_layers(self, layers):
        self.layers = layers

    def get_db(self, cfg):
        if QSqlDatabase.contains("midb"):
            if self.db:
                if self.db.isOpen():
                    self.db.close()
            QSqlDatabase.removeDatabase("midb")

        self.db = QSqlDatabase.addDatabase("QPSQL", "midb")
        self.db.setHostName(cfg.get('host', 'localhost'))
        self.db.setPort(int(cfg.get('port', 5432)))
        self.db.setDatabaseName(cfg.get('dbname', ''))
        self.db.setUserName(cfg.get('user', ''))
        self.db.setPassword(cfg.get('pswd', ''))

        self.query = QSqlQuery(self.db)

    def connect(self):
        ok = self.db.open()
        return self.db.isValid()
        #return ok

    def execute(self, sql, value, layer, idx):
        self.query.prepare(sql)
        self.query.addBindValue(value)
        if self.query.exec_():
            return self.proccess(layer, idx)
        else:
            sqlError = self.query.lastError()
            self.iface.messageBar().pushCritical('Error', sqlError.databaseText())
            return None

    def get_layer(self, idx):
        return self.layers[idx]

    def get_by_nomencla(self, nomencla, idx):
        if self.connect():
            pda = 'null::int'
            pdo = 'null::varchar'
            if idx >= 7:
                pda = 'pda::int'

            if idx == 0:
                pdo = 'nam'

            layer = self.get_layer(idx)
            sql = "SELECT cca, {} as pda, ST_Astext(geom), {} as nam FROM {}.{} WHERE cca = ?".format(pda, pdo, self.schema, layer)
            return self.execute(sql, nomencla, layer, idx)
        else:
            self.iface.messageBar().pushCritical('Error', 'No se pudo conectar a la base de datos')

    def get_by_partida(self, pdopda):
        if pdopda == '0'*9:
            return []

        if self.connect():
            layer = self.get_layer(7)
            sql = "SELECT cca, pda, ST_Astext(geom) FROM {}.{} WHERE pda = ?".format(self.schema, layer)
            return self.execute(sql, pdopda, layer, 7)
        else:
            self.iface.messageBar().pushCritical('Error', 'No se pudo conectar a la base de datos')

    def proccess(self, layer, idx):
        result = []
        while self.query.next():
            cca = self.query.value(0)
            partida = self.query.value(1)
            if partida:
                try:
                    partida = int(partida[3:])
                except ValueError:
                    partida = None

            if idx == 0:
                nomenclatura = self.query.value(3)
            else:
                nomenclatura = self.utils.format_nomenclatura(cca)

            row = {
                "id": "{}.{}".format(layer, cca),
                "partido": int(cca[:3]),
                "partida": partida,
                "nomenclatura": nomenclatura,
                "codigo": cca,
                "wkt": self.query.value(2),
                "layer": layer.capitalize()
            }
            result.append(row)
        return result
