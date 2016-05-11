__author__ = 'christopher'
import ase.io as aseio
import ase
import os
import math

from filestore.api import register_handler
from filestore.handlers import HandlerBase
import numpy as np

# from pyiid.utils import load_gr_file

class ASEAtomsHandler(HandlerBase):
    specs = {'ase'} | HandlerBase.specs

    def __init__(self, filename):
        self.filename = str(filename)

    def __call__(self, is_trajectory):
        if is_trajectory:
            return ase.io.PickleTrajectory(self.filename, 'r')
        else:
            return ase.io.read(self.filename)

'''
class PDFGetX3Handler(HandlerBase):
    specs = {'pdfgetx3'} | HandlerBase.specs

    def __init__(self, filename):
        self.filename = str(filename)

    def __call__(self):
        return load_gr_file(self.filename)[1]
'''

class GeneratedPDFHandler(HandlerBase):
    specs = {'genpdf'} | HandlerBase.specs
    def __init__(self, filename):
        self.filename = str(filename)

    def __call__(self):
        return np.load(self.filename)

handlers = [ASEAtomsHandler,
            # PDFGetX3Handler,
            GeneratedPDFHandler]
for handler in handlers:
    for spec in handler.specs:
        register_handler(spec, handler)
