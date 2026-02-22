"""
PWLB helper: attempt to fetch a current PWLB borrowing rate from a public source.

This tries a small number of fallbacks and returns None if not available.
"""
import requests

DEFAULT_SOURCES = [
    # UK DMO provides data; this is a best-effort CSV endpoint (may change).
    'https://www.dmo.gov.uk/data/periodic.csv',
]


def get_pwlb_rate_from_dmo():
    try:
        r = requests.get('https://www.dmo.gov.uk/data/periodic.csv', timeout=5)
        if r.status_code != 200:
            return None
        text = r.text
        # naive search for PWLB-like column header "PWLB"
        # This is a best-effort parser: look for a float in the text and return the first plausible rate
        for line in text.splitlines():
            parts = [p.strip() for p in line.split(',') if p.strip()]
            for p in parts:
                try:
                    val = float(p)
                    if 0.1 < val < 20:
                        return val
                except Exception:
                    continue
    except Exception:
        return None
    return None


def get_latest_pwlb_rate():
    # Try DMO
    rate = get_pwlb_rate_from_dmo()
    if rate:
        return rate
    # As fallback, try Bank of England series (not implemented fully) — return None
    return None
