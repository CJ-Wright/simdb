import simdb
from simdb.odm_templates import AtomicConfig
from simdb.insert import insert_atom_document
from simdb.search import find_atomic_config_document
import time as ttime
import tempfile
import ase
from simdb.utils.testing import simdb_setup, simdb_teardown
from nose.tools import assert_equal, assert_not_equal


def setup():
    simdb_setup()
    simdb.ATOM_PATH = tempfile.gettempdir()


def teardown():
    # gets run last
    simdb_teardown()


def test_single_config():
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])
    a = insert_atom_document('au2', atoms)
    ret, = find_atomic_config_document(_id=a.id)

    # make sure the retrieved document got something from filestore
    assert(hasattr(ret, 'payload'))
    # make sure the payload is equivalent to the original atoms
    assert(atoms == ret.payload[0])
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(atoms), id(ret.payload))


def test_traj():
    traj = [ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]]),
            ase.Atoms('Au2', [[0, 0, 0], [0, 0, 2]])]

    a = insert_atom_document('au2', traj)
    ret, = find_atomic_config_document(_id=a.id)

    # make sure the retrieved document got something from filestore
    assert(hasattr(ret, 'payload'))
    # make sure the payload is equivalent to the original atoms
    print ret.payload
    assert(traj == ret.payload)
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(traj), id(ret.payload))

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
