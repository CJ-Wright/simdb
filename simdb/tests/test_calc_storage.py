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


def test_spring():
    from pyiid.calc.spring_calc import Spring
    calc_kwargs = {'k': 100, 'rt': 2.4}
    a = insert_calc('test spring', 'Spring', calc_kwargs)
    ret, = find_calc_document(_id=a.id)

    local_calc = Spring(**calc_kwargs)
    print(local_calc, ret.payload)
    # make sure the retrieved document got something from filestore
    assert(hasattr(ret, 'payload'))
    # make sure the payload is equivalent to the original atoms
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])
    atoms.set_calculator(local_calc)
    l_force = atoms.get_forces()
    l_energy = atoms.get_potential_energy()

    atoms.set_calculator(ret.payload)
    re_force = atoms.get_forces()
    re_energy = atoms.get_potential_energy()
    # assert(local_calc == ret.payload)
    assert(np.all(l_force == re_force))
    assert(l_energy == re_energy)
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(local_calc), id(ret.payload))


def test_pdfcalc_generated():
    from pyiid.calc.pdfcalc import PDFCalc
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])
    db_atoms = insert_atom_document('au2', atoms)

    exp_dict = {'qmin': 0.0, 'qmax': 25., 'qbin': .1, 'rmin': 2.6, 'rmax': 5.,
        'rstep': .01}
    pdf_db = insert_experimental_1d_data_document('au2 test', atomic_config=db_atoms,
                                      exp_dict=exp_dict)

    calc_kwargs = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
    a = insert_calc('test spring', 'PDF', calc_kwargs, calc_exp=pdf_db)
    ret, = find_calc_document(_id=a.id)

    pdfdata, = find_1d_data_document(_id=pdf_db.id)
    pdf = pdfdata.file_payload

    local_calc = PDFCalc(obs_data=pdf, **calc_kwargs)
    print(local_calc, ret.payload)
    # make sure the retrieved document got something from filestore
    assert(hasattr(ret, 'payload'))

    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 2.5]])
    atoms.set_calculator(local_calc)
    l_force = atoms.get_forces()
    l_energy = atoms.get_potential_energy()

    atoms.set_calculator(ret.payload)
    re_force = atoms.get_forces()
    re_energy = atoms.get_potential_energy()
    print(l_force, re_force)
    assert(np.all(l_force == re_force))
    assert(l_energy == re_energy)
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(local_calc), id(ret.payload))


def test_pdfcalc_cut():
    from pyiid.calc.pdfcalc import PDFCalc
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])
    db_atoms = insert_atom_document('au2', atoms)

    exp_dict = {'qmin': 0.0, 'qmax': 25., 'qbin': .1, 'rmin': 0., 'rmax': 40.,
        'rstep': .01}
    pdf_db = insert_experimental_1d_data_document('au2 test', atomic_config=db_atoms,
                                      exp_dict=exp_dict)
    # Here we hem in the bad data
    exp_dict['rmin'] = 3.
    exp_dict['rmax'] = 4.
    pdf_db.pdf_params = exp_dict
    pdf_db.save()

    calc_kwargs = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
    a = insert_calc('test spring', 'PDF', calc_kwargs, calc_exp=pdf_db)
    ret, = find_calc_document(_id=a.id)

    pdfdata, = find_1d_data_document(_id=pdf_db.id)
    pdf = pdfdata.file_payload

    local_calc = PDFCalc(obs_data=pdf, **calc_kwargs)
    print(local_calc.exp_dict)
    assert len(local_calc.gobs) == len(np.arange(exp_dict['rmin'], exp_dict['rmax'], exp_dict['rstep']))

    print(local_calc, ret.payload)
    # make sure the retrieved document got something from filestore
    assert(hasattr(ret, 'payload'))

    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 2.5]])
    atoms.set_calculator(local_calc)
    l_force = atoms.get_forces()
    l_energy = atoms.get_potential_energy()

    atoms.set_calculator(ret.payload)
    re_force = atoms.get_forces()
    re_energy = atoms.get_potential_energy()
    print(l_force, re_force)
    assert(np.all(l_force == re_force))
    assert(l_energy == re_energy)
    # make sure that the bits that came back from filestore are a different
    # object
    assert_not_equal(id(local_calc), id(ret.payload))


#TODO: test lammps and redo F(Q)
