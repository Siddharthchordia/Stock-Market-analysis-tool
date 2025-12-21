from decimal import Decimal
from stocks.models import (
    Company,
    FinancialValue,
    Metric,
    CompanyFundamental,
    TimePeriod
)
from django.db.models import Sum,Count
from datetime import date


def safe_percentage(a, b):
    if a is None or b in (None, 0):
        return None
    return (Decimal(a) / Decimal(b)) * 100

def get_annual_value(company,metric_code):
    fv=FinancialValue.objects.filter(
        company=company,
        metric__code=metric_code,
        time_period__period_type='annual',
    ).select_related('time_period').order_by('-time_period__year').first()
    return fv.value if fv else None

def get_yearly_quarter_value_sum(company,year, metric_code):
    qs = FinancialValue.objects.filter(
        company=company,
        metric__code=metric_code,
        time_period__period_type="quarterly",
        time_period__year=year
    ).select_related('time_period').aggregate(
        total=Sum('value'),
        cnt=Count('value')
    )
    return qs['total'] if qs['cnt']==4 else None



def generate_company_fundamentals(company):

    q_year = date.today().year -1
    revenue = get_yearly_quarter_value_sum(company,q_year,"SALES")
    operating_profit = get_yearly_quarter_value_sum(company,q_year,"OPERATING_PROFIT")
    net_profit = get_yearly_quarter_value_sum(company,q_year,"NET_PROFIT")

    equity_share_capital = get_annual_value(company,"EQUITY_SHARE_CAPITAL")
    reserves = get_annual_value(company,"RESERVES")
    total_debt = get_annual_value(company,"BORROWINGS")

    total_equity = (
        (equity_share_capital or 0) +
        (reserves or 0)
        if equity_share_capital or reserves else None
    )
    capital_employed = (
        (total_equity or 0) +
        (total_debt or 0)
        if total_equity or total_debt else None
    )

    operating_margin = safe_percentage(operating_profit, revenue)
    net_margin = safe_percentage(net_profit, revenue)
    roe = safe_percentage(net_profit, total_equity)
    roce = safe_percentage(operating_profit, capital_employed)
    debt_to_equity = safe_percentage(total_debt, total_equity)/100

    CompanyFundamental.objects.update_or_create(
        company=company,
        defaults={
            "revenue": revenue,
            "operating_margin": operating_margin,
            "net_margin": net_margin,
            "roe": roe,
            "roce": roce,
            "debt_to_equity": debt_to_equity,
        }
    )











def generate_all_company_fundamentals():
    for company in Company.objects.filter(is_active=True):
        generate_company_fundamentals(company)
