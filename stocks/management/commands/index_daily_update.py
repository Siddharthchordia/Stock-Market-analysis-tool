from django.core.management.base import BaseCommand
from stocks.utils.get_index_histories import append_index
from stocks.models import Index
class Command(BaseCommand):
    help = "Updates indexes"
    def handle(self,*args, **options):
        for index in Index.objects.filter(exchange="NSE"):
            append_index(index)
