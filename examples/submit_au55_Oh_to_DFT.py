__author__ = 'christopher'
"""
This use case examines how to submit a job when using simulated data
"""
import ase
from simdb.insert import *
from simdb.search import *
from pyiid.utils import build_sphere_np
from copy import deepcopy as dc

parent_atoms = ase.io.read(
    '/mnt/bulk-data/Dropbox/BNL_Project/Simulations/Models.d/2-AuNP-DFT.d/SizeVariation.d/Au55.Oh_rx_PBe.xyz'
)

target_config = insert_atom_document('Au DFT Target', parent_atoms)
pdf = insert_experimental_1d_data_document('Au DFT Target', atomic_config=target_config)

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
exp_dict['qmin'] = .1
exp_dict['rmin'] = 2.5
exp_dict['rmax'] = 12.

# Now create the kwargs for the two calculators: PDF and Spring
calc_kwargs1 = {'conv': 300, 'potential': 'rw', 'exp_dict': exp_dict}
calc1 = insert_calc('Au DFT Target Rw', 'PDF', calc_kwargs1, target_data=pdf)

calc_kwargs2 = {'k': 100, 'rt': exp_dict['rmin']}
calc2 = insert_calc('Au DFT Target spring', 'Spring', calc_kwargs2)

# Create the combined Potential Energy Surface (PES)
calc_list = [calc1, calc2]
pes = insert_pes('Au DFT Target Rw Spring', calc_list)

params, = find_simulation_parameter_document(
    name='T=1, iter=100, accept=.65 no continue')

# starting_atoms = ase.io.read(
#     '/mnt/bulk-data/Dropbox/BNL_Project/Simulations/Models.d/2-AuNP-DFT.d/SizeVariation.d/Au55.Oh_ini.xyz')

# Add the atoms to the DB
# start_config = insert_atom_document('Au Oh Starting', starting_atoms)
start_config, = find_atomic_config_document(name='Au Oh Starting')
# Finally create the simulation
sim = insert_simulation('Au55 Oh -> DFT', params, start_config, pes)
print 'simulation added, number ', sim.id
