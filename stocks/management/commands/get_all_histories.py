from stocks.utils.get_historical_data import get_history
from django.core.management.base import BaseCommand
from stocks.models import Company

class Command(BaseCommand):
    help = "Generates transactions for testing"
    def handle(self,*args, **options):
        companies = Company.objects.all()
        for company in companies:
            try:
                get_history(company)
            except Exception as e:
                print(f"Failed for {company.ticker}: {e}")

