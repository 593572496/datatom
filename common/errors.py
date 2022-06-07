# register 错误代码
EMAIL_FORMAT_ERROR = 10000  # 注册时邮箱校验格式出错
VCODE_ERROR = 10001  # 注册时校验验证码失败
EMAIL_ERROR = 10002  # 注册时校验缓存中邮箱失败
USER_IS_EXIST = 10003  # 注册时用户已经存在
PASSWORD_FORMAT_ERROR = 10004  # 注册时密码不符合要求
# 登录错误代码
USER_NAME_FORMAT_ERROR = 20000  # 登录时用户名格式不正确
USER_OR_PASSWORD_ERROR = 20001  # 用户名或者密码错误
USER_CODE_ERROR = 20002  # 用户登录时验证码出错
# 中间验证错误：
USER_SESSION_ERROR = 30001  # 中间件使用session错误，请跳转至登录界面，重新登录
USER_COOKIE_ERROR = 30002  # 中间件验证cookie错误，请跳转登录界面，重新登录
# 修改用户信息时数据校验报错
POST_USER_PROFILE_ERROR = 40000
# 上传头像
UPLOAD_IMAGE_IS_NULL = 40001  # 上传的头像为空
UPLOAD_IMAGE_TYPE_IS_ERROR = 40002  # 上传的头像格式不正确，支持（png,jpeg,jpg）
UPLOAD_IMAGE_SIZE_IS_TOOBIG = 40003  # 上传的头像超过了5M

# 权限相关错误
DONT_HAVE_POWER = 50001  # 没有相应的权限
SET_POWER_ERROR = 50002  # 超级用户给普通用户设置权限时出错
DONT_MODIFY_SELF_POWER = 50003  # 超级用户无法修改自己的权限

# 删除用户相关报错
DONT_REMOVE_SELF = 60000  # 不能删除自己
REMOVE_USER_DONT_EXIST = 60001  # 删除的用户不存在
# 重置用户密码
REST_PASSWORD_USER_DONT_EXIST = 60002  # 重置密码的用户不存在
QUERY_USER_DONT_EXIST = 60003  # 查询的用户不存在

# 修改用户密码
CHECK_OLD_PASSWORD_FAILED = 60004  # 修改密码时验证旧密码失败

# patch
PATCH_CHECK_POWER_ERROR = 70000  # 删除，修改，上传补丁时权限出错
UPLOAD_PATCH_IS_NONE = 70001  # 上传的补丁文件为空
UPLOAD_PATCH_TYPE_ERROR = 70002  # 上传的格式不正确
CREATE_NEW_PATCH_ERROR = 70003  # 保存新的patch到数据库失败
