from peewee import Model, TextField, CharField, IntegerField, ForeignKeyField, DateTimeField, CompositeKey, SQL
from settings import db

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class ExperimentType(BaseModel):
    description = TextField(null=True)
    ega_name = CharField(null=True)
    ihec_name = CharField(null=True)
    internal_assay_category = CharField(null=True)
    internal_assay_short_name = CharField(null=True)
    name = CharField(null=True, unique=True)
    public_assay_short_name = CharField(null=True)

    class Meta:
        table_name = 'experiment_type'

class Species(BaseModel):
    common_name = CharField()
    scientific_name = CharField()
    taxon_id = IntegerField(primary_key=True)

    class Meta:
        table_name = 'species'

class Donor(BaseModel):
    is_other_assembly = IntegerField(null=True)
    is_pool = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    last_modification = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    phenotype = CharField(null=True)
    private_name = CharField(null=True, unique=True)
    public_name = CharField(null=True, unique=True)
    taxon = ForeignKeyField(column_name='taxon_id', field='taxon_id', model=Species, null=True)

    class Meta:
        table_name = 'donor'

class Sample(BaseModel):
    ega_egan = CharField(column_name='EGA_EGAN', null=True)
    biomaterial_type = CharField(null=True)
    donor = ForeignKeyField(column_name='donor_id', field='id', model=Donor, null=True)
    epirr_acc = CharField(null=True)
    last_modification = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    private_name = CharField(null=True)
    public_name = CharField(null=True, unique=True)
    release_3_public_id = CharField(null=True)

    class Meta:
        table_name = 'sample'

class Dataset(BaseModel):
    ega_egax = CharField(column_name='EGA_EGAX', null=True)
    experiment_type = ForeignKeyField(column_name='experiment_type_id', field='id', model=ExperimentType, null=True)
    last_modification = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    library_layout = CharField(null=True)
    release_status = CharField(null=True)
    sample = ForeignKeyField(column_name='sample_id', field='id', model=Sample, null=True)

    class Meta:
        table_name = 'dataset'
        indexes = (
            (('sample', 'experiment_type'), True),
        )

class ReleaseSet(BaseModel):
    ega_egad = CharField(column_name='EGA_EGAD', null=True)
    description = TextField(null=True)
    name = CharField(null=True)
    release = CharField(null=True)

    class Meta:
        table_name = 'release_set'

class DatasetToReleaseSet(BaseModel):
    dataset = ForeignKeyField(column_name='dataset_id', field='id', model=Dataset)
    release_set = ForeignKeyField(column_name='release_set_id', field='id', model=ReleaseSet)

    class Meta:
        table_name = 'dataset_to_release_set'
        indexes = (
            (('dataset', 'release_set'), True),
        )
        primary_key = CompositeKey('dataset', 'release_set')

class DonorProperty(BaseModel):
    is_exported_to_ega = IntegerField()
    property = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'donor_property'

class DonorMetadata(BaseModel):
    donor = ForeignKeyField(column_name='donor_id', field='id', model=Donor)
    donor_property = ForeignKeyField(column_name='donor_property_id', field='id', model=DonorProperty)
    value = TextField(null=True)

    class Meta:
        table_name = 'donor_metadata'
        indexes = (
            (('donor', 'donor_property'), True),
        )

class ExperimentProperty(BaseModel):
    is_exported_to_ega = IntegerField()
    property = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'experiment_property'

class ExperimentMetadata(BaseModel):
    dataset = ForeignKeyField(column_name='dataset_id', field='id', model=Dataset)
    experiment_property = ForeignKeyField(column_name='experiment_property_id', field='id', model=ExperimentProperty)
    value = TextField(null=True)

    class Meta:
        table_name = 'experiment_metadata'
        indexes = (
            (('dataset', 'experiment_property'), True),
        )

class PublicTrack(BaseModel):
    assembly = CharField(null=True)
    dataset = ForeignKeyField(column_name='dataset_id', field='id', model=Dataset)
    file_name = CharField(null=True)
    file_type = CharField(null=True)
    md5sum = CharField(null=True)
    path = CharField(null=True)
    track_type = CharField(null=True)
    url = CharField(null=True)

    class Meta:
        table_name = 'public_track'

class Run(BaseModel):
    ega_egar = CharField(column_name='EGA_EGAR', null=True)
    dataset = ForeignKeyField(column_name='dataset_id', field='id', model=Dataset)
    lane = CharField()
    library_name = CharField(null=True)
    run = CharField()

    class Meta:
        table_name = 'run'
        indexes = (
            (('dataset_id', 'library_name', 'run', 'lane'), True),
        )

class RunFile(BaseModel):
    encrypted_md5 = CharField(null=True)
    md5 = CharField(null=True)
    name = CharField(null=True)
    run = ForeignKeyField(column_name='run_id', field='id', model=Run)

    class Meta:
        table_name = 'run_file'

# class RunPairedEnd(BaseModel):
#     experiment = CharField(null=True)
#     is_paired_end = CharField(null=True)
#     library_strategy = CharField(null=True)
#     sample = CharField(null=True)

#     class Meta:
#         table_name = 'run_paired_end'
#         primary_key = False

class SampleProperty(BaseModel):
    is_exported_to_ega = IntegerField()
    property = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'sample_property'

class SampleMetadata(BaseModel):
    sample = ForeignKeyField(column_name='sample_id', field='id', model=Sample)
    sample_property = ForeignKeyField(column_name='sample_property_id', field='id', model=SampleProperty)
    value = TextField(null=True)

    class Meta:
        table_name = 'sample_metadata'
        indexes = (
            (('sample', 'sample_property'), True),
        )

class User(BaseModel):
    can_edit = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    email = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'user'

