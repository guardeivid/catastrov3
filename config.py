# -*- coding: utf-8 -*-

import os
import pickle

config = {'host': '196.1.1.5', 'dbname': 'ada', 'port': 5432, 'user': 'catastro', 'pswd': 'catastro_plugin', 'schema': 'catastro022016'}
pickle.dump(config, open(os.path.join(os.path.dirname(__file__),'settings.db'), 'wb'), 2)
