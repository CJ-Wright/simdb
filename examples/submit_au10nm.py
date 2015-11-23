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
from simdb.insert import *
from simdb.search import *
from pyiid.utils import build_sphere_np


# Read in the starting atoms
starting_atoms = build_sphere_np('/mnt/work-data/dev/IID_data/examples/Au/10_nm/1100138.cif', 100./2)

# Add the atoms to the DB
start_config = insert_atom_document('10nm_Au', starting_atoms)

# Now load the G(r) data, this is not needed if it is already in the DB
gr_file_loc = '/mnt/work-data/dev/IID_data/examples/Au/10_nm/Au_10nm_d204-00002_00009_sum.gr'
pdf = insert_experimental_1d_data_document('10nm Au PDF data', input_filename=gr_file_loc)

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
exp_dict['rmin'] = 2.4
# exp_dict['rmax'] = 40.

# Now create the kwargs for the two calculators: PDF and Spring
calc_kwargs1 = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
calc1 = insert_calc('10nm Au PDF Rw calc', 'PDF', calc_kwargs1, calc_exp=pdf)

calc_kwargs2 = {'k': 100, 'rt': exp_dict['rmin']}
calc2 = insert_calc('10nm Au spring', 'Spring', calc_kwargs2)

# Create the combined Potential Energy Surface (PES)
calc_list = [calc1, calc2]
pes = insert_pes('PDF Spring', calc_list)

# Create the simulation parameters
params = insert_simulation_parameters('test param', 1., 100, .65)

# Finally create the simulation
sim = insert_simulation('10nm_Au_PDF+Spring', params, start_config, pes)
print 'simulation added, number ', sim.id
