def build_genre_lines(genres: list[str]) -> str:
    """Validate genres and return bullet lines ready for prompt injection."""
    unknown = [g for g in genres if g not in GENRES]
    if unknown:
        raise ValueError(f"Unknown genre(s): {unknown}. Valid: {list(GENRES)}")
    return "\n".join(f"- {g}: {GENRES[g]}" for g in genres)


GENRES: dict[str, str] = {
    "realistic": "Natural and believable dialogue grounded in everyday situations and plausible human behavior.",
    "humorous": "Funny, witty, playful, or lighthearted dialogue intended to entertain.",
    "romantic": "Dialogue centered on affection, attraction, love, relationships, or emotional connection.",
    "dramatic": "Emotionally intense dialogue that emphasizes conflict, significance, or high personal stakes.",
    "mystery": "Dialogue that introduces intrigue, secrets, uncertainty, or unanswered questions.",
}
