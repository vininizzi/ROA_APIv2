from datetime import datetime, timezone
import re


def parse_pdf_date_from_spec(pdf_date: str | None) -> datetime | None:
    """
    Converte datas do formato PDF (ex: D:20241022015619Z)
    para datetime Python.
    """
    if not pdf_date or not isinstance(pdf_date, str):
        return None

    # Remove prefixo "D:" se existir
    if pdf_date.startswith("D:"):
        pdf_date = pdf_date[2:]

    # Regex PDF Date
    match = re.match(
        r"(\d{4})"        # YYYY
        r"(\d{2})"        # MM
        r"(\d{2})"        # DD
        r"(\d{2})?"       # HH
        r"(\d{2})?"       # mm
        r"(\d{2})?"       # SS
        r"(Z|[+-]\d{2}'?\d{2}')?$",  # timezone
        pdf_date
    )

    if not match:
        return None

    year, month, day, hour, minute, second, tz = match.groups()

    dt = datetime(
        int(year),
        int(month),
        int(day),
        int(hour or 0),
        int(minute or 0),
        int(second or 0),
    )

    # Timezone
    if tz == "Z":
        dt = dt.replace(tzinfo=timezone.utc)
    elif tz and (tz.startswith("+") or tz.startswith("-")):
        sign = 1 if tz[0] == "+" else -1
        hours = int(tz[1:3])
        minutes = int(tz[-2:])
        offset = timezone(sign * (hours * 3600 + minutes * 60))
        dt = dt.replace(tzinfo=offset)

    return dt
