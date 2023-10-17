from django.core.management.base import BaseCommand
from blockchain.models import UserToken, TokenGroup, Signature

class Command(BaseCommand):
    help = 'Execute to perform custom database operations. Located in /blockchain/management/commands/db_ops_script.py'
    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.NOTICE('Running your script...'))
        
        Signature.objects.all().delete()
        UserToken.objects.all().update(is_claimed=False, tokenId=None)
        
        self.stdout.write(self.style.SUCCESS('Successfully ran your script!'))

