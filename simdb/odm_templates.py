"""
ODM templates for use with simdb
Note that all the the templates get git hashes attached to them and conda lists
when they are pulled out
"""
import os
from mongoengine import DynamicDocument
from mongoengine import (StringField, DictField, IntField, FloatField,
                         ReferenceField, BooleanField, ListField, DENY)

DATABASE_ALIAS = 'simdb'

__all__ = ['OneDData', 'AtomicConfig', 'Ensemble', 'Calc', 'PES',
           'Simulation']


class AtomicConfig(DynamicDocument):
    name = StringField(required=False)
    file_uid = StringField(required=True, unique=True)
    time = FloatField(required=True)
    generating_comment = StringField()
    git_hash = ListField(default=[])
    conda_list = ListField(default=[])
    meta = {'indexes': ['_id', 'name'], 'db_alias': DATABASE_ALIAS}


class OneDData(DynamicDocument):
    name = StringField(required=True)
    file_uid = StringField(required=True)
    data_type = StringField(required=True)
    experiment_uid = StringField()
    ase_config_id = ReferenceField(AtomicConfig)
    exp_params = DictField(required=True)
    time = FloatField(required=True)
    git_hash = ListField(default=[])
    conda_list = ListField(default=[])
    meta = {'indexes': ['_id', 'name'], 'db_alias': DATABASE_ALIAS}

# TODO: Need to deal with calculators with function kwargs
# It seems that BSON can't serialize the functions
# It may be necessary to build the function/object upon search
class Calc(DynamicDocument):
    name = StringField(required=True)
    calculator = StringField(required=True)
    calc_kwargs = DictField(required=True)
    target_data = ReferenceField(OneDData)
    git_hash = ListField(default=[])
    conda_list = ListField(default=[])
    meta = {'db_alias': DATABASE_ALIAS}


class PES(DynamicDocument):
    name = StringField(required=True)
    calc_list = ListField(required=True)
    git_hash = ListField(default=[])
    conda_list = ListField(default=[])
    meta = {'db_alias': DATABASE_ALIAS}


class Ensemble(DynamicDocument):
    name = StringField(required=True)
    ensemble = StringField(required=True)
    ensemble_kwargs = DictField(required=True)
    git_hash = ListField(default=[])
    conda_list = ListField(default=[])
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
    metadata = ListField(default=[])
    git_hash = ListField(default=[])
    conda_list = ListField(default=[])
    meta = {'db_alias': DATABASE_ALIAS}
