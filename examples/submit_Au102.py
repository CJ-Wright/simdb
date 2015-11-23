__author__ = 'christopher'
import ase
from simdb.insert import *
from simdb.search import *
from pyiid.utils import build_sphere_np
from copy import deepcopy as dc
from ase.cluster.decahedron import Decahedron
# Read in the parent atoms
# parent_atoms = ase.io.read(
#     '/mnt/bulk-data/Dropbox/BNL_Project/xyz_files/Au102MBA44_Auonly.xyz')
# target_config = insert_atom_document('Au102MBA44_Auonly DFT', parent_atoms)
target_config, = find_atomic_config_document(name='Au102MBA44_Auonly DFT')

# target_config, = find_atomic_config_document(name='C60 DFT')
parent_atoms = target_config.file_payload[-1]

# Now load the G(r) data, this is not needed if it is already in the DB
pdf = insert_experimental_1d_data_document('Au102MBA44_Auonly DFT Target rmax ns',
                               atomic_config=target_config,
                               exp_dict={'rmin': 2.7, 'rmax': 15., 'qmin': .1,
                                         'qmax': 50., 'sampling': 'ns'})
# pdf = next(find_pdf_data_document(name='Au102MBA44_Auonly DFT Target'))

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
exp_dict['qmin'] = .1
exp_dict['rmin'] = 2.7
exp_dict['rmax'] = 15.

# Now create the kwargs for the two calculators: PDF and Spring
calc_kwargs1 = {'conv': 300., 'potential': 'rw', 'exp_dict': exp_dict}
calc1 = insert_calc('Au102MBA44_Auonly Rw rmax ns', 'PDF', calc_kwargs1,
                    calc_exp=pdf)

# calc_kwargs2 = {'k': 200, 'rt': exp_dict['rmin']}
# calc2 = insert_calc('Au102MBA44_Auonly rmin spring', 'Spring', calc_kwargs2)
calc2 = next(find_calc_document(name='Au102MBA44_Auonly rmin spring'))

# calc_kwargs3 = {'k': 200, 'rt': exp_dict['rmax'], 'sp_type':'att'}
# calc3 = insert_calc('Au102MBA44_Auonly rmax spring Att', 'Spring', calc_kwargs3)
calc3 = next(find_calc_document(name='Au102MBA44_Auonly rmax spring Att'))

# Create the combined Potential Energy Surface (PES)
calc_list = [calc1, calc2, calc3]
pes = insert_pes('Au102MBA44_Auonly RW rmax ns Spring Att', calc_list)
# pes, = find_pes_document(name='Au102MBA44_Auonly RW Spring Att')

# Create the simulation parameters
params = insert_simulation_parameters('T=1.0, iter=200, accept=.65', 1.0, 200,
                                      .65,
                                      continue_sim=False)

# params = next(find_simulation_parameter_document(name='T=1, iter=100, accept=.65'))
# starting_atoms = build_sphere_np('/mnt/work-data/dev/IID_data/examples/Au/10_nm/1100138.cif', 15./2)
# The structure has two too many atoms, so we have to remove 2 from the surface

# del starting_atoms[10]
# del starting_atoms[1]

# starting_atoms = Decahedron('Au', 2, 3, 1)
# starting_atoms.extend(starting_atoms[0])
# starting_atoms[-1].position += [3, 3, 0]
# Add the atoms to the DB
# start_config = insert_atom_document('Au102_mark_deca_2_3_1', starting_atoms)
start_config = next(find_atomic_config_document(name='Au102_mark_deca_2_3_1'))
# Finally create the simulation
sim = insert_simulation('Au102_mdeca_2_3_1_to_MBA_full_rmax_ns', params,
                        start_config, pes)
print 'simulation added, number ', sim.id
