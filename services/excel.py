import io

from openpyxl import load_workbook


def extract_text_cells(file_bytes: bytes) -> dict[str, list[dict]]:
    """Extract text cells from each sheet. Returns {sheet_name: [{ref, text}, ...]}."""
    wb = load_workbook(io.BytesIO(file_bytes), data_only=False)
    result = {}

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        cells = []
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                if isinstance(cell.value, str) and not cell.value.startswith("="):
                    cells.append({"ref": cell.coordinate, "text": cell.value})
        result[sheet_name] = cells

    wb.close()
    return result


def write_translations(file_bytes: bytes, translations: dict[str, dict[str, str]]) -> bytes:
    """Write translated text back to the workbook.

    translations: {sheet_name: {cell_ref: translated_text}}
    """
    wb = load_workbook(io.BytesIO(file_bytes))

    for sheet_name, cell_map in translations.items():
        if sheet_name not in wb.sheetnames:
            continue
        ws = wb[sheet_name]
        for ref, text in cell_map.items():
            ws[ref] = text

    output = io.BytesIO()
    wb.save(output)
    wb.close()
    return output.getvalue()
