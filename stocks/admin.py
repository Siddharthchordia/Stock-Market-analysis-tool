# admin.py
from django.contrib import admin
from .models import (
    Company,
    TimePeriod,
    MetricCategory,
    Metric,
    FinancialValue,
)
from .forms import FinancialValueAdminForm


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "ticker", "exchange", "sector", "is_active"]
    search_fields = ["name", "ticker"]
    list_filter = ["exchange", "sector", "is_active"]


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
    list_display = ["name", "code", "category", "is_derived"]
    list_filter = ["category", "is_derived"]
    search_fields = ["name", "code"]
    autocomplete_fields = ["category"]



@admin.register(FinancialValue)
class FinancialValueAdmin(admin.ModelAdmin):
    form = FinancialValueAdminForm
    list_display = ["company", "metric", "time_period", "value"]
    list_filter = ["company",  "time_period"]
    autocomplete_fields = ["company", "metric", "time_period"]