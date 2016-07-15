import simdb
from uuid import uuid4
import simdb
from simdb.odm_templates import AtomicConfig
from simdb.insert import *
from simdb.search import *
import time as ttime
import tempfile
import ase
from simdb.utils.testing import simdb_setup, simdb_teardown
from nose.tools import assert_equal, assert_not_equal
from pyiid.experiments.elasticscatter import ElasticScatter

__author__ = 'christopher'


def setup():
    simdb_setup()
    simdb.EXP_DATA_PATH = tempfile.gettempdir()
    simdb.ATOM_PATH = tempfile.gettempdir()


def teardown():
    # gets run last
    simdb_teardown()


def test_insert_and_retrieve_fabricated_data():
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])
    a = insert_atom_document('au2', atoms)
    ret, = find_atomic_config_document(_id=a.id)

    pdf = insert_experimental_1d_data_document('test au2', atomic_config=ret)

    ret_pdf, = find_1d_data_document(_id=pdf.id)
    s = ElasticScatter()
    actual_gr = s.get_pdf(ret.file_payload[0])
    # make sure the retrieved document got something from filestore
    assert (hasattr(ret_pdf, 'file_payload'))
    # make sure the payload is equivalent to the original atoms
    assert (np.all(actual_gr == ret_pdf.file_payload))
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(actual_gr), id(ret_pdf.file_payload))


def test_insert_and_retrieve_actual_data():
    file_loc = 'simdb/tests/FinalSum_Ni_STD.gr'
    pdf = insert_experimental_1d_data_document('test actual',
                                               input_filename=file_loc)

    ret_pdf, = find_1d_data_document(_id=pdf.id)

    actual_gr = load_gr_file(file_loc)[1]
    # make sure the retrieved document got something from filestore
    assert (hasattr(ret_pdf, 'file_payload'))
    # make sure the payload is equivalent to the original atoms
    print(ret_pdf.file_payload)
    assert (np.all(actual_gr == ret_pdf.file_payload))
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(actual_gr), id(ret_pdf.file_payload))
