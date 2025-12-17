from stocks.models import Company, CompanyHistory
import yfinance as yf

def get_history(company: Company):
    symbol = f"{company.ticker}.NS"
    stock = yf.Ticker(symbol)
    df = stock.history(start="1900-01-01")
    records=[]
    for idx,row in df.iterrows():
        records.append(
            CompanyHistory(
                company=company,
                date = idx.date(),
                closing_price=row["Close"],
                volume = row['Volume']
            )
        )
    CompanyHistory.objects.bulk_create(
        records,
        ignore_conflicts=True
    )