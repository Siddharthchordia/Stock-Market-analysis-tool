from celery import shared_task
from django.db import transaction
from stocks.models import Company
from stocks.utils.marketsnapshot import get_live_snapshot, get_weekly_updates
from stocks.utils.get_index_histories import append_index


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def update_company_snapshot(self, company_id):
    company = Company.objects.get(id=company_id)
    get_live_snapshot(company)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def update_index_snapshot(self, index_id):
    index = Index.objects.get(id=index_id)
    append_index(index)


@shared_task
def daily_market_snapshot():
    for company_id in Company.objects.filter(is_active=True).values_list("id", flat=True):
        update_company_snapshot.delay(company_id)

    for index_id in Index.objects.values_list("id", flat=True):
        update_index_snapshot.delay(index_id)



@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=300, retry_kwargs={"max_retries": 2})
def weekly_market_update(self):
    for company in Company.objects.filter(is_active=True):
        with transaction.atomic():
            get_weekly_updates(company)

