from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    index: int
    text: str
    start_char: int
    end_char: int


def chunk_text(text: str, chunk_size: int = 1400, overlap: int = 180) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size doit être positif")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap doit être compris entre 0 et chunk_size - 1")

    normalized = text.strip()
    if not normalized:
        return []

    chunks: list[Chunk] = []
    cursor = 0
    index = 0
    text_length = len(normalized)

    while cursor < text_length:
        hard_end = min(cursor + chunk_size, text_length)
        end = hard_end

        if hard_end < text_length:
            candidates = [
                normalized.rfind("\n\n", cursor + chunk_size // 2, hard_end),
                normalized.rfind(". ", cursor + chunk_size // 2, hard_end),
                normalized.rfind("\n", cursor + chunk_size // 2, hard_end),
                normalized.rfind(" ", cursor + chunk_size // 2, hard_end),
            ]
            best = max(candidates)
            if best > cursor:
                end = best + (2 if normalized[best : best + 2] in {"\n\n", ". "} else 1)

        chunk = normalized[cursor:end].strip()
        if chunk:
            chunks.append(Chunk(index=index, text=chunk, start_char=cursor, end_char=end))
            index += 1

        if end >= text_length:
            break
        next_cursor = max(end - overlap, cursor + 1)
        cursor = next_cursor

    return chunks
