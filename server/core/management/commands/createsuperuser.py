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
        allowed_ips = env.create_su_ips

        if not allowed_ips or current_ip not in allowed_ips:
            self.stdout.write(
                self.style.ERROR(
                    f"ACCESS DENIED: IP {current_ip} is not authorized to create a superuser."
                )
            )
            return None
        self.stdout.write(self.style.SUCCESS(f"IP {current_ip} authorized."))
        super().handle(*args, **options)
        return None
