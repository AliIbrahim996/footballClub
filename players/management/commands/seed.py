from django.core.management.base import BaseCommand
from players.models import *

""" Clear all data and creates Skills """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'


class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('seeding done!.')


def clear_data(self):
    """Deletes all the table data"""
    self.stdout.write("Delete instances")
    PlayerSkills.objects.all().delete()
    Skills.objects.all().delete()
    Player.objects.all().delete()
    Category.objects.all().delete()
    Plans.objects.all().delete()


def run_seed(self, mode):
    """ Seed database based on mode
    """
    # Clear data from tables
    clear_data(self)
    if mode == MODE_CLEAR:
        return
