import logging
import re

log = logging.getLogger(__name__)

# U+0022 straight, U+201C left curly, U+201D right curly.
# chr(0x22) avoids source-file encoding converting straight quotes to curly.
# Optional leading/trailing * handles markdown-italic wrapping (*”...”*).
_QUOTES = chr(0x22) + chr(0x201C) + chr(0x201D)
_QO = r'\*?[' + _QUOTES + ']'   # opening quote, optional leading *
_QC = '[' + _QUOTES + r']\*?'   # closing quote, optional trailing *

# Primary: line starts with “N.”, optional blank lines, then opening quote.
_NUMBERED = re.compile(rf'(?m)^\s*\d+\.\s*(?:\n\s*)?{_QO}([\s\S]+?){_QC}')

# Fallback A: opening quote at the start of a line (no number required).
_LINE_QUOTE = re.compile(rf'(?m)^\s*{_QO}([\s\S]+?){_QC}')

# Fallback B: any quoted block anywhere in the text.
_ANY_QUOTE = re.compile(rf'{_QO}([\s\S]+?){_QC}')

# Completions are multi-sentence; filter out short incidental quoted strings.
_MIN_LEN = 30


def _extract(pattern: re.Pattern, raw: str) -> list[str]:
    return [m.group(1).strip() for m in pattern.finditer(raw) if len(m.group(1).strip()) >= _MIN_LEN]


_NUMBERED_PLAIN = re.compile(r'(?m)^\s*\d+\.\s+(.+)')


def parse_story_ideas(raw: str, expected: int) -> list[str]:
    """Extract plain numbered lines from story-ideas LLM output."""
    ideas = [m.group(1).strip() for m in _NUMBERED_PLAIN.finditer(raw) if m.group(1).strip()]
    if len(ideas) >= expected:
        return ideas[:expected]
    log.debug("parse_story_ideas failed — expected=%d got=%d\nraw:\n%s", expected, len(ideas), raw)
    raise ValueError(f"Expected {expected} story ideas, got {len(ideas)}.")


def parse_completions(raw: str, expected: int) -> list[str]:
    """Extract quoted dialogue blocks from numbered LLM output.

    Tries three strategies in order:
      1. Numbered label + quote  (e.g. "1.\\n\\"text\\"")
      2. Quote at start of line  (no number required)
      3. Any quoted block of sufficient length
    """
    best = 0
    for pattern in (_NUMBERED, _LINE_QUOTE, _ANY_QUOTE):
        completions = _extract(pattern, raw)
        if len(completions) == expected:
            return completions
        if len(completions) > best:
            best = len(completions)

    log.debug("parse_completions failed — expected=%d best=%d\nraw:\n%s", expected, best, raw)
    raise ValueError(f"Expected {expected} completions, got {best}.")
