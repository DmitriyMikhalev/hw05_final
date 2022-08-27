import datetime as dt


def year(request):
    """Return a current year"""
    return {
        "year": dt.date.today().year
    }
