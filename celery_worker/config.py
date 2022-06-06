"""
windows 不支持celery 需要使用eventlet来启动
celery.exe -A worker worker -l info -P eventlet -c 5 -c 指定协程的数量
"""
broker_url = 'redis://192.168.1.12:6379/2'
broker_pool_limit = 1000  # broker 连接池 默认10

timezone = 'Asia/Shanghai'
accept_content = ['pickle', 'json']  # pickle 序列化和反序列化（用于实例化对象）

task_serializer = 'pickle'

result_backend = 'redis://192.168.1.12:6379/3'
result_serializer = 'pickle'
result_cache_max = 10000  # 最大结果缓存数量
result_expires = 3600  # 任务结果过期时间
worker_redirect_stdouts_level = 'INFO'
