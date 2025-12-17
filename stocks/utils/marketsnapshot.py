import yfinance as yf
from stocks.models import Company, CompanyMarketSnapshot, CompanyHistory


def get_live_snapshot(company: Company):
    try:
        stock = yf.Ticker(f"{company.ticker}.NS")  
        info = stock.info
        CompanyMarketSnapshot.objects.update_or_create( 
            company=company,
            defaults={
            "price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "pb": info.get("priceToBook"),
            "high_52w": info.get("fiftyTwoWeekHigh"),
            "low_52w": info.get("fiftyTwoWeekLow"),
        })
    except Exception as e:
        print(f"Failed for {company.ticker}: {e}")
