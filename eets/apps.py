from django.apps import AppConfig

class EetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eets'

    def ready(self):
        pass  # Nezavolajte start() tu, aby sa predišlo duplicitnému spúšťaniu