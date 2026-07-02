import csv
import io
import urllib.request
from urllib.parse import quote

from app.core.exceptions import DataSyncError


def build_public_csv_url(sheet_id: str, gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def build_public_csv_url_for_sheet(sheet_id: str, sheet_name: str) -> str:
    encoded_sheet_name = quote(sheet_name)
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"


def fetch_csv_rows(url: str) -> list[dict[str, str]]:
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            raw = response.read().decode("utf-8-sig")
    except Exception as exc:
        raise DataSyncError(
            "Không đọc được Google Sheet. Hãy kiểm tra sheet đã bật quyền xem công khai hoặc dùng dữ liệu mẫu."
        ) from exc

    reader = csv.DictReader(io.StringIO(raw))
    return [{key.strip(): (value or "").strip() for key, value in row.items()} for row in reader]


def fetch_public_sheet_rows(sheet_id: str, gid: str) -> list[dict[str, str]]:
    url = build_public_csv_url(sheet_id, gid)
    return fetch_csv_rows(url)


def fetch_public_sheet_rows_by_name(sheet_id: str, sheet_name: str) -> list[dict[str, str]]:
    url = build_public_csv_url_for_sheet(sheet_id, sheet_name)
    return fetch_csv_rows(url)
