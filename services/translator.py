import json
import math
import re

from core.bedrock import BEDROCK_MAX_TOKENS, BEDROCK_MODEL_ID, get_bedrock_client
from core.prompts import LANGUAGE_PROMPTS, SYSTEM_PROMPTS

MAX_INPUT_TOKENS = 180_000
CHARS_PER_TOKEN_EN = 4
CHARS_PER_TOKEN_CJK = 1.5

MAX_CELLS_PER_CHUNK = 200
MAX_RETRIES = 3
MIN_CHUNK_SIZE = 5


class OutputTruncatedError(Exception):
    pass


def _estimate_tokens(text: str) -> int:
    cjk_chars = sum(1 for c in text if '一' <= c <= '鿿' or '　' <= c <= 'ヿ' or '가' <= c <= '힯')
    other_chars = len(text) - cjk_chars
    return math.ceil(cjk_chars / CHARS_PER_TOKEN_CJK + other_chars / CHARS_PER_TOKEN_EN)


def _chunk_cells(cells: list[dict], max_input_tokens: int) -> list[list[dict]]:
    """Split cells into chunks that fit within token budgets and cell count limit."""
    output_budget = int(BEDROCK_MAX_TOKENS * 0.9)
    chunks = []
    current_chunk = []
    current_input_tokens = 0
    current_output_tokens = 0

    for cell in cells:
        cell_json = json.dumps(cell, ensure_ascii=False)
        cell_tokens = _estimate_tokens(cell_json)
        at_cell_limit = len(current_chunk) >= MAX_CELLS_PER_CHUNK
        at_input_limit = current_chunk and current_input_tokens + cell_tokens > max_input_tokens
        at_output_limit = current_chunk and current_output_tokens + cell_tokens > output_budget
        if at_cell_limit or at_input_limit or at_output_limit:
            chunks.append(current_chunk)
            current_chunk = []
            current_input_tokens = 0
            current_output_tokens = 0
        current_chunk.append(cell)
        current_input_tokens += cell_tokens
        current_output_tokens += cell_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _extract_json(raw: str) -> str:
    """Extract JSON array from model response, handling code blocks and preamble."""
    cleaned = raw.strip()

    # Remove markdown code blocks
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    # Find the JSON array in case there's text before/after it
    match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if match:
        return match.group(0)

    return cleaned


def _build_sheet_user_message(
    cells: list[dict], sheet_name: str, file_prompt: str, sheet_prompt: str | None,
) -> str:
    lines = [f'Sheet: "{sheet_name}"']
    lines.append(f"File instructions: {file_prompt}")
    if sheet_prompt:
        lines.append(f"Sheet instructions: {sheet_prompt}")
    lines.append("")
    lines.append(
        "Translate the following cells. Return ONLY a valid JSON array with the same structure, "
        "where each \"text\" field is replaced with the translation. "
        "Do not add or remove entries. Do not truncate the output. "
        "You MUST follow the file/sheet instructions above about what to keep untranslated."
    )
    lines.append("")
    lines.append(json.dumps(cells, ensure_ascii=False))
    return "\n".join(lines)


def _call_bedrock(client, full_system: str, user_message: str) -> list[dict]:
    """Call Bedrock and parse JSON response with retries."""
    messages = [{"role": "user", "content": [{"text": user_message}]}]

    for attempt in range(MAX_RETRIES):
        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": full_system}],
            messages=messages,
            inferenceConfig={"maxTokens": BEDROCK_MAX_TOKENS, "temperature": 0.0},
        )

        raw = response["output"]["message"]["content"][0]["text"]
        stop_reason = response.get("stopReason", "")
        output_tokens = response.get("usage", {}).get("outputTokens", 0)

        if stop_reason == "max_tokens" or output_tokens >= BEDROCK_MAX_TOKENS:
            print(f"  Output truncated (tokens={output_tokens}, max={BEDROCK_MAX_TOKENS})")
            raise OutputTruncatedError(f"Output truncated at {output_tokens} tokens")

        try:
            return json.loads(_extract_json(raw))
        except json.JSONDecodeError as e:
            if attempt == MAX_RETRIES - 1:
                raise ValueError(f"Failed to parse JSON after {MAX_RETRIES} attempts: {e}\nRaw: {raw[:500]}")

            print(f"  JSON parse error (attempt {attempt + 1}/{MAX_RETRIES}, stop={stop_reason}): {e}")

            messages = [
                {"role": "user", "content": [{"text": user_message}]},
                {"role": "assistant", "content": [{"text": raw}]},
                {"role": "user", "content": [{"text": "Your response contained invalid JSON. Please return the complete, valid JSON array again."}]},
            ]


def translate_sheet(
    language: str,
    file_prompt: str,
    sheet_name: str,
    sheet_prompt: str | None,
    cells: list[dict],
) -> dict[str, str]:
    """Translate all text cells in a sheet. Returns {cell_ref: translated_text}."""
    if not cells:
        return {}

    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
    lang_prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS["en"])
    full_system = f"{system_prompt}\n\n{lang_prompt}\n\nFile context: {file_prompt}"

    system_tokens = _estimate_tokens(full_system)
    available_tokens = MAX_INPUT_TOKENS - system_tokens - 500

    chunks = _chunk_cells(cells, available_tokens)
    total_chunks = len(chunks)
    if total_chunks > 1:
        print(f'Sheet "{sheet_name}": {len(cells)} cells split into {total_chunks} chunks')

    client = get_bedrock_client()
    result = {}

    queue = list(enumerate(chunks))
    while queue:
        i, chunk = queue.pop(0)
        label = f"chunk {i + 1}" if total_chunks > 1 or len(chunks) > 1 else sheet_name
        print(f'  Translating {label} ({len(chunk)} cells)')

        try:
            user_message = _build_sheet_user_message(chunk, sheet_name, file_prompt, sheet_prompt)
            translated = _call_bedrock(client, full_system, user_message)
            for cell in translated:
                result[cell["ref"]] = cell["text"]
        except OutputTruncatedError:
            if len(chunk) <= MIN_CHUNK_SIZE:
                raise ValueError(f"Output truncated even with {len(chunk)} cells — cells may be too large")
            mid = len(chunk) // 2
            print(f"  Splitting chunk ({len(chunk)} cells) into 2 halves")
            queue.insert(0, (i, chunk[:mid]))
            queue.insert(1, (i, chunk[mid:]))

    return result
