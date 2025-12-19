# admin.py
from django.contrib import admin
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tempfile
from .models import (
    Company,
    TimePeriod,
    MetricCategory,
    Metric,
    FinancialValue,
    CompanyFundamental,
    CompanyMarketSnapshot,
    CompanyHistory,
    Index,IndexCategory,IndexHistory
)
from .forms import FinancialValueAdminForm, CompanyAdminForm
from stocks.utils.import_excel import import_data_sheet
from stocks.utils.marketsnapshot import get_live_snapshot
from stocks.utils.get_historical_data import get_history
from stocks.utils.get_index_histories import get_index_history


# admin.site.register(CompanyHistory)
@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    list_filter=['company']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    list_display = ["name", "ticker", "exchange", "sector", "is_active"]
    search_fields = ["name", "ticker"]
    list_filter = ["exchange", "sector", "is_active"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        get_live_snapshot(obj)
        get_history(obj)
        excel_file = form.cleaned_data.get("excel_file")


        if excel_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                for chunk in excel_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                import_data_sheet(
                    file_path=tmp_path,
                    company_ticker=obj.ticker
                )

            finally:
                os.remove(tmp_path)


# admin.site.register(IndexHistory)
@admin.register(IndexHistory)
class IndexHistoryAdmin(admin.ModelAdmin):
    list_display=["index",'date','value']
    ordering=['-date']
    


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin):
    list_display = ['name','ticker','exchange','category']
    list_filter = ['name','ticker','exchange','category']
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        get_index_history(obj)

admin.site.register(IndexCategory)

@admin.register(CompanyMarketSnapshot)
class CompanyMarketSnapshotAdmin(admin.ModelAdmin):
    list_display = ["company","price","market_cap","pe","pb"]



@admin.register(CompanyFundamental)
class CompanyFundamentalAdmin(admin.ModelAdmin):
    list_display = ["company",'revenue','operating_margin','roce','roe','debt_to_equity']




@admin.register(TimePeriod)
class TimePeriodAdmin(admin.ModelAdmin):
    list_display = ["year", "quarter", "period_type"]
    list_filter = ["period_type", "year"]
    search_fields = ["year", "quarter"]


@admin.register(MetricCategory)
class MetricCategoryAdmin(admin.ModelAdmin):
    list_display = ["code"]
    search_fields = ["code"]


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "category"]
    list_filter = ["category"]
    search_fields = ["name", "code"]
    autocomplete_fields = ["category"]



@admin.register(FinancialValue)
class FinancialValueAdmin(admin.ModelAdmin):
    form = FinancialValueAdminForm
    list_display = ["company", "metric", "time_period", "value"]
    list_filter = ["company",  "time_period"]
    autocomplete_fields = ["company", "metric", "time_period"]

