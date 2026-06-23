"""Finnish language verification MCP server powered by libvoikko.

Copyright (C) 2026  Markus Pasanen
SPDX-License-Identifier: GPL-3.0-or-later
"""

import re

from typing_extensions import TypedDict

import libvoikko
from mcp.server.fastmcp import FastMCP

voikko = libvoikko.Voikko("fi")

mcp = FastMCP("voikko-mcp", host="0.0.0.0", port=8000)


class SpellingResult(TypedDict):
    word: str
    correct: bool
    suggestions: list[str]


class GrammarError(TypedDict):
    start: int
    length: int
    snippet: str
    description: str
    suggestions: list[str]


class SpellingErrorEntry(TypedDict):
    word: str
    suggestions: list[str]


class VerifyTextResult(TypedDict):
    text: str
    is_correct: bool
    spelling_errors: list[SpellingErrorEntry]
    grammar_errors: list[GrammarError]


class HyphenateResult(TypedDict):
    word: str
    hyphenated: str


class TokenEntry(TypedDict):
    token_type: str
    token_text: str
    position: int


@mcp.tool(description=(
    "Check if a single Finnish word is spelled correctly. "
    "Use when you need to verify the spelling of an individual word "
    "(e.g. a name, a term, or a word the user typed). "
    "Pass only one word at a time; the word must be in its base dictionary form."
))
def check_spelling(word: str) -> SpellingResult:
    """Check if a single Finnish word is correct.

    Args:
        word: A single Finnish word to check.

    Returns:
        SpellingResult with word, correct, and suggestions.
    """
    try:
        is_correct = voikko.spell(word)
        suggestions = voikko.suggest(word) if not is_correct else []
        return SpellingResult(
            word=word,
            correct=is_correct,
            suggestions=suggestions,
        )
    except Exception as e:
        return SpellingResult(word=word, correct=False, suggestions=[], error=str(e))  # type: ignore[typeddict-unknown-key]


@mcp.tool(description=(
    "Get spelling suggestions for a misspelled Finnish word. "
    "Use when a word is known to be incorrect and you want alternatives. "
    "Returns a list of correctly spelled candidates. "
    "If the word is already correct the list will be empty."
))
def suggest_spelling(word: str) -> list[str]:
    """Get spelling suggestions for a misspelled word.

    Args:
        word: A potentially misspelled Finnish word.

    Returns:
        list of suggested correct spellings.
    """
    try:
        return voikko.suggest(word)
    except Exception:
        return []


@mcp.tool(description=(
    "Check grammar of full Finnish text and return error details. "
    "Use when inspecting a sentence, paragraph, or longer Finnish text for "
    "grammar issues (capitalization at sentence start, word-order errors, etc.). "
    "Each error includes the snippet, its character position, a human-readable "
    "description, and suggested corrections."
))
def check_grammar(text: str) -> list[GrammarError]:
    """Check grammar of full Finnish text.

    Args:
        text: Finnish text to check for grammar errors.

    Returns:
        list of GrammarError dicts.
    """
    try:
        errors: list[GrammarError] = []
        for err in voikko.grammarErrors(text, "fi"):
            start = err.startPos
            length = err.errorLen
            errors.append(GrammarError(
                start=start,
                length=length,
                snippet=text[start:start + length],
                description=err.shortDescription,
                suggestions=list(err.suggestions) if err.suggestions else [],
            ))
        return errors
    except Exception:
        return []


@mcp.tool(description=(
    "Full verification of Finnish text: runs both spell checking and grammar "
    "checking in a single call. Use when you have a complete text and want a "
    "quick yes/no answer about its correctness, plus a breakdown of any spelling "
    "and grammar errors found. More efficient than calling check_spelling and "
    "check_grammar separately."
))
def verify_text(text: str) -> VerifyTextResult:
    """Full verification (spelling + grammar) of Finnish text.

    Args:
        text: Finnish text to verify.

    Returns:
        VerifyTextResult with text, is_correct, and error lists.
    """
    try:
        grammar_errors: list[GrammarError] = []
        for err in voikko.grammarErrors(text, "fi"):
            start = err.startPos
            length = err.errorLen
            grammar_errors.append(GrammarError(
                start=start,
                length=length,
                snippet=text[start:start + length],
                description=err.shortDescription,
                suggestions=list(err.suggestions) if err.suggestions else [],
            ))

        words = re.findall(r"[A-Za-z\u00C0-\u024F\u0400-\u04FF\u00E4\u00F6\u00E5\u0152\u0153]+", text)
        spelling_errors: list[SpellingErrorEntry] = []
        for w in words:
            if not voikko.spell(w):
                spelling_errors.append(SpellingErrorEntry(
                    word=w,
                    suggestions=voikko.suggest(w),
                ))

        is_correct = len(spelling_errors) == 0 and len(grammar_errors) == 0
        return VerifyTextResult(
            text=text,
            is_correct=is_correct,
            spelling_errors=spelling_errors,
            grammar_errors=grammar_errors,
        )
    except Exception:
        return VerifyTextResult(
            text=text,
            is_correct=False,
            spelling_errors=[],
            grammar_errors=[],
        )


@mcp.tool(description=(
    "Morphological analysis of a Finnish word. "
    "Use when you need to understand the grammatical structure of a word — "
    "its base form, case (sijamuoto), number, possessive suffix, word class, "
    "and internal structure. Useful for language learning, linguistic analysis, "
    "or disambiguating inflected forms."
))
def analyze_word(word: str) -> list[dict]:
    """Morphological analysis of a Finnish word.

    Args:
        word: A Finnish word to analyze morphologically.

    Returns:
        list of dicts with analysis results (BASEFORM, CLASS, SIJAMUOTO, etc.).
    """
    try:
        return voikko.analyze(word)
    except Exception:
        return []


@mcp.tool(description=(
    "Hyphenate a Finnish word into syllables. "
    "Use when you need to show syllable boundaries for pronunciation, "
    "line-breaking, or educational purposes. Returns the word with hyphens "
    "inserted at syllable boundaries (e.g. 'ta-lo-is-sa')."
))
def hyphenate_word(word: str) -> HyphenateResult:
    """Hyphenate a Finnish word.

    Args:
        word: A Finnish word to hyphenate.

    Returns:
        HyphenateResult with word and hyphenated representation.
    """
    try:
        return HyphenateResult(
            word=word,
            hyphenated=voikko.hyphenate(word),
        )
    except Exception:
        return HyphenateResult(word=word, hyphenated=word)


@mcp.tool(description=(
    "Tokenize Finnish text into words, whitespace, and punctuation tokens. "
    "Use when you need to split Finnish text into its constituent parts while "
    "preserving punctuation and spacing. Each token reports its type "
    "(WORD, WHITESPACE, PUNCTUATION) and character position. "
    "More accurate than naive whitespace splitting because it understands "
    "Finnish tokenization rules."
))
def tokenize_text(text: str) -> list[TokenEntry]:
    """Tokenize Finnish text.

    Args:
        text: Finnish text to tokenize.

    Returns:
        list of TokenEntry dicts with token_type, token_text, and position.
    """
    try:
        tokens: list[TokenEntry] = []
        pos = 0
        for tok in voikko.tokens(text):
            tokens.append(TokenEntry(
                token_type=tok.tokenTypeName,
                token_text=tok.tokenText,
                position=pos,
            ))
            pos += len(tok.tokenText)
        return tokens
    except Exception:
        return []


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
