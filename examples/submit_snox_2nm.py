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

name = 'SnOx_2nm'

# Read in the starting atoms
starting_atoms = build_sphere_np('/mnt/work-data/dev/IID_data/examples/SnOx/1000062.cif', 23./2)

# Add the atoms to the DB
start_config = insert_atom_document(name + 'starting config', starting_atoms)

# Now load the G(r) data, this is not needed if it is already in the DB
gr_file_loc = '/mnt/work-data/dev/IID_data/examples/SnOx/SnO2_300K-sum_00608_637_sqmsklargemsk.gr'
pdf = insert_experimental_1d_data_document(name + ' PDF Target', input_filename=gr_file_loc)

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
exp_dict['rmin'] = 1.5
exp_dict['rmax'] = 24.

# Now create the kwargs for the two calculators: PDF and Spring
calc_kwargs1 = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
calc1 = insert_calc(name + ' Rw', 'PDF', calc_kwargs1, target_data=pdf)

calc_kwargs2 = {'k': 200, 'rt': exp_dict['rmin']}
calc2 = insert_calc(name + ' spring', 'Spring', calc_kwargs2)

calc_kwargs3 = {'k': 200, 'rt': exp_dict['rmax'], 'sp_type': 'att'}
calc3 = insert_calc(name + ' spring Att', 'Spring',
                    calc_kwargs3)
# Create the combined Potential Energy Surface (PES)
calc_list = [calc1, calc2, calc3]
pes = insert_pes(name + ' rw Spring Att', calc_list)

# Create the simulation parameters
params = insert_simulation_parameters('T=1.0, iter=200, accept=.65', 1.0, 200,
                                      .65,
                                      continue_sim=False)

# Finally create the simulation
sim = insert_simulation(name, params, start_config, pes)
print 'simulation added, number ', sim.id
