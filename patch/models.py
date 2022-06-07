from django.db import models


class Patch(models.Model):
    STATUS = ((0, 'discard'), (1, 'normal'))
    patch_name = models.CharField(max_length=100, null=False, unique=True)
    patch_description = models.CharField(max_length=200, null=False)
    patch_download = models.CharField(max_length=200, null=False, unique=True)
    create_time = models.DateField(auto_now_add=True)
    last_change = models.DateField(auto_now=True)
    patch_remarks = models.CharField(max_length=100, null=True)
    patch_status = models.CharField(choices=STATUS, default=1, max_length=2)

    @property
    def query_all_version(self):
        if not hasattr(self, 'all_version_list'):
            all_version = PatchVersion.objects.using('patch').filter(patch_id=self.id).all()
            self.all_version_list = [Version.objects.using('patch').filter(id=version.version_id).first().version for
                                     version in all_version]
        return self.all_version_list

    def to_dict(self):
        return {
            'patch_name': self.patch_name,
            'patch_description': self.patch_description,
            'patch_remarks': self.patch_remarks,
            'patch_status': self.patch_status,
            'patch_version': self.query_all_version,
            'patch_id': self.id,
            'patch_create_time': str(self.create_time),
            'patch_last_change': str(self.last_change)
        }

    class Meat:
        db_table = 'patch'


class Version(models.Model):
    version = models.CharField(max_length=5, null=False, unique=True)

    def parent_version(self, use_db='patch'):
        if not hasattr(self, 'pversion'):
            if self.version.startswith('v2'):
                self.pversion = ParentVersion.objects.using(use_db).get(pversion='v2').pversion
            elif self.version.startswith('v3'):
                self.pversion = ParentVersion.objects.using(use_db).get(pversion='v3').pversion
            elif self.version.startswith('v4'):
                self.pversion = ParentVersion.objects.using(use_db).get(pversion='v4').pversion
            else:
                self.pversion = 'infinity'

        return self.pversion

    class Meta:
        db_table = 'version'


class ParentVersion(models.Model):
    pversion = models.CharField(max_length=8, unique=True, null=False, default='infinity')

    class Meta:
        db_table = 'parent_version'


class PatchVersion(models.Model):
    patch_id = models.IntegerField()
    version_id = models.IntegerField()

    @classmethod
    def patch_add_version(cls, patch_id, version_id, use_db='patch'):
        cls.objects.using(use_db).create(patch_id=patch_id, version_id=version_id)

    @classmethod
    def patch_remove_version(cls, patch_id, version_id, use_db='patch'):
        cls.objects.using(use_db).filter(patch_id=patch_id, version_id=version_id).detel()

    class Meta:
        db_table = 'patch_version'
