from django.core.management.base import BaseCommand
from blockchain.models import UserToken

class Command(BaseCommand):
    help = 'Execute to perform custom database operations. Located in /blockchain/management/commands/db_ops_script.py'
    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.NOTICE('Running your script...'))
        tokens = UserToken.objects.all()
        for token in tokens:
            token.is_claimed = False
            token.save()
        self.stdout.write(self.style.SUCCESS('Successfully ran your script!'))

