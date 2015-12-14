__author__ = 'christopher'
"""
This use case examines how to submit a job when using simulated data
"""
import ase
from simdb.insert import *
from simdb.search import *
from pyiid.utils import build_sphere_np
from copy import deepcopy as dc
from ase.visualize import view


# starting_atoms = ase.io.read(
#     '/mnt/bulk-data/Dropbox/BNL_Project/Simulations/Models.d/2-AuNP-DFT.d/SizeVariation.d/Au55.Oh_ini.xyz')

# Add the atoms to the DB
# start_config = insert_atom_document('Au Oh Starting', starting_atoms)
start_config = next(find_atomic_config_document(name='Au Oh Starting'))

# parent_atoms = ase.io.read(
#     '/mnt/work-data/dev/IID_data/examples/Au/55_amorphous/no_lammps/Au55.300K_amorphous.xyz'
# )

# target_config = insert_atom_document('Au amorph Target', parent_atoms)
target_config = next(find_atomic_config_document(name='Au amorph Target'))

# pdf = insert_pdf_data_document('Au amorph Target', atomic_config=target_config)
pdf = next(find_1d_data_document(name='Au amorph Target'))

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
exp_dict['qmin'] = .1
exp_dict['rmin'] = 2.5
exp_dict['rmax'] = 14.

# Now create the kwargs for the two calculators: PDF and Spring
calc_kwargs1 = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
calc1 = insert_calc('Au amorph Target Rw', 'PDF', calc_kwargs1, target_data=pdf)

calc_kwargs2 = {'k': 200, 'rt': exp_dict['rmin']}
calc2 = insert_calc('Au amorph Target spring', 'Spring', calc_kwargs2)

calc_kwargs3 = {'k': 200, 'rt': exp_dict['rmax'], 'sp_type':'att'}
calc3 = insert_calc('Au amorph Target spring Att', 'Spring', calc_kwargs3)

# Create the combined Potential Energy Surface (PES)
calc_list = [calc1, calc2, calc3]
pes = insert_pes('Au amorph Target Rw Spring Att', calc_list)

params = insert_simulation_parameters('T=1.0, iter=300, accept=.65', 1.0, 300, .65,
                                      continue_sim=False)

# Finally create the simulation
sim = insert_simulation('Au55_Oh_to_amorph', params, start_config, pes)
print 'simulation added, number ', sim.id
