import gspread
import os
from dotenv import load_dotenv
load_dotenv()

gc = gspread.service_account(os.environ.get('PATH'))
sheets_url = os.environ.get('URL')
sheet = gc.open_by_url(sheets_url).get_worksheet(0)


def append_sheet(data: list):
    sheet.append_row(data)
    return sheet.get()
