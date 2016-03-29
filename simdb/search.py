from .odm_templates import *
from filestore.api import *
from .utils import _ensure_connection, get_git_hash, get_conda_env

from pyiid.calc.multi_calc import MultiCalc
import importlib
from git import Repo
import os.path

__author__ = 'christopher'

def set_software_env(config):
    if hasattr(config, 'payload'):
        config.git_hash.append({'odm':get_git_hash(config), 
                                'payload':get_git_hash(config.payload)})
    else:
        config.git_hash.append(get_git_hash(config))
    config.conda_list.append(get_conda_env())

@_ensure_connection
def find_atomic_config_document(**kwargs):
    atomic_configs = AtomicConfig.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for atomic_config in atomic_configs:
        atomic_config.payload = retrieve(atomic_config.file_uid)
        set_software_env(atomic_config)
        yield atomic_config


@_ensure_connection
def find_1d_data_document(**kwargs):
    data_sets = OneDData.objects(__raw__=kwargs).order_by('-_id').all()
    for data_set in data_sets:
        data_set.payload = retrieve(data_set.file_uid)
        set_software_env(data_set)
        yield data_set


supported_calculators = {
    '1D': ['pyiid.calc.calc_1d', 'Calc1D', find_1d_data_document],
    'Spring': ['pyiid.calc.spring_calc', 'Spring'],
    'LAMMPS': ['ase.calculators.lammpslib', 'LAMMPSlib']
}

supported_ensembles = {
    'NUTS': ['pyiid.sim.nuts_hmc', 'NUTSCanonicalEnsemble'],
}

supported_experiments = {'PDF': ['pyiid.experiments.elasticscatter',
                                 'ElasticScatter', 'get_pdf', 'get_grad_pdf'],
                         'FQ': ['pyiid.experiments.elasticscatter',
                                'ElasticScatter', 'get_fq', 'get_grad_fq']}


def build_experiment(data_type, exp_params):
    """
    Build an experiment object from the database
    Parameters
    ----------
    data_type: str
        type of experiment
    exp_params: dict
        The experimental parameters
    Returns
    --------
    func:
        The function which generates the data
    grad:
        The gradient of the above function

    """
    if data_type in supported_experiments.keys():
        mod = importlib.import_module(supported_experiments[data_type][0])
        exp = getattr(mod, supported_experiments[data_type][1])(exp_params)
        func = getattr(exp, supported_experiments[data_type][2])
        grad = getattr(exp, supported_experiments[data_type][3])
        return func, grad


def build_calculator(calculator, calc_kwargs, target_data=None):
    """
    Build a calculator from the database

    Parameters
    ----------
    calculator: str
        The Calculator's name
    calc_kwargs: dict
        The kwargs to the calculator with the exception of target_data
    target_data: OneDData
        The target OneDdata
    Returns
    -------
    calculator

    """
    if calculator in supported_calculators.keys():
        mod = importlib.import_module(supported_calculators[calculator][0])
        calc = getattr(mod, supported_calculators[calculator][1])
        # If experimental PES put in the exp, also modify the calcs themselves
        # they may need to write their own scatter object
        if target_data is not None:
            exp, = supported_calculators[calculator][2](_id=target_data.id)
            exp_data = exp.payload
            f, g = build_experiment(target_data.data_type,
                                    target_data.exp_params)
            calc_kwargs['exp_function'] = f
            calc_kwargs['exp_grad_function'] = g
            return calc(target_data=exp_data, **calc_kwargs)
        else:
            return calc(**calc_kwargs)


def build_ensemble(ensemble, ensemble_kwargs, atoms):
    """
    Build an ensemble from the database
    Parameters
    -----------
    ensemble: str
        Name of ensemble
    ensemble_kwargs: dict
        Kwargs for the ensemble
    atoms: Ase.Atoms
        The starting atomic configuration
    """
    if ensemble in supported_ensembles.keys():
        mod = importlib.import_module(supported_ensembles[ensemble][0])
        ens = getattr(mod, supported_ensembles[ensemble][1])
        return ens(atoms, **ensemble_kwargs)


@_ensure_connection
def find_calc_document(**kwargs):
    calculators = Calc.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for calc in calculators:
        # build the calculator
        return_calc = build_calculator(
            calculator=calc.calculator,
            calc_kwargs=calc.calc_kwargs,
            target_data=calc.target_data
        )
        calc.payload = return_calc
        set_software_env(calc)
        yield calc


@_ensure_connection
def find_pes_document(**kwargs):
    potential_energy_surfaces = PES.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for pes in potential_energy_surfaces:
        calc_l = []
        for calc_params in pes.calc_list:
            # build the calculator
            calc = build_calculator(
                calculator=calc_params.calculator,
                calc_kwargs=calc_params.calc_kwargs,
                target_data=calc_params.target_data
            )
            calc_l.append(calc)
        pes.payload = MultiCalc(calc_list=calc_l)
        set_software_env(pes)
        yield pes


@_ensure_connection
def find_simulation_document(priority=False, **kwargs):
    if priority:
        sims = Simulation.objects(__raw__=kwargs).order_by('-priority',
                                                           '-_id').all()
    else:
        sims = Simulation.objects(__raw__=kwargs).order_by('-_id').all()
    for sim in sims:
        set_software_env(sim)
        yield sim


@_ensure_connection
def find_ensemble_document(atoms, **kwargs):
    ensembles = Ensemble.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for e in ensembles:
        # build the calculator
        return_ensemble = build_ensemble(
            ensemble=e.ensemble,
            ensemble_kwargs=e.calc_kwargs,
            atoms=atoms
        )
        e.payload = return_ensemble
        set_software_env(e)
        yield e
