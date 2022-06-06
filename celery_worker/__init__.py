import os
from celery import Celery

# 设置环境变量,加载django的settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datatom.settings')
# 创建Celery Application
celery_app = Celery('datatom')
celery_app.config_from_object('celery_worker.config')
celery_app.autodiscover_tasks()


def call_by_worker(func_):
    """将任务放在celery中异步执行"""
    task = celery_app.task(func_)
    return task.delay

#
# @celery_app.task
# def func(x, y):
#     return x * y


# func.delay(x,y),将函数放到celery去执行

"""celery 会通过django的url配置一层一层的去找被celery装饰了的函数，所以要想装饰了的函数被发现就必须要配置url，不然运行该任务就会报错没有注册"""
