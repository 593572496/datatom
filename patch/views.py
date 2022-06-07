import os.path
import uuid
import logging
import filetype
from datatom.settings import BASE_DIR
from custom_lib.json_response import render_json
from user.logic import get_cache_or_update_cache
from common import errors
from patch.models import Patch, PatchVersion, Version
from patch.logic import query_cache_or_db, refresh_patch_cache

use_db = 'patch'

log = logging.getLogger('err')


def add_patch(request):  # 上传补丁
    user_name = request.session.get('user_name')
    user = get_cache_or_update_cache(user_name)
    if user.user_authority_list[0] == 'SuperAdmin' or user.user_authority_list[0] == 'Admin':
        file = request.FILES.get('file')
        if file:
            if filetype.guess(file).extension in ['zip', 'tar', 'rar', 'gz', 'bz2', '7z', 'xz']:
                file_name_prefix = uuid.uuid1().hex
                file_name = '-'.join([file_name_prefix, file.name])
                file_path = os.path.join(BASE_DIR, r'media\patch', file_name)
                with open(file_path, 'wb') as f:  # 开celery,不阻塞，等文件上传完毕后才能写入数据库，页面开启小窗口
                    for chunk in file.chunks():
                        f.write(chunk)
                patch_name = request.POST.get('patch_name')
                patch_description = request.POST.get('patch_description')
                patch_remarks = request.POST.get('patch_remarks')
                patch_version = request.POST.get('patch_version')
                # 手动分割上传的多个值，前端多选框应该上传的是列表？
                patch_version = patch_version.split(',')
                obj, created = Patch.objects.using(use_db).get_or_create(patch_name=patch_name,
                                                                         patch_description=patch_description,
                                                                         patch_remarks=patch_remarks,
                                                                         patch_download=file_path)
                if created:
                    for version in patch_version:
                        version_id = Version.objects.using(use_db).get(version=version).id
                        PatchVersion.patch_add_version(obj.id, version_id)
                        refresh_patch_cache()  # 刷新缓存，需要放到celery中执行
                    return render_json(None)
                else:
                    return render_json(None, errors.CREATE_NEW_PATCH_ERROR)
            else:
                return render_json(None, errors.UPLOAD_PATCH_TYPE_ERROR)
        else:
            return render_json(None, errors.UPLOAD_PATCH_IS_NONE)

    else:
        return render_json(None, errors.PATCH_CHECK_POWER_ERROR)


def delete_patch(request):  # 删除补丁
    user_name = request.session.get('user_name')
    user = get_cache_or_update_cache(user_name)
    if user.user_authority_list[0] == 'SuperAdmin':
        # 根据patch_download（具有唯一性）来删除补丁
        patch_name = request.POST.get('patch_name')
        patch_object = Patch.objects.using(use_db).get(patch_name=patch_name)
        PatchVersion.objects.using(use_db).filter(patch_id=patch_object.id).all().delete()
        if os.path.isfile(patch_object.patch_download):
            os.remove(patch_object.patch_download)
        # else: #log不能用，还没调试好
        #     log.error('文件不存在')
        patch_object.delete()
        refresh_patch_cache()
        return render_json(None)
    else:
        return render_json(None, errors.PATCH_CHECK_POWER_ERROR)


def query_all_patch(request):  # 查询所有的补丁
    return render_json(query_cache_or_db())


def modify_patch(request):  # 修改补丁
    is_change = False
    user_name = request.session.get('user_name')
    user = get_cache_or_update_cache(user_name)
    if user.user_authority_list[0] == 'SuperAdmin' or user.user_authority_list[0] == 'Admin':
        new_file = request.FILES.get('new_file')
        old_patch_name = request.POST.get('old_patch_name')
        patch_object = Patch.objects.using(use_db).get(patch_name=old_patch_name)
        if new_file:
            old_file_path = patch_object.patch_download
            if filetype.guess(new_file).extension in ['zip', 'tar', 'rar', 'gz', 'bz2', '7z', 'xz']:
                file_name_prefix = uuid.uuid1().hex
                new_file_name = '-'.join([file_name_prefix, new_file.name])
                new_file_path = os.path.join(BASE_DIR, r'media\patch', new_file_name)
                with open(new_file_path, 'wb') as f:  # 开celery,不阻塞，等文件上传完毕后才能写入数据库，页面开启小窗口
                    for chunk in new_file.chunks():
                        f.write(chunk)
                # 删除旧的文件
                if os.path.isfile(old_file_path):
                    os.remove(old_file_path)
                # else:
                #     log.error('文件不存在')
                patch_object.patch_download = new_file_path
                is_change = True
            else:
                return render_json(None, errors.UPLOAD_PATCH_TYPE_ERROR)
        new_patch_name = request.POST.get('new_patch_name')
        new_patch_description = request.POST.get('new_patch_description')
        new_patch_remarks = request.POST.get('new_patch_remarks')
        new_patch_status = request.POST.get('new_patch_status')
        if new_patch_name != patch_object.patch_name:
            patch_object.patch_name = new_patch_name
            is_change = True
        if new_patch_description != patch_object.patch_description:
            patch_object.patch_description = new_patch_description
            is_change = True
        if new_patch_remarks != patch_object.patch_remarks:
            patch_object.patch_remarks = new_patch_remarks
            is_change = True
        if new_patch_status != patch_object.patch_status:
            patch_object.patch_status = new_patch_status
            is_change = True
        new_patch_version = request.POST.get('new_patch_version')
        new_patch_version_list = new_patch_version.split(',')
        new_patch_version_list.sort()
        patch_object.query_all_version.sort()
        if new_patch_version_list != patch_object.query_all_version:  # 列表及时所有元素相等，但是顺序不同也不相等
            PatchVersion.objects.using(use_db).filter(patch_id=patch_object.id).all().delete()
            for version in new_patch_version_list:
                version_id = Version.objects.using(use_db).get(version=version).id
                PatchVersion.patch_add_version(patch_object.id, version_id)
            is_change = True
        if is_change:
            patch_object.save()
            refresh_patch_cache()  # 刷新缓存
        return render_json(None)
    else:
        return render_json(None, errors.PATCH_CHECK_POWER_ERROR)


def refresh_patch(request):
    refresh_patch_cache()
    return render_json(None)
