#!/usr/bin/python

from app import db
import peewee
from playhouse.shortcuts import model_to_dict

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Peewee Objects
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BaseModel(peewee.Model):
    def toJson(self):
        dict = model_to_dict(self)
        return dict
        
    class Meta:
        database = db


class Species(BaseModel):
    taxon_id = peewee.IntegerField(primary_key=True)
    scientific_name = peewee.CharField()
    common_name = peewee.CharField()


class Donor(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    public_name = peewee.CharField()
    private_name = peewee.CharField()
    taxon_id = peewee.IntegerField()
    phenotype = peewee.CharField()
    is_pool = peewee.BooleanField()


class DonorProperty(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    property = peewee.CharField()
    type = peewee.CharField()
    is_exported_to_ega = peewee.BooleanField()

    class Meta:
        db_table = 'donor_property'


class DonorMetadata(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    value = peewee.CharField()

    donor = peewee.ForeignKeyField(Donor)
    donor_property = peewee.ForeignKeyField(DonorProperty)

    class Meta:
        db_table = 'donor_metadata'


class Sample(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    public_name = peewee.CharField()
    private_name = peewee.CharField()
    public_archive_id = peewee.CharField()
    # epirr_acc = peewee.CharField()
    # EGAN = peewee.CharField()

    donor = peewee.ForeignKeyField(Donor)


class SampleProperty(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    property = peewee.CharField()
    type = peewee.CharField()
    is_exported_to_ega = peewee.BooleanField()

    class Meta:
        db_table = 'sample_property'


class SampleMetadata(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    value = peewee.CharField()

    sample = peewee.ForeignKeyField(Sample)
    sample_property = peewee.ForeignKeyField(SampleProperty)

    class Meta:
        db_table = 'sample_metadata'


class ExperimentType(BaseModel):
    name  = peewee.CharField()
    internal_assay_short_name = peewee.CharField()
    ihec_name = peewee.CharField()

    class Meta:
        db_table = 'experiment_type'


class Dataset(BaseModel):
    id = peewee.IntegerField()
    sample_id = peewee.IntegerField()
    release_status = peewee.CharField()
    EGA_EGAX = peewee.CharField()

    sample = peewee.ForeignKeyField(Sample)
    experiment_type = peewee.ForeignKeyField(ExperimentType)


class Run(BaseModel):
    id = peewee.IntegerField()
    dataset_id = peewee.IntegerField()
    run = peewee.CharField()
    lane = peewee.CharField()
    md5_read_1 = peewee.CharField()
    md5_read_2 = peewee.CharField()
    md5_encEGA_read_1 = peewee.CharField()
    md5_encEGA_read_2 = peewee.CharField()
    EGA_EGAR = peewee.CharField()


class ReleaseSet(BaseModel):
    id = peewee.IntegerField()
    release = peewee.CharField()
    name = peewee.CharField()
    description = peewee.CharField()
    EGA_EGAD = peewee.CharField()

    class Meta:
        db_table = 'release_set'


class DatasetToReleaseSet(BaseModel):
    dataset_id = peewee.IntegerField()
    release_set_id = peewee.IntegerField()

    class Meta:
        db_table = 'dataset_to_release_set'