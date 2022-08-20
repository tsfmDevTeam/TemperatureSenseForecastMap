from django.apps import AppConfig
import os


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        from .clock import start

        release_flag = os.environ.get("wbgt_release", "0")
        if release_flag == "1":
            start()
