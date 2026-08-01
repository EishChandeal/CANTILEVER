import calendar
from datetime import datetime, date

def format_currency(amount: float, symbol: str = "₹") -> str:
    """
    Formats a numeric amount into Indian number format currency notation.
    Example: 123456.78 -> '₹ 1,23,456.78'
    """
    if amount is None:
        amount = 0.0

    is_negative = amount < 0
    amount = abs(amount)
    
    # Format decimal to 2 places
    amount_str = f"{amount:.2f}"
    integer_part, decimal_part = amount_str.split('.')
    
    # Indian grouping algorithm: last 3 digits, then groups of 2 digits
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        # split remaining into 2-digit groups from right to left
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last_three
    else:
        formatted_int = integer_part

    prefix = "-" if is_negative else ""
    return f"{prefix}{symbol} {formatted_int}.{decimal_part}"


def format_date(date_str: str) -> str:
    """
    Converts a date string (YYYY-MM-DD or ISO format) to human-readable format.
    Example: '2026-08-01' -> '01 Aug 2026'
    """
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return date_str


def get_month_year_options(n: int = 24) -> list[tuple[str, int, int]]:
    """
    Generates a list of (display_label, month_int, year_int) tuples
    for the last N months starting from the current month.
    Example: [('August 2026', 8, 2026), ('July 2026', 7, 2026), ...]
    """
    today = date.today()
    options = []
    current_year = today.year
    current_month = today.month

    for _ in range(n):
        month_name = calendar.month_name[current_month]
        label = f"{month_name} {current_year}"
        options.append((label, current_month, current_year))
        
        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1

    return options
