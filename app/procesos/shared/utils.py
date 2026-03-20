from datetime import date

def get_fecha_hoy() -> str:
    return date.today().strftime('%Y-%m-%d')
