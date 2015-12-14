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
__author__ = 'christopher'


def setup():
    simdb_setup()
    simdb.PDF_PATH = tempfile.gettempdir()
    simdb.ATOM_PATH = tempfile.gettempdir()


def teardown():
    # gets run last
    simdb_teardown()


def test_insert_and_retrieve_fabricated_data():
    from pyiid.calc.spring_calc import Spring
    from pyiid.calc.multi_calc import MultiCalc
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])

    calc_kwargs1 = {'k': 100, 'rt': 2.4}
    calc_kwargs2 = {'k': 500, 'rt': 2.0}
    a = insert_calc('test spring', 'Spring', calc_kwargs1)
    b = insert_calc('test spring', 'Spring', calc_kwargs2)

    calc_list = [a, b]

    c = insert_pes('Double Spring', calc_list)

    ret, = find_pes_document(_id=c.id)

    a_calc, = find_calc_document(_id=a.id)
    b_calc, = find_calc_document(_id=b.id)
    local = MultiCalc(calc_list=[a_calc.payload, b_calc.payload])

    atoms.set_calculator(local)
    l_energy = atoms.get_potential_energy()
    l_force = atoms.get_forces()

    atoms.set_calculator(ret.payload)
    re_force = atoms.get_forces()
    re_energy = atoms.get_potential_energy()

    # make sure the retrieved document got something from filestore
    assert(hasattr(ret, 'payload'))
    # make sure the payload is equivalent to the original atoms
    assert(np.all(l_force == re_force))
    assert(l_energy == re_energy)
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(local), id(ret.payload))

if __name__ == '__main__':
    import nose

    nose.runmodule(argv=[
        # '-s',
        '--with-doctest',
        # '--nocapture',
        '-v',
        '-x',
    ],
        # env={"NOSE_PROCESSES": 1, "NOSE_PROCESS_TIMEOUT": 599},
        exit=False)