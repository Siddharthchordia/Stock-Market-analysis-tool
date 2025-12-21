from stocks.utils.get_historical_data import get_history
from stocks.utils.get_index_histories import get_index_history
from django.core.management.base import BaseCommand
from stocks.models import Company, Index

class Command(BaseCommand):
    help = "Gets all historical data"
    def handle(self,*args, **options):
        companies = Company.objects.all()
        for company in companies:
            try:
                get_history(company)
            except Exception as e:
                print(f"Failed for {company.ticker}: {e}")
        indexes = Index.objects.all()
        for index in indexes:
            try:
                get_index_history(index)
            except Exception as e:
                print(f"Failed for {index.ticker}: {e}")
        self.stdout.write(self.style.SUCCESS("Histories fetched successfully"))
