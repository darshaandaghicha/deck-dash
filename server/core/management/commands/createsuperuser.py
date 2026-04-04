from socket import gethostbyname, gethostname
from django.contrib.auth.management.commands import createsuperuser

from core.utils.env import env


class Command(createsuperuser.Command):
    """
    Enhanced createsuperuser with IP gating.
    Only runs if current machine IP == SU_IP from .env
    """

    def handle(self, *args, **options):
        current_ip = gethostbyname(gethostname())

        try:
            su_ip = env.create_su_ips()
            if current_ip != su_ip:
                return print("YOU ARE NOT AUTHORIZED to CREATE SUPER USER.")
        except ValueError as err:
            print(f"Env Error: ${err}")
        finally:
            super().handle(*args, **options)
        return None
