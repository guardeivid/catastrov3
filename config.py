from builtins import object
import os
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
import pickle

class Config(object):

    def __init__(self):
        self.file = os.path.join(os.path.dirname('__file__'), 'settings.db')
        #self.file = 'C:/Users/da2/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/CatastroV3/settings.db'
        print(self.file)
        self.db = self.get_db()
        self.query = QSqlQuery(self.db)

        config = {
            'host': 'localhost',
            'dbname': '',
            'port': 5432,
            'user': '',
            'pswd': '',
            'schema': 'public',
            'layers': ["departamento", "circunscripcion", "seccion", "chacra", "quinta", "fraccion", "manzana", "parcela", "subparcela"],
            'partidos': self.get_partidos()
        }

        self.set_config(config)
        #print(config)

        config2 = self.get_config()
        print(config2)

    def get_db(self):
        if QSqlDatabase.contains("midb"):
            QSqlDatabase.removeDatabase("midb")

        db = QSqlDatabase.addDatabase("QPSQL", "midb")
        db.setHostName('localhost')
        db.setPort(5432)
        db.setDatabaseName('')
        db.setUserName('')
        db.setPassword('')
        return db

    def connect(self):
        ok = self.db.open()
        return ok

    def get_partidos(self):
        partidos = []
        if self.connect():
            sql = "SELECT id, nombre FROM public.departamento ORDER BY id"
            if self.query.exec_(sql):
                row = self.query.record()
                while self.query.next():
                    id = self.query.value(int(row.indexOf("id")))
                    nombre = self.query.value(row.indexOf("nombre"))
                    partido = [str(id) + '- ' + nombre, str(id)]
                    partidos.append(partido)
                print('Cargado todos los partidos')
            else:
                print('No se pudo ejecutar la consulta')
        else:
            print('No se pudo conectar a la base de datos')

        return partidos

    def get_config(self):
        return pickle.load(open(self.file, 'rb'))

    def set_config(self, config):
        pickle.dump(config, open(self.file, 'wb'), 2)

Config()
