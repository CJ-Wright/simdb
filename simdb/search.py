from .odm_templates import *
from filestore import commands as fsc
from filestore.api import register_handler
from .utils import _ensure_connection

from pyiid.calc.multi_calc import MultiCalc
import importlib

__author__ = 'christopher'


def build_obj(mod, obj_name, args=None, kwargs=None):
    """
    Build an object from some basic information.
    Note if any of the kwarg keys are valid uuids we will attempt to load the
    information in as a filestore retrieval
    Parameters
    ----------
    mod: str
        Module name/path
    obj_name: str
        The name of the object within the module
    args: list or tup
        The args to be passed to the object
    kwargs: dict
        The kwargs to be passed to the object
    Returns
    -------
    object:
        The built object
    """
    # If experimental PES put in the exp, also modify the calcs themselves
    # they may need to write their own scatter object
    mod = importlib.import_module(mod)
    obj = getattr(mod, obj_name)
    return obj(*args, **kwargs)


@_ensure_connection
def find_atomic_config_document(**kwargs):
    atomic_configs = AtomicConfig.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for atomic_config in atomic_configs:
        atomic_config.payload = fsc.retrieve(atomic_config.file_uid)
        yield atomic_config


@_ensure_connection
def find_1d_data_document(**kwargs):
    data_sets = ProcessedData.objects(__raw__=kwargs).order_by('-_id').all()
    for data_set in data_sets:
        data_set.payload = fsc.retrieve(data_set.file_uid)
        yield data_set


@_ensure_connection
def find_calc_document(**kwargs):
    calculators = Calc.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for calc in calculators:
        # extract/build the kwargs
        # build the calculator
        return_calc = build_obj(
            mod=calc.module,
            obj_name=calc.object_name,
            kwargs=calc.kwargs
        )
        calc.payload = return_calc
        yield calc


@_ensure_connection
def find_pes_document(**kwargs):
    potential_energy_surfaces = PES.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for pes in potential_energy_surfaces:
        calc_l = []
        for calc in pes.calcs:
            # build the calculator
            calc = find_calc_document(_id=calc)
            calc_l.append(calc.payload)
        # If we only have one calculator just use that calc
        if len(pes.calcs) == 1:
            pes.payload = calc.payload
        else:
            pes.payload = MultiCalc(calc_list=calc_l)
        yield pes


@_ensure_connection
def find_ensemble_document(atoms, **kwargs):
    ensembles = Ensemble.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for e in ensembles:
        # build the calculator
        return_ensemble = build_obj(
            mod=e.module,
            obj_name=e.object_name,
            args=atoms,
            kwargs=e.kwargs
        )
        e.payload = return_ensemble
        yield e


def build_sim(sim):
    starting_atoms = find_atomic_config_document(_id=sim.starting)
    pes = find_pes_document(_id=sim.pes)
    starting_atoms.set_calculator(pes.payload)
    opt = find_ensemble_document(atoms=starting_atoms, _id=sim.optimizer)
    return starting_atoms, pes, opt


@_ensure_connection
def find_simulation_document(priority=False, **kwargs):
    if priority:
        sims = Simulation.objects(__raw__=kwargs).order_by('-priority',
                                                           '-_id').all()
    else:
        sims = Simulation.objects(__raw__=kwargs).order_by('-_id').all()
    for sim in sims:
        yield sim
