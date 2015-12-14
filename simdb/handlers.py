__author__ = 'christopher'
import ase.io as aseio
import ase
import os
import math

from filestore.api import register_handler
from filestore.handlers import HandlerBase
import numpy as np

from simdb.readers.pdfgetx3_gr import load_gr_file

class ASEAtomsHandler(HandlerBase):
    specs = {'ase'} | HandlerBase.specs

    def __init__(self, filename):
        self.filename = str(filename)

    def __call__(self,**kwargs):
        try:
            ret = ase.io.PickleTrajectory(self.filename, 'r')[:]
        except:
            ret = ase.io.read(self.filename)
        return ret


class PDFGetX3Handler(HandlerBase):
    specs = {'pdfgetx3'} | HandlerBase.specs

    def __init__(self, filename):
        self.filename = str(filename)

    def __call__(self, **kwargs):
        return load_gr_file(self.filename, **kwargs)


class GeneratedPDFHandler(HandlerBase):
    specs = {'genpdf'} | HandlerBase.specs

    def __init__(self, filename):
        self.filename = str(filename)

    def __call__(self, **kwargs):
        return np.load(self.filename)


class FileLocation(HandlerBase):
    specs = {'fileloc'} | HandlerBase.specs

    def __init__(self, filename):
        self.filename = filename

    def __call__(self, **kwargs):
        return self.filename


handlers = [ASEAtomsHandler, PDFGetX3Handler, GeneratedPDFHandler]
for handler in handlers:
    for spec in handler.specs:
        register_handler(spec, handler)
