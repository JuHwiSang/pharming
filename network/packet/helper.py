def chunk_lengths_reduce(chunk_lengths: list[int], to: int) -> list[int]:
    chunk_lengths = chunk_lengths.copy()
    while sum(chunk_lengths) != to:
        chunk_lengths[-2] -= sum(chunk_lengths) - to
        if chunk_lengths[-2] <= 0:
            del chunk_lengths[-2]
    return chunk_lengths