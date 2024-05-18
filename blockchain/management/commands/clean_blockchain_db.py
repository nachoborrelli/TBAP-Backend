from django.core.management.base import BaseCommand
from blockchain.models import UserToken, Signature
from djan

class Command(BaseCommand):
    help = 'Execute to perform custom database operations. Located in /blockchain/management/commands/db_ops_script.py'
    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.NOTICE('Running your script...'))

        # Signature.objects.filter(id=5).update(nonce=100, was_used=True)
        # Signature.objects.filter(id=5).delete()
        Signature.objects.all().delete()

        # UserToken.objects.filter(id=9).delete()
        UserToken.objects.all().delete()
        # UserToken.objects.all().update(is_claimed=False, tokenId=None)
        
        self.stdout.write(self.style.SUCCESS('Successfully ran your script!'))

