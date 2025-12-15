import pandas as pd
from django.db import transaction
from stocks.models import (
    Company,
    Metric,
    MetricCategory,
    TimePeriod,
    FinancialValue,
)
from datetime import datetime, date

# =====================================================
# Helpers
# =====================================================

def normalize_code(name: str) -> str:
    return (
        name.upper()
        .replace("&", "AND")
        .replace("%", "PERCENT")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )



def is_valid_period(label) -> bool:
    """
    Accept only real datetime/date objects.
    """
    return isinstance(label, (datetime, date))


def parse_year(two_digit_year: str) -> int:
    y = int(two_digit_year)
    return 2000 + y if y < 50 else 1900 + y


def get_or_create_time_period(dt, report_type: str) -> TimePeriod:
    """
    dt: datetime.date or datetime.datetime
    report_type: 'annual' or 'quarterly'
    """

    year = dt.year
    month = dt.month

    if report_type == "annual":
        period_type = "annual"
        quarter = None

    elif report_type == "quarterly":
        period_type = "quarterly"

        quarter_map = {
            6: 1,   # Jun
            9: 2,   # Sep
            12: 3,  # Dec
            3: 4,   # Mar
        }

        if month not in quarter_map:
            raise ValueError(f"Invalid quarter month: {month}")

        quarter = quarter_map[month]

    else:
        raise ValueError("Invalid report_type")

    obj, _ = TimePeriod.objects.get_or_create(
        year=year-1 if quarter==4 or period_type=="annual" else year,
        quarter=quarter,
        period_type=period_type,
    )
    return obj


def get_or_create_metric(name: str, category_code: str) -> Metric:
    category = MetricCategory.objects.get(code=category_code)
    code = normalize_code(name)

    metric, _ = Metric.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "category": category,
            "is_derived": False,
        },
    )
    return metric


# =====================================================
# Section configuration (SINGLE SOURCE OF TRUTH)
# =====================================================

SECTION_MAP = {
    "PROFIT & LOSS": {"category": "PNL", "report_type": "annual"},
    "QUARTERS": {"category": "PNL", "report_type": "quarterly"},
    "BALANCE SHEET": {"category": "BS", "report_type": "annual"},
    "CASH FLOW:": {"category": "CF", "report_type": "annual"},
}

IGNORED_SECTIONS = {
    "META",
    "PRICE:",
    "DERIVED:",
    "RATIOS",
    "TRENDS",
}


# =====================================================
# Main Importer
# =====================================================

@transaction.atomic
def import_data_sheet(
    file_path: str,
    company_ticker: str,
):
    """
    Imports financial data ONLY from the 'Data Sheet'.

    Ignores:
    - Trailing / Best Case / Worst Case
    - Derived / Ratios / Trends / Price
    """

    # ---------------------------------------------
    # Company
    # ---------------------------------------------
    company, _ = Company.objects.get_or_create(
        ticker=company_ticker,
        defaults={
            "name": company_ticker,
            "exchange": "nse",
            "sector": "Unknown",
            "industry": "Unknown",
            "listing_date": "2000-01-01",
            "is_active": True,
        },
    )

    # ---------------------------------------------
    # Read Data Sheet (RAW)
    # ---------------------------------------------
    df = pd.read_excel(
        file_path,
        sheet_name="Data Sheet",
        header=None,
        engine="openpyxl",
        engine_kwargs={"data_only": True},
    )

    current_section = None
    current_periods = []

    for i in range(len(df)):
        first_cell = str(df.iloc[i, 0]).strip()

        if not first_cell or first_cell == "nan":
            continue

        cell_upper = first_cell.upper()

        # -----------------------------------------
        # Ignore blocks
        # -----------------------------------------
        if cell_upper in IGNORED_SECTIONS:
            current_section = None
            continue

        # -----------------------------------------
        # Detect section
        # -----------------------------------------
        if cell_upper in SECTION_MAP:
            current_section = SECTION_MAP[cell_upper]
            current_periods = []
            continue

        # -----------------------------------------
        # Detect Report Date row
        # -----------------------------------------
        if cell_upper == "REPORT DATE" and current_section:
            current_periods = df.iloc[i, 1:].tolist()
            print(current_periods)
            continue

        # -----------------------------------------
        # Metric rows
        # -----------------------------------------
        if current_section and current_periods:
            metric_name = first_cell

            # Skip totals / blanks
            if metric_name.upper() == "TOTAL":
                continue

            metric = get_or_create_metric(
                metric_name,
                current_section["category"],
            )

            for col_idx, period_label in enumerate(current_periods):
                if not is_valid_period(period_label):
                    continue

                value = df.iloc[i, col_idx + 1]

                if value is None or pd.isna(value):
                    continue

                time_period = get_or_create_time_period(
                    period_label,
                    current_section["report_type"],
                )

                FinancialValue.objects.update_or_create(
                    company=company,
                    metric=metric,
                    time_period=time_period,
                    defaults={"value": value},
                )