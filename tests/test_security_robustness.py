import pytest
from django.urls import reverse
from stocks.models import Company, FinancialValue, TimePeriod, Metric
from django.db.utils import IntegrityError
from django.test import Client

@pytest.mark.django_db
class TestSecurity:


    def test_sql_injection_autocomplete(self, client):
        url = reverse("stock-autocomplete")
        payload = "' OR 1=1 --"
        response = client.get(url, {"q": payload})
        
        assert response.status_code == 200
        
    def test_xss_stock_base(self, client, company, company_fundamental, company_market_snapshot):
        malicious_name = "<script>alert('XSS')</script>"
        company.name = malicious_name
        company.save()
        
        url = reverse("get-stock", args=[company.ticker])
        response = client.get(url)
        
        assert response.status_code == 200
        content = response.content.decode()
    
        assert "<script>alert('XSS')</script>" not in content
        assert "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;" in content or "&lt;script&gt;alert('XSS')&lt;/script&gt;" in content

    def test_input_validation_long_string(self, client):

        url = reverse("stock-autocomplete")
        long_query = "A" * 10000
        response = client.get(url, {"q": long_query})
        
        assert response.status_code == 200

@pytest.mark.django_db
class TestRobustness:


    def test_get_stock_valid(self, client, company, company_fundamental, company_market_snapshot):
        url = reverse("get-stock", args=[company.ticker])
        response = client.get(url)
        
        assert response.status_code == 200
        assert company.name in response.content.decode()

    def test_get_stock_case_insensitive(self, client, company, company_fundamental, company_market_snapshot):
        url = reverse("get-stock", args=[company.ticker.lower()])
        response = client.get(url)
        assert response.status_code == 200

    def test_get_stock_not_found(self, client):
        url = reverse("get-stock", args=["NON_EXISTENT"])
        response = client.get(url)
        
        assert response.status_code == 404

    def test_get_stock_missing_fundamentals(self, client, company):

        url = reverse("get-stock", args=[company.ticker])
        
        response = client.get(url)
        assert response.status_code == 404

    def test_financial_data_integrity(self, client, company, company_fundamental, company_market_snapshot, financial_value, metric):

        url = reverse("get-stock", args=[company.ticker])
        response = client.get(url)
        
        assert response.status_code == 200
        content = response.content.decode()
        
        # Check for metric name
        assert metric.name in content
        
        # Check for revenue (5000 -> 5,000)
        # Using string search might be brittle, but checking for 'Sales' (metric name) 
        # ensures the table for PNL is being rendered.
        # Also check for fundamentals revenue if possible
        if company_fundamental.revenue:
            # Simple check for 5,000
            assert "5,000" in content or "5000" in content

    def test_autocomplete_partial_match(self, client, company):

        url = reverse("stock-autocomplete")
        response = client.get(url, {"q": company.name[:4]}) # "Test"
        
        assert response.status_code == 200
        assert company.ticker in response.content.decode()

    def test_autocomplete_no_match(self, client):

        url = reverse("stock-autocomplete")
        response = client.get(url, {"q": "XYZ_NO_MATCH"})
        
        assert response.status_code == 200
        assert "<li>" not in response.content.decode() or "No results" in response.content.decode()

    def test_database_integrity_unique_constraints(self, company):

        with pytest.raises(IntegrityError):
            Company.objects.create(
                name="Duplicate Ticker Company",
                ticker=company.ticker, # Duplicate
                exchange="nse",
                sector="Energy"
            )
