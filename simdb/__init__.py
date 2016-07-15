from . import odm_templates
from .odm_templates import DATABASE_ALIAS
import os

connection_config = {'host': 'localhost',
                     'database': 'simdb',
                     'port': 27017,
                     'timezone': 'US/Eastern'}

ATOM_PATH = os.path.join('/mnt/bulk-data/', 'data', 'ase-atoms')
EXP_DATA_PATH = os.path.join('/mnt/bulk-data/', 'data', 'PDF')
from . import handlers
