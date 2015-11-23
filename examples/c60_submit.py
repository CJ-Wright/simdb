__author__ = 'christopher'
import ase
from simdb.insert import *
from simdb.search import *
from pyiid.utils import build_sphere_np
from copy import deepcopy as dc

# Read in the parent atoms
# parent_atoms = ase.io.read(
#     '/mnt/bulk-data/Dropbox/BNL_Project/Simulations/Models.d/1-C60.d/C60.xyz')
# target_config = insert_atom_document('C60 DFT', parent_atoms)
# target_config, = find_atomic_config_document(name='C60 DFT')

target_config, = find_atomic_config_document(name='C60 DFT')
parent_atoms = target_config.file_payload[-1]

# Now load the G(r) data, this is not needed if it is already in the DB
# pdf = insert_pdf_data_document('C60 DFT Target', atomic_config=target_config)
pdf = next(find_1d_data_document(name='C60 DFT Target'))

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
exp_dict['qmin'] = .1
exp_dict['rmin'] = 1.2
exp_dict['rmax'] = 8.

# Now create the kwargs for the two calculators: PDF and Spring
# calc_kwargs1 = {'conv': 1, 'potential': 'chi_sq', 'exp_dict': exp_dict}
# calc1 = insert_calc('C60 chi_sq', 'PDF', calc_kwargs1, calc_exp=pdf)
calc1 = next(find_calc_document(name='C60 Rw'))
# calc_kwargs2 = {'k': 200, 'rt': exp_dict['rmin']}
# calc2 = insert_calc('C60 spring', 'Spring', calc_kwargs2)
calc2 = next(find_calc_document(name='C60 spring'))

calc_kwargs3 = {'k': 200, 'rt': exp_dict['rmax'], 'sp_type':'att'}
calc3 = insert_calc('C60 spring Att', 'Spring', calc_kwargs3)

# Create the combined Potential Energy Surface (PES)
calc_list = [calc1, calc2, calc3]
pes = insert_pes('C60 RW Spring Att', calc_list)
# pes, = find_pes_document(name='C60 PDF Spring')

# Create the simulation parameters
# params = insert_simulation_parameters('T=1, iter=100, accept=.65', 1, 100, .65,
#                                       continue_sim=True)
params = next(find_simulation_parameter_document(name='T=1, iter=100, accept=.65'))
'''
# rattles = [.05, .07, .08, .1]
rattles = [.08, .1]
for rattle in rattles:
    # rattle the starting position
    starting_atoms = dc(parent_atoms)
    starting_atoms.rattle(rattle)

    # Add the atoms to the DB
    start_config = insert_atom_document('C60_' + str(rattle), starting_atoms)
    # Finally create the simulation
    sim = insert_simulation('C60_chi_sq_rattle_to_DFT_' + str(rattle), params, start_config, pes)
    print 'simulation added, number ', sim.id
'''
starting_atoms = dc(parent_atoms)
starting_atoms.positions = np.random.uniform(-exp_dict['rmax'], exp_dict['rmax'], parent_atoms.positions.shape)

# Add the atoms to the DB
start_config = insert_atom_document('C60_gas2', starting_atoms)
# Finally create the simulation
sim = insert_simulation('C60_gas_to_DFT', params, start_config, pes)
print 'simulation added, number ', sim.id
