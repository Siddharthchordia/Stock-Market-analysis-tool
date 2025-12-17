import pytest
from stocks.models import Company, Metric, MetricCategory, TimePeriod, FinancialValue, CompanyFundamental, CompanyMarketSnapshot

@pytest.fixture
def company(db):
    return Company.objects.create(
        name="Test Company",
        ticker="TEST",
        exchange="nse",
        sector="Technology"
    )

@pytest.fixture
def other_company(db):
    return Company.objects.create(
        name="Other Company",
        ticker="OTHER",
        exchange="bse",
        sector="Finance"
    )

@pytest.fixture
def metric_category(db):
    return MetricCategory.objects.create(
        code="PNL"
    )

@pytest.fixture
def metric(db, metric_category):
    return Metric.objects.create(
        code="SALES",
        name="Sales",
        category=metric_category
    )

@pytest.fixture
def time_period_annual(db):
    return TimePeriod.objects.create(
        year=2023,
        period_type="annual"
    )

@pytest.fixture
def time_period_quarterly(db):
    return TimePeriod.objects.create(
        year=2023,
        quarter=1,
        period_type="quarterly"
    )

@pytest.fixture
def financial_value(db, company, metric, time_period_annual):
    return FinancialValue.objects.create(
        company=company,
        metric=metric,
        time_period=time_period_annual,
        value=1000.00
    )

@pytest.fixture
def company_fundamental(db, company):
    return CompanyFundamental.objects.create(
        company=company,
        revenue=5000.00,
        net_margin=10.00,
        roe=15.00
    )

@pytest.fixture
def company_market_snapshot(db, company):
    return CompanyMarketSnapshot.objects.create(
        company=company,
        price=100.00,
        market_cap=10000.00,
        pe=20.00
    )
