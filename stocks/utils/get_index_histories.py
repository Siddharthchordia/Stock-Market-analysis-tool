from stocks.models import Index, IndexHistory
import yfinance as yf
from decimal import Decimal
from django.utils.timezone import make_naive
def get_index_history(index: Index):

    symbol = index.metadata.get("yahoo_symbol")
    if not symbol:
        return
    stock = yf.Ticker(symbol)
    df = stock.history(period="max")
    records=[]
    for idx,row in df.iterrows():
        if row.isna().any():
            continue
        records.append(
            IndexHistory(
                index=index,
                date = make_naive(idx).date(),
                value=Decimal(row["Close"]),
            )
        )
    IndexHistory.objects.bulk_create(
        records,
        ignore_conflicts=True
    )



def append_index(index: Index):
    symbol = index.metadata.get("yahoo_symbol")
    if not symbol:
        return

    stock = yf.Ticker(symbol)
    df = stock.history(period="5d")
    if df.empty:
        return
    last_row = df.dropna().iloc[-1]
    ts = last_row.name

    IndexHistory.objects.update_or_create(
        index=index,
        date=make_naive(ts).date(),
        defaults={
            "value": Decimal(last_row["Close"]),
        }
    )
