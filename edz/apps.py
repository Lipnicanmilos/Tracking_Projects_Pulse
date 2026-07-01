from django.apps import AppConfig

class EdzConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'edz'

    def ready(self):
        pass  # Nezavolajte start() tu, aby sa predišlo duplicitnému spúšťaniu