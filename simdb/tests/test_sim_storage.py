__author__ = 'christopher'
import simdb
from uuid import uuid4
import simdb
from simdb.odm_templates import AtomicConfig, SimulationParameters
from simdb.insert import *
from simdb.search import *
import time as ttime
import tempfile
import ase
from simdb.utils.testing import simdb_setup, simdb_teardown
from nose.tools import assert_equal, assert_not_equal

def setup():
    simdb_setup()
    simdb.PDF_PATH = tempfile.gettempdir()
    simdb.ATOM_PATH = tempfile.gettempdir()


def teardown():
    # gets run last
    simdb_teardown()


def test_double_spring_sim():
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 1.5]])
    db_atoms = insert_atom_document('au2', atoms)


    calc_kwargs1 = {'k': 100, 'rt': 2.4}
    calc_kwargs2 = {'k': -500, 'rt': 2.0}
    a = insert_calc('test spring', 'Spring', calc_kwargs1)
    b = insert_calc('test spring', 'Spring', calc_kwargs2)

    calc_list = [a, b]

    c = insert_pes('Double Spring', calc_list)

    params = insert_simulation_parameters('test param', 1., 1, .65)

    sim = insert_simulation('test sim', params, db_atoms, c)

    ret, = find_simulation_document(_id=sim.id)

    sim_params, = find_simulation_parameter_document(_id=ret.params.id)
    assert 1 == sim_params.iterations
    assert .65 == sim_params.target_acceptance
    assert 1. == sim_params.temperature

    from pyiid.workflow.simulation import run_simulation
    run_simulation(sim)

def test_pdf_spring_sim():
    atoms = ase.Atoms('Au2', [[0, 0, 0], [0, 0, 3]])
    db_atoms = insert_atom_document('au2', atoms)

    exp_dict = {
        'qmin': 0.0,
        'qmax': 25.,
        'qbin': .1,
        'rmin': 2.6,
        # 'rmin': 1.25,
        'rmax': 5.,
        'rstep': .01
    }
    pdf_db = insert_experimental_1d_data_document('au2 test', atomic_config=db_atoms,
                                      exp_dict=exp_dict)
    calc_kwargs1 = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
    calc_kwargs2 = {'k': 500, 'rt': 2.0}
    a = insert_calc('test pdf', 'PDF', calc_kwargs1, calc_exp=pdf_db)
    b = insert_calc('test spring', 'Spring', calc_kwargs2)

    calc_list = [a, b]

    c = insert_pes('PDF Spring', calc_list)

    params = insert_simulation_parameters('test param', 1., 1, .65)

    sim = insert_simulation('test sim', params, db_atoms, c)

    ret, = find_simulation_document(_id=sim.id)

    sim_params, = find_simulation_parameter_document(_id=ret.params.id)
    assert 1 == sim_params.iterations
    assert .65 == sim_params.target_acceptance
    assert 1. == sim_params.temperature

    from pyiid.workflow.simulation import run_simulation
    run_simulation(sim)

def final_test():
    __author__ = 'christopher'
    """
    This use case examines how to submit to the db using experimental data starting
    with a previously refined 2nm Au structure based on PDF+FF
    Note: This is the first run on the DB for this work, so everything needs to be
    entered, once the DB is more fully populated then many of the insert_*
    statements can be replaced with find_* statements, with associated changes made
    to the internal parameters, followed by a obj.save() call.
    """
    import ase
    # from simdb.insert import *
    # from simdb.search import *


    # Read in the starting atoms
    starting_atoms = ase.io.read('/mnt/work-data/dev/IID_data/db_test/PDF_LAMMPS_587.traj')

    # Add the atoms to the DB
    start_config = insert_atom_document('2nm Au FF+PDF refined', starting_atoms)

    # Now load the G(r) data, this is not needed if it is already in the DB
    gr_file_loc = '/mnt/work-data/dev/IID_data/examples/Au/2_nm/10_112_15_Au_Fit2d_FinalSum.gr'
    pdf = insert_experimental_1d_data_document('2nm Au data', input_filename=gr_file_loc)

    # Cut the rmin and rmax data
    exp_dict = pdf.pdf_params
    exp_dict['rmin'] = 2.5
    exp_dict['rmax'] = 25.

    # Now create the kwargs for the two calculators: PDF and Spring
    calc_kwargs1 = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
    calc1 = insert_calc('2nm Au PDF Rw calc', 'PDF', calc_kwargs1, calc_exp=pdf)

    calc_kwargs2 = {'k': 100, 'rt': exp_dict['rmin']}
    calc2 = insert_calc('test spring', 'Spring', calc_kwargs2)

    # Create the combined Potential Energy Surface (PES)
    calc_list = [calc1, calc2]
    pes = insert_pes('PDF Spring', calc_list)

    # Create the simulation parameters
    params = insert_simulation_parameters('test param', 1., 100, .65)

    # Finally create the simulation
    sim = insert_simulation('2nm Au FF+PDF starting PES=PDF+SP', params, start_config, pes)
    print 'simulation added, number ', sim.id
