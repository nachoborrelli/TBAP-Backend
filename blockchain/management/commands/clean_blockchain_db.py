from django.core.management.base import BaseCommand
from blockchain.models import UserToken, TokenGroup, Signature

class Command(BaseCommand):
    help = 'Execute to perform custom database operations. Located in /blockchain/management/commands/db_ops_script.py'
    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.NOTICE('Running your script...'))
        
        #Delete all signatures, user tokens and token groups
        Signature.objects.all().delete()
        UserToken.objects.all().delete()
        TokenGroup.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully ran your script!'))

