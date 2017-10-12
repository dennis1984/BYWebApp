# -*- coding:utf-8 -*-


class WebAppRouter(object):
    """
    控制 Consumer App 应用中模型的
    所有数据库操作的路由
    """
    def db_for_read(self, model, **hints):
        module_name = self.get_module_name(model)
        if module_name == 'Admin_App':
            return 'admin'
        return None

    def db_for_write(self, model, **hints):
        module_name = self.get_module_name(model)
        if module_name == 'Admin_App':
            return 'admin'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        obj1_module_name = self.get_module_name(obj1)
        obj2_module_name = self.get_module_name(obj2)
        return None

    def allow_syncdb(self, db, model):
        return None

    @classmethod
    def get_module_name(cls, model):
        return model._meta.model.__module__.split('.', 1)[0]
