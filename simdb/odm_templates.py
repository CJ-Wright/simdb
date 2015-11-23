"""
ODM templates for use with metadatstore
"""
import os

from mongoengine import DynamicDocument
from mongoengine import (StringField, DictField, IntField, FloatField,
                         ReferenceField, BooleanField, ListField, DENY)

DATABASE_ALIAS = 'simdb'

__all__ = ['ProcessedData', 'AtomicConfig', 'SimulationParameters', 'Calc',
           'PES',
           'Simulation']


class AtomicConfig(DynamicDocument):
    name = StringField(required=False)
    file_uid = StringField(required=True, unique=True)
    time = FloatField(required=True)
    generating_comment = StringField()
    meta = {'indexes': ['_id', 'name'], 'db_alias': DATABASE_ALIAS}


class ProcessedData(DynamicDocument):
    name = StringField(required=True)
    file_uid = StringField(required=True)
    experiment_uid = StringField()
    ase_config_id = ReferenceField(AtomicConfig)
    pdf_params = DictField(required=True)
    time = FloatField(required=True)
    meta = {'indexes': ['_id', 'name'], 'db_alias': DATABASE_ALIAS}


class Calc(DynamicDocument):
    name = StringField(required=True)
    calculator = StringField(required=True)
    calc_kwargs = DictField(required=True)
    target_data = ReferenceField(ProcessedData)
    meta = {'db_alias': DATABASE_ALIAS}


class PES(DynamicDocument):
    name = StringField(required=True)
    calc_list = ListField(required=True)
    meta = {'db_alias': DATABASE_ALIAS}


class Simulation(DynamicDocument):
    # Simulation Request Part, all the inputs for a simulation
    name = StringField(required=True)
    starting_atoms = ReferenceField(AtomicConfig,
                                            reverse_delete_rule=DENY,
                                            required=True,
                                            db_field='atoms_id')
    pes = ReferenceField(PES, reverse_delete_rule=DENY, required=True,
                         db_field='PES_id')
    ensemble = ReferenceField(Ensemble, reverse_delete_rule=DENY,
                              required=True, db_field='ensemble_id')
    # queue control
    priority = IntField(default=5)
    ran = BooleanField(default=False)
    skip = BooleanField(default=False)
    error = BooleanField(default=False)
    solved = BooleanField(default=False)

    # Simulation returns
    start_total_energy = ListField(default=[])
    start_potential_energy = ListField(default=[])
    start_kinetic_energy = ListField(default=[])

    final_total_energy = ListField(default=[])
    final_potential_energy = ListField(default=[])
    final_kinetic_energy = ListField(default=[])

    start_time = ListField(default=[])
    end_time = ListField(default=[])

    # Simulation metadata results
    iterations = ListField(default=[])
    total_samples = ListField(default=[])
    total_iterations = ListField(default=[])
    leapfrog_per_iter = ListField(default=[])
    seed = ListField(default=[])
    metadata = ListField(default=[])
    meta = {'db_alias': DATABASE_ALIAS}


class Ensemble(DynamicDocument):
    name = StringField(required=True)
    ensemble = StringField(required=True)
    ensemble_kwargs = DictField(required=True)
    meta = {'db_alias': DATABASE_ALIAS}
