from datetime import datetime

TIME_FORMATS = ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M%p")

def parse_time(value):
    start = value.split("-")[0].strip()
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(start, fmt).time()
        except ValueError:
            continue
    return datetime.min.time()  # unparseable values go first

def sort_key(row):
    time_reserved, _, day = row
    date = datetime.strptime(day.strip(), "%m/%d/%Y")  # handles 7/5/2026 and 07/05/2026
    return (date.date(), parse_time(time_reserved))