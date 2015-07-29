from simdb.odm_templates import *
from filestore import commands as fsc
from filestore.api import register_handler
from .utils import _ensure_connection

from pyiid.calc.multi_calc import MultiCalc
import importlib

__author__ = 'christopher'


@_ensure_connection
def find_atomic_config_document(**kwargs):
    atomic_configs = AtomicConfig.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for atomic_config in atomic_configs:
        atomic_config.file_payload = fsc.retrieve(atomic_config.file_uid)
        yield atomic_config


@_ensure_connection
def find_pdf_data_document(**kwargs):
    pdf_data_sets = PDFData.objects(__raw__=kwargs).order_by('-_id').all()
    for data_set in pdf_data_sets:
        data_set.file_payload = fsc.retrieve(data_set.file_uid)
        yield data_set


supported_calculators = {
    'PDF': ['pyiid.calc.pdfcalc', 'PDFCalc', find_pdf_data_document],
    # 'FQ': ['pyiid.calc.fqcalc', 'FQCalc', find_fq_data_document],
    'Spring': ['pyiid.calc.spring_calc', 'Spring'],
    'LAMMPS': ['ase.calculators.lammpslib', 'LAMMPSlib']
}


def build_calculator(calculator, calc_kwargs, calc_exp=None):
    if calculator in supported_calculators.keys():
        # If experimental PES put in the exp, also modify the calcs themselves
        # they may need to write their own scatter object
        mod = importlib.import_module(supported_calculators[calculator][0])
        calc = getattr(mod, supported_calculators[calculator][1])
        if calc_exp is not None:
            exp, = supported_calculators[calculator][2](_id=calc_exp.id)
            exp_data = exp.file_payload
            return calc(obs_data=exp_data, **calc_kwargs)
        else:
            return calc(**calc_kwargs)


@_ensure_connection
def find_calc_document(**kwargs):
    calculators = Calc.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for calc in calculators:
        # build the calculator
        return_calc = build_calculator(
            calculator=calc.calculator,
            calc_kwargs=calc.calc_kwargs,
            calc_exp=calc.calc_exp
        )
        calc.payload = return_calc
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
                calc_exp=calc_params.calc_exp
            )
            calc_l.append(calc)
        pes.payload = MultiCalc(calc_list=calc_l)
        yield pes


@_ensure_connection
def find_simulation_parameter_document(**kwargs):
    sim_params = SimulationParameters.objects(__raw__=kwargs).order_by(
        '-_id').all()
    for params in sim_params:
        yield params


@_ensure_connection
def find_simulation_document(priority=False, **kwargs):
    if priority:
        sims = Simulation.objects(__raw__=kwargs).order_by('-priority',
                                                           '-_id').all()
    else:
        sims = Simulation.objects(__raw__=kwargs).order_by('-_id').all()
    for sim in sims:
        yield sim
