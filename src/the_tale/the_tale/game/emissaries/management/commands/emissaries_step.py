
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Do one emissary calculation step'

    def handle(self, *args, **options):
        emissaries_logic.sync_power()
