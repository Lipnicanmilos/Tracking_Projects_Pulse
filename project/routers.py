class AppRouter:
    """
    A router to control all database operations on models in the user application.
    """
    def db_for_read(self, model, **hints):
        # if model._meta.app_label == 'users_data':
        if model._meta.app_label == None:
            return 'default'
            # return 'users_db'
        elif model._meta.app_label == 'cis_db':
            return 'cis_db'
        return None

    def db_for_write(self, model, **hints):
        # if model._meta.app_label == 'user_data':
        if model._meta.app_label == None:
            return 'default'
            # return 'users_db'
        elif model._meta.app_label == 'cis_db':
            return 'cis_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # if obj1._meta.app_label == 'user_data' or \
        #    obj2._meta.app_label == 'user_data':
        if obj1._meta.app_label == None or obj2._meta.app_label == None:
            return True
        elif obj1._meta.app_label == 'cis_db' or obj2._meta.app_label == 'cis_db':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'users_db'
        database.
        """
        # if app_label == 'user_data':
        if app_label == None:
            return db == 'default'
            # return db == 'users_db'
        elif app_label == 'cis_db':
            return False

        return None
