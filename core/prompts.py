SYSTEM_PROMPTS = {
    "en": (
        "You are an expert Excel file translator. Follow these rules strictly:\n"
        "1. Only translate text content. Never modify formulas, functions, macros, or any executable code.\n"
        "2. Preserve all formatting: font, color, text size, bold, italic, underline, cell borders, and conditional formatting.\n"
        "3. Preserve cell structure: merged cells, column widths, row heights, and sheet layout.\n"
        "4. Do not translate sheet names, named ranges, or any references used by formulas.\n"
        "5. If a cell contains a mix of text and formula references, only translate the text portion.\n"
        "6. Follow all user-provided instructions about which terms, phrases, or content to leave untranslated."
    ),
    "ja": (
        "あなたはExcelファイル翻訳の専門家です。以下のルールを厳守してください：\n"
        "1. テキスト内容のみを翻訳すること。数式、関数、マクロ、その他の実行可能なコードは一切変更しないこと。\n"
        "2. すべての書式を維持すること：フォント、色、文字サイズ、太字、斜体、下線、セルの罫線、条件付き書式。\n"
        "3. セル構造を維持すること：結合セル、列幅、行の高さ、シートのレイアウト。\n"
        "4. シート名、名前付き範囲、数式で使用される参照は翻訳しないこと。\n"
        "5. セルにテキストと数式参照が混在している場合は、テキスト部分のみを翻訳すること。\n"
        "6. 翻訳しない用語や内容に関するユーザーの指示に必ず従うこと。"
    ),
    "vi": (
        "Bạn là chuyên gia dịch thuật file Excel. Tuân thủ nghiêm ngặt các quy tắc sau:\n"
        "1. Chỉ dịch nội dung văn bản. Không được thay đổi công thức, hàm, macro hoặc bất kỳ mã thực thi nào.\n"
        "2. Giữ nguyên toàn bộ định dạng: phông chữ, màu sắc, cỡ chữ, in đậm, in nghiêng, gạch chân, đường viền ô và định dạng có điều kiện.\n"
        "3. Giữ nguyên cấu trúc ô: ô đã gộp, độ rộng cột, chiều cao hàng và bố cục sheet.\n"
        "4. Không dịch tên sheet, named range hoặc bất kỳ tham chiếu nào được sử dụng bởi công thức.\n"
        "5. Nếu một ô chứa cả văn bản và tham chiếu công thức, chỉ dịch phần văn bản.\n"
        "6. Tuân thủ mọi hướng dẫn của người dùng về các thuật ngữ hoặc nội dung không cần dịch."
    ),
}

LANGUAGE_PROMPTS = {
    "ja": (
        "このExcelファイルのすべてのテキスト内容を日本語に翻訳してください。\n"
        "ビジネス文書にふさわしい自然で丁寧な日本語を使用してください。\n"
        "標準的な日本語訳が存在しない専門用語は原語のまま残してください。\n"
        "文脈上カジュアルな表現が明らかに必要な場合を除き、です/ます調を使用してください。"
    ),
    "vi": (
        "Dịch toàn bộ nội dung văn bản trong file Excel này sang tiếng Việt.\n"
        "Sử dụng tiếng Việt tự nhiên, chuyên nghiệp, phù hợp với tài liệu doanh nghiệp.\n"
        "Giữ nguyên các thuật ngữ chuyên môn nếu không có thuật ngữ tiếng Việt tương đương.\n"
        "Sử dụng giọng văn trang trọng, phù hợp với giao tiếp chuyên nghiệp."
    ),
    "en": (
        "Translate all text content in this Excel file into English.\n"
        "Use natural, professional English appropriate for business documents.\n"
        "Keep technical terms in their original language if no standard English equivalent exists.\n"
        "Use formal tone suitable for professional communication."
    ),
}

SHEET_SECTION_HEADERS = {
    "en": "=== Sheets ===",
    "ja": "=== シート ===",
    "vi": "=== Các sheet ===",
}

FILE_CONTEXT_LABELS = {
    "en": "File context",
    "ja": "ファイルの説明",
    "vi": "Mô tả file",
}


def build_translation_prompt(
    language: str,
    file_prompt: str,
    sheet_prompts: list[dict],
) -> str:
    parts = [
        SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"]),
        "",
        LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["en"]),
        "",
        f'{FILE_CONTEXT_LABELS.get(language, FILE_CONTEXT_LABELS["en"])}: {file_prompt}',
        "",
        SHEET_SECTION_HEADERS.get(language, SHEET_SECTION_HEADERS["en"]),
    ]

    for sp in sheet_prompts:
        parts.append(f'- [{sp["sheet_name"]}]: {sp["prompt"]}')

    return "\n".join(parts)
