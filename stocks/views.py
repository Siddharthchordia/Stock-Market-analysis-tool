from django.shortcuts import render, get_object_or_404
from .models import Company, FinancialValue, TimePeriod, Metric
from .forms import CompanyForm
from django.db.models import Q

# Create your views here.
def index(request):
    return render(request,'stocks/index.html')

def get_stock(request,ticker):
    company = get_object_or_404(Company, ticker__iexact=ticker)
    
    def get_table_data(period_type, category_code, limit=12):
        # Get periods for this company and period type
        periods = TimePeriod.objects.filter(
            values__company=company, 
            period_type=period_type
        ).distinct().order_by('-year', '-quarter')[:limit]
        
        # Sort chronologically for display
        periods = sorted(periods, key=lambda p: (p.year, p.quarter or 0))
        
        if not periods:
            return [], []

        # Get metrics for this category
        metrics = Metric.objects.filter(category__code=category_code).order_by('id')
        
        data = []
        for metric in metrics:
            row_values = []
            has_data = False
            for period in periods:
                val = FinancialValue.objects.filter(
                    company=company, metric=metric, time_period=period
                ).first()
                if val:
                    row_values.append(val.value)
                    has_data = True
                else:
                    row_values.append(None)
            
            if has_data:
                data.append({
                    'metric': metric.name,
                    'values': row_values
                })
                
        return periods, data

    quarterly_periods, quarterly_data = get_table_data('quarterly', 'PNL', limit=8)
    pnl_periods, pnl_data = get_table_data('annual', 'PNL')
    bs_periods, bs_data = get_table_data('annual', 'BS')
    cf_periods, cf_data = get_table_data('annual', 'CF')
    
    context = {
        'company': company,
        'quarterly_periods': quarterly_periods,
        'quarterly_data': quarterly_data,
        'pnl_periods': pnl_periods,
        'pnl_data': pnl_data,
        'bs_periods': bs_periods,
        'bs_data': bs_data,
        'cf_periods': cf_periods,
        'cf_data': cf_data,
    }
    return render(request, 'stocks/stock-base.html', context)


def stock_autocomplete(request):
    q = request.GET.get("q", "").strip()

    companies = Company.objects.none()
    if q:
        companies = (
            Company.objects
            .filter(Q(name__icontains=q) | Q(ticker__icontains=q))
            .order_by("ticker")[:10]
        )

    return render(
        request,
        "stocks/partials/autocomplete_results.html",
        {"companies": companies}
    )
