#!/usr/bin/python

from app import db
import peewee
from playhouse.shortcuts import model_to_dict

#----------------------------------
# All the ForeignKeys have been defined incorrectly in this model file.  However, it does work.
# As far as I can tell, everything seems to work by virtue of the side effect of an ORM bug, but only in Peewee 2.5.1.  Future peewee versions have corrected the bug and thus broken the functionality.  peewee cannot be upgraded without some rework of the models, queries and most of the javascript (almost everything).  Since this is an internal project, rarely used and the handsOnTable version is already woefully outdated (0.25.0 versus 7.4.2), no attempt at repair has been made so far. 
# Foreign keys should NOT be defined twice, as both an xxx_id field and a ForeignKey field, as such (example taken from DonorMetadata)
#    donor_id = peewee.IntegerField()
#    donor_property_id = peewee.IntegerField()
#
#    donor = peewee.ForeignKeyField(Donor)
#    donor_property = peewee.ForeignKeyField(DonorProperty)
#
# ForeignKeyFields should be defined as such:
#    donor = ForeignKeyField(db_column='donor_id', rel_model=Donor, to_field='id')
#    donor_property = ForeignKeyField(db_column='donor_property_id', rel_model=DonorProperty, to_field='id')
#
# Such duplicate definitons have created a situation where one field is used for joins by the ORM (ie. donor) but doesn't really exist in the database and another field (xxx_id) is expected through the api.
# Corrections will require changes to the queries.py and all the javascript stuff now that xxx_id fields are expected everywhere.
# 
# Addendum: Perhaps it would be possible to correct the models.py then put some ugly, hacky stuff into queries.py to preserve the API.  At least then it wouldn't require modifying the javascript.
# ---------------------------------

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Peewee Objects
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BaseModel(peewee.Model):
    def toJSON(self):
        dict = model_to_dict(self)
        return dict

    class Meta:
        database = db


class User(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField()
    email = peewee.CharField()
    can_edit = peewee.BooleanField()

    def is_authenticated(self):
        """
        This property should return True if the user is authenticated, i.e. they
        have provided valid credentials. (Only authenticated users will fulfill
        the criteria of login_required.)
        """
        return True

    def is_active(self):
        """
        This property should return True if this is an active user - in addition
        to being authenticated, they also have activated their account, not been
        suspended, or any condition your application has for rejecting an account.
        Inactive accounts may not log in (without being forced of course).
        """
        return True

    def is_anonymous(self):
        """
        This property should return True if this is an anonymous user. (Actual users
        should return False instead.)
        """
        return False

    def get_id(self):
        """
        This method must return a unicode that uniquely identifies this user, and
        can be used to load the user from the user_loader callback. Note that this
        must be a unicode - if the ID is natively an int or some other type, you will
        need to convert it to unicode.
        """
        return str(self.id)


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

    species = peewee.ForeignKeyField(Species, db_column='taxon_id')


class DonorProperty(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    property = peewee.CharField()
    type = peewee.CharField()
    is_exported_to_ega = peewee.BooleanField()

    class Meta:
        db_table = 'donor_property'


class DonorMetadata(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    donor_id = peewee.IntegerField()
    value = peewee.CharField()
    donor_property_id = peewee.IntegerField()

    donor = peewee.ForeignKeyField(Donor)
    donor_property = peewee.ForeignKeyField(DonorProperty)

    class Meta:
        db_table = 'donor_metadata'


class Sample(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    public_name = peewee.CharField()
    private_name = peewee.CharField()
    epirr_acc = peewee.CharField()
    EGA_EGAN = peewee.CharField()
    biomaterial_type = peewee.CharField()

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
    sample_id = peewee.IntegerField()
    value = peewee.CharField()

    sample = peewee.ForeignKeyField(Sample)
    sample_property = peewee.ForeignKeyField(SampleProperty)

    class Meta:
        db_table = 'sample_metadata'


class ExperimentType(BaseModel):
    name  = peewee.CharField()
    internal_assay_short_name = peewee.CharField()
    ihec_name = peewee.CharField()
    public_assay_short_name = peewee.CharField()
    ega_name = peewee.CharField()

    class Meta:
        db_table = 'experiment_type'


class Dataset(BaseModel):
    id = peewee.IntegerField()
    sample_id = peewee.IntegerField()
    release_status = peewee.CharField()
    EGA_EGAX = peewee.CharField()
    experiment_type_id = peewee.IntegerField()
    library_layout = peewee.CharField()

    sample = peewee.ForeignKeyField(Sample)
    experiment_type = peewee.ForeignKeyField(ExperimentType)


class ExperimentProperty(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    property = peewee.CharField()
    type = peewee.CharField()
    is_exported_to_ega = peewee.BooleanField()

    class Meta:
        db_table = 'experiment_property'


class ExperimentMetadata(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    dataset_id = peewee.IntegerField()
    value = peewee.CharField()

    dataset = peewee.ForeignKeyField(Dataset)
    experiment_property = peewee.ForeignKeyField(ExperimentProperty)

    class Meta:
        db_table = 'experiment_metadata'


class Run(BaseModel):
    id = peewee.IntegerField()
    dataset_id = peewee.IntegerField()
    library_name = peewee.CharField()
    run = peewee.CharField()
    lane = peewee.CharField()
    EGA_EGAR = peewee.CharField()

    dataset = peewee.ForeignKeyField(Dataset)


class RunFile(BaseModel):
    id = peewee.IntegerField()
    run_id = peewee.IntegerField()
    name = peewee.CharField()
    md5 = peewee.CharField()
    encrypted_md5 = peewee.CharField()

    run = peewee.ForeignKeyField(Run)

    class Meta:
        db_table = 'run_file'


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


class PublicTrack(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    dataset_id = peewee.IntegerField()
    assembly = peewee.CharField()
    track_type = peewee.CharField()
    md5sum = peewee.CharField()
    url = peewee.CharField()
    path = peewee.CharField()
    file_name = peewee.CharField()
    file_type = peewee.CharField()

    dataset = peewee.ForeignKeyField(Dataset)

    class Meta:
        db_table = 'public_track'
