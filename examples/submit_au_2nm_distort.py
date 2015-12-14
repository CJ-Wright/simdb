__author__ = 'christopher'
import ase
from simdb.insert import *
from simdb.search import *
from pyiid.utils import build_sphere_np
from copy import deepcopy as dc
from ase.cluster import *
from ase.constraints import FixAtoms
from pyiid.utils import tag_surface_atoms
from ase.visualize import view
from ase.atoms import Atoms

# name = '1nm_Au_distorted_surface_oct'
# name = '1nm_Au_distorted_surface_icos'
name = '1nm_Au_distorted_surface_fcc'

# parent_atoms = Atoms(Octahedron('Au', 4, 0))
parent_atoms = Atoms(FaceCenteredCubic('Au', [[1,0, 0], [1, 1, 0], [1, 1, 1]], (2, 4, 2)))
# parent_atoms = Icosahedron('Au', 3)

parent_atoms.set_tags(0)
tag_surface_atoms(parent_atoms)
# Prevent the core from moving
c = FixAtoms([atom.index for atom in parent_atoms if atom.tag == 0])
parent_atoms.set_constraint(c)
# move the surface
target_atoms = dc(parent_atoms)
target_atoms.rattle(.2)

start_config = insert_atom_document(name + ' starting', parent_atoms)
# start_config = next(find_atomic_config_document(name='2nm Au crystal'))
target_config = insert_atom_document(name + ' Target',
                                     target_atoms)

# Now load the G(r) data, this is not needed if it is already in the DB
pdf = insert_experimental_1d_data_document(name + ' Target',
                               atomic_config=target_config,
                               exp_dict={'rmin': 2.3, 'rmax': 13., 'qmin': .1,
                                         'qmax': 50., 'sampling': 'ns'})

# Cut the rmin and rmax data
exp_dict = pdf.pdf_params
# exp_dict['qmin'] = .1
# exp_dict['rmin'] = 2.
# exp_dict['rmax'] = 12.

# Now create the kwargs for the two calculators: PDF and Spring
calc_kwargs1 = {'conv': 300., 'potential': 'rw', 'exp_dict': exp_dict}
calc1 = insert_calc(name + ' Rw', 'PDF', calc_kwargs1,
                    target_data=pdf)

calc_kwargs2 = {'k': 200, 'rt': exp_dict['rmin']}
calc2 = insert_calc(name + ' spring', 'Spring', calc_kwargs2)
# calc2 = next(find_calc_document(name='Au102MBA44_Auonly spring'))

calc_kwargs3 = {'k': 200, 'rt': exp_dict['rmax'], 'sp_type': 'att'}
calc3 = insert_calc(name + ' spring Att', 'Spring',
                    calc_kwargs3)
# calc3 = next(find_calc_document(name='Au102MBA44_Auonly spring Att'))

# Create the combined Potential Energy Surface (PES)
calc_list = [
    calc1,
    calc2,
    calc3
]
pes = insert_pes(name + ' rw Spring Att', calc_list)
# pes, = find_pes_document(name='Au102MBA44_Auonly RW Spring Att')

# Create the simulation parameters
params = insert_simulation_parameters('T=1.0, iter=200, accept=.65', 1.0, 200,
                                      .65,
                                      continue_sim=False)

# params = next(find_simulation_parameter_document(name='T=1, iter=100, accept=.65'))
# The structure has two too many atoms, so we have to remove 2 from the surface

# Finally create the simulation
sim = insert_simulation(name, params, start_config,
                        pes)
print 'simulation added, number ', sim.id
