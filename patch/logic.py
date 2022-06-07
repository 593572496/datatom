from patch.models import Patch, PatchVersion, Version
from django.core.cache import cache
from celery_worker import call_by_worker

use_db = 'patch'
All_PATCH_CACHE_KEY = 'ALL_PATCH_CACHE_KEY'


@call_by_worker
def refresh_patch_cache():
    all_patch = Patch.objects.using(use_db).all()
    data_list = []
    for patch in all_patch:
        all_version = PatchVersion.objects.using('patch').filter(patch_id=patch.id).all()
        all_version_list = [Version.objects.using('patch').filter(id=version.version_id).first().version for
                            version in all_version]
        data = {'patch_id': patch.id, 'patch_name': patch.patch_name, 'patch_description': patch.patch_description,
                'patch_status': patch.patch_status, 'create_time': str(patch.create_time),
                'last_change': str(patch.last_change), 'patch_version': all_version_list}
        data_list.append(data)
    cache.set(All_PATCH_CACHE_KEY, data_list)


def query_cache_or_db():  # 从缓存中查询，如缓存中没有则从数据库中获取并刷新cache
    all_patch = cache.get(All_PATCH_CACHE_KEY)
    if all_patch:
        return all_patch
    else:
        refresh_patch_cache()
        return cache.get(All_PATCH_CACHE_KEY)
