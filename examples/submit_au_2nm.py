__author__ = 'christopher'
"""
This use case examines how to submit to the db using experimental data starting
with a previously refined 2nm SnOx structure based on PDF+FF
Note: This is the first run on the DB for this work, so everything needs to be
entered, once the DB is more fully populated then many of the insert_*
statements can be replaced with find_* statements, with associated changes made
to the internal parameters, followed by a obj.save() call.
"""
import ase
from simdb.insert import *
from simdb.search import *


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
