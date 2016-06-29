from __future__ import print_function
import os
import time as ttime
from uuid import uuid4
import simdb
from ase import io as aseio
from .utils import _ensure_connection
from .odm_templates import *
from filestore import commands as fsc
from .readers.pdfgetx3_gr import load_gr_file
import numpy as np
from .search import *

__author__ = 'christopher'


@_ensure_connection
def insert_atom_document(name, ase_object, time=None):
    if time is None:
        time = ttime.time()
    # at some level, you dont actually care where this thing is on disk
    file_uid = str(uuid4())

    is_trajectory = False
    if isinstance(ase_object, list):
        is_trajectory = True

    # create the filename
    file_name = os.path.join(simdb.ATOM_PATH, file_uid + '.traj')
    # save the object
    aseio.write(file_name, ase_object)

    # do the filestore magic
    resource = fsc.insert_resource('ase', file_name)
    fsc.insert_datum(resource, file_uid,
                     datum_kwargs={'is_trajectory': is_trajectory})

    # create an instance of a mongo document (metadata)
    a = AtomicConfig(name=name, file_uid=file_uid, time=time)
    # save the document
    a.save()
    return a


@_ensure_connection
def insert_experimental_1d_data_document(name, input_filename=None,
                                         parameter_function=None,
                                         filestore_handle='pdfgetx3',
                                         time=None):
    if time is None:
        time = ttime.time()
    # at some level, you dont actually care where this thing is on disk
    file_uid = str(uuid4())

    # Then the data is experimental, thus we should let filestore know it
    # exists, and load the PDF generating parameters into the Metadata
    res = fsc.insert_resource(filestore_handle, input_filename)
    fsc.insert_datum(res, file_uid)
    params = parameter_function(input_filename)

    # create an instance of a mongo document (metadata)
    a = ProcessedData(name=name, file_uid=file_uid,
                      # experiment_uid=exp_uid,
                      exp_params=params, time=time)
    # save the document
    a.save()
    return a


@_ensure_connection
def insert_generated_1d_data_document(name,
                                      atomic_config=None, exp_func=None,
                                      exp_params=None,
                                      handler='genpdf',
                                      time=None):
    if time is None:
        time = ttime.time()
    # at some level, you dont actually care where this thing is on disk
    file_uid = str(uuid4())
    # create the filename
    file_name = os.path.join(simdb.PDF_PATH, file_uid + '.gr')

    # get the atomic configuration from the DB
    atomic_doc, = find_atomic_config_document(_id=atomic_config.id)
    atoms = atomic_doc.file_payload[-1]

    # Generate the PDF from the atomic configuration
    data = exp_func(atoms)
    generated = True

    # Save the gobs
    # TODO: replace with context
    f = open(file_name, 'w')
    np.save(f, data)
    f.close()
    res = fsc.insert_resource(handler, file_name)
    fsc.insert_datum(res, file_uid)

    # create an instance of a mongo document (metadata)
    if generated is True:
        a = ProcessedData(name=name, file_uid=file_uid,
                          ase_config_id=atomic_config,
                          exp_params=exp_params, time=time)
    a.save()
    return a


@_ensure_connection
def insert_calc(name, calculator, calc_kwargs, calc_exp=None, time=None):
    try:
        if calc_exp is None:
            existing_calc = next(
                find_calc_document(name=name, calculator=calculator,
                                   calc_kwargs=calc_kwargs))
        else:
            existing_calc = next(
                find_calc_document(name=name, calculator=calculator,
                                   calc_kwargs=calc_kwargs, calc_exp=calc_exp))

        print('Record already exists with id {}'.format(existing_calc.id))
        print('Returning the existing calculator')
        return existing_calc

    except:
        if time is None:
            time = ttime.time()
        if calc_exp is not None:
            calc = Calc(name=name, calculator=calculator,
                        calc_kwargs=calc_kwargs,
                        calc_exp=calc_exp, time=time)
        else:
            calc = Calc(name=name, calculator=calculator,
                        calc_kwargs=calc_kwargs,
                        time=time)
        # save the document
        calc.save(validate=True, write_concern={"w": 1})
        return calc


@_ensure_connection
def insert_pes(name, calc_list, time=None):
    try:
        existing_pes = next(find_pes_document(name=name, calc_list=calc_list))
        print('Record already exists with id {}'.format(existing_pes.id))
        print('Returning the existing calculator')
        return existing_pes
    except:
        if time is None:
            time = ttime.time()
        pes = PES(name=name, calc_list=calc_list,
                  time=time)
        # save the document
        pes.save(validate=True, write_concern={"w": 1})
        return pes


@_ensure_connection
def insert_simulation(name, starting_atoms, pes, ensemble, skip=False,
                      iterations=100,
                      time=None):
    if time is None:
        time = ttime.time()
    if iterations is None:
        iteration = []
    else:
        iteration = [iterations]
    sp = Simulation(name=name, starting_atoms=starting_atoms,
                    ensemble=ensemble, pes=pes, iterations=iteration, skip=skip)
    # save the document
    sp.save(validate=True, write_concern={"w": 1})
    return sp
