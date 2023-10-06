from collections import Counter
from typing import Any, Callable, Optional

from src.constants import (
    BLANK,
    SPACE, 
    HYPHEN,
    DOUBLEWORD_SEPARATOR,
    MIN_DOUBLEWORD_LENGTH, 
    REMOVE_NUMBERS, 
    REMOVABLE_CHARACTERS,
    INVALID_WORD_RATIO,
    COMBINE_SPLITWORDS,
    SEPARATE_DOUBLEWORDS,
    SPLIT_BY_FREQUENCY,
)
from src.patterns import (
    WHITESPACE_PATTERN,
    WORD_SEARCH_PATTERN,
    CAPWORDS_PATTERN,
    CITATION_NUMBER_PATTERN,
    DOUBLE_SPACE_PATTERN,
    NEWLINE_PATTERN,
    NUMBER_PATTERN,
    WHITESPACE_HYPHEN_PATTERN,
    WHITESPACE_TXT_PATTERN,
    HYPHEN_PATTERN,
    LINE_SPLIT_PATTERN,
    BRACKETED_NUMBERS_PATTERN,
    DOT_IN_BRACKETS_PATTERN,
    CF_PATTERN,
    AUTHOR_CITATION_PATTERN,
    JSTOR_TERMS_PATTERN
)
from src.processing import is_proper_noun, is_english_word, get_word_frequency

def substitution_pattern(arg_pos: int, function: Callable, 
                         *args: tuple, predicate: Optional[bool] = None) -> Callable:
    args: list = list(args)
    def wrapper(arg: Any) -> str:
        fargs = args[:]
        if predicate is not None and not predicate:
            return arg
        fargs.insert(arg_pos, arg)
        return function(*fargs)
    return wrapper

DOCUMENT_SUBTITUTIONS = (
    substitution_pattern(0, str.replace, "-\n", BLANK),
    substitution_pattern(1, WHITESPACE_HYPHEN_PATTERN.sub, SPACE),
    substitution_pattern(1, HYPHEN_PATTERN.sub, BLANK),
    substitution_pattern(1, BRACKETED_NUMBERS_PATTERN.sub, BLANK),
    substitution_pattern(1, JSTOR_TERMS_PATTERN.sub, BLANK),
    substitution_pattern(1, NUMBER_PATTERN.sub, BLANK, predicate=REMOVE_NUMBERS),
    substitution_pattern(1, CITATION_NUMBER_PATTERN.sub, BLANK, predicate=(not REMOVE_NUMBERS)),
    substitution_pattern(1, DOT_IN_BRACKETS_PATTERN.sub, BLANK),
    substitution_pattern(1, CF_PATTERN.sub, BLANK),
    substitution_pattern(1, AUTHOR_CITATION_PATTERN.sub, BLANK),
)

def is_whitespace(line: str) -> bool:
    return bool(WHITESPACE_PATTERN.match(line))

def is_valid_word_ratio(line: str) -> bool:
    words = parse_words(line)
    total_tokens = len(line.split())
    valid_tokens = len(words)
    return valid_tokens / total_tokens >= INVALID_WORD_RATIO

def is_valid_line(line: str) -> bool:
    return is_valid_word_ratio(line)

def count_words(text: str) -> Counter:
    word_counts = Counter()
    tokens = parse_text(text).split()
    for token in tokens:
        token = parse_without_punctuation(token).lower()
        if CAPWORDS_PATTERN.search(token):
            split_words = CAPWORDS_PATTERN.sub(SPACE, token).lower().split()
            for word in filter(is_english_word, split_words):
                word_counts[word] += 1
        elif is_english_word(token):
            word_counts[token.lower()] += 1
    return word_counts

def parse_word(token: str) -> str:
    if (word_match := WORD_SEARCH_PATTERN.search(token)) is None:
        return BLANK
    
    word = word_match.group(0)
    return word

def parse_without_punctuation(token: str) -> str:
    return token.strip(REMOVABLE_CHARACTERS)

def parse_doubleword(token: str) -> Optional[str]:
    if (word_len := len(token)) < MIN_DOUBLEWORD_LENGTH:
        return None
    
    word_pairs = []
    first_word_start = 0
    next_word_start = MIN_DOUBLEWORD_LENGTH - 2
    next_word_end = word_len

    for first_word_end in range(next_word_start, next_word_end):
        first_word = token[first_word_start:first_word_end]
        next_word = token[next_word_start:next_word_end]

        if is_english_word(first_word) and is_english_word(next_word):
            first_word_frequency = get_word_frequency(first_word)
            next_word_frequency = get_word_frequency(next_word)
            average_frequency = (first_word_frequency + next_word_frequency) // 2
            split_doubleword = first_word + DOUBLEWORD_SEPARATOR + next_word
            word_pairs.append((split_doubleword, average_frequency))

        next_word_start += 1
        next_word_end += 1
    
    if not word_pairs:
        return None
    
    if SPLIT_BY_FREQUENCY:
        return max(word_pairs, key=lambda i: i[0])[0]
    else:
        return word_pairs[0][0]

def parse_combinable_words(token: str, other_token: str) -> Optional[str]:
    if not token or not other_token:
        return None
    
    if parse_word(token) != token:
        return None
    
    if is_english_word(token) or is_english_word(other_token):
        return None
    if not is_english_word(combined_word := token + other_token):
        return None
    
    return combined_word

def parse_hyphenated_word(token: str) -> Optional[str]:
    if token.count(HYPHEN) != 1:
        return None
    
    word_part, other_word_part = token.split(HYPHEN)
    parts_are_words = is_english_word(word_part) and is_english_word(other_word_part)
    word = word_part + other_word_part

    if SPLIT_BY_FREQUENCY:
        word_frequency = get_word_frequency(word)
        parts_frequency = (
            (get_word_frequency(word_part) 
            + get_word_frequency(other_word_part)) // 2
        ) 
        if word_frequency >= parts_frequency or not parts_are_words:
            return word
        else:
            return None

    if parts_are_words:
        return None
    
    if not is_english_word(word := word_part + other_word_part):
        return None
    return word

def parse_words(text: str) -> list[str]:
    words = []
    tokens = text.split()
    for token in tokens:
        if (word := parse_word(token)) and is_english_word(word):
            words.append(word)
    return words

def parse_line(line: str, remove_newlines: bool = False) -> str:
    remove_whitespace = WHITESPACE_TXT_PATTERN.sub(BLANK, line)
    remove_double_spaces = DOUBLE_SPACE_PATTERN.sub(BLANK, remove_whitespace)
    if remove_newlines:
        return NEWLINE_PATTERN.sub(SPACE, remove_double_spaces).strip()
    else:
        return remove_double_spaces.strip()
    
def parse_text(text: str) -> str:
    for substitution in DOCUMENT_SUBTITUTIONS:
        text = substitution(text)
    return text

def parse_fulltext(text: str) -> list[str]:
    parsed_lines = []
    lines = LINE_SPLIT_PATTERN.split(parse_text(text))
    for line in lines:
        if is_whitespace(line) or not is_valid_line(line):
            continue

        parsed_line = []
        previous_token = BLANK
        for token in line.split(SPACE):
            remove_previous_token = False
            word = parse_word(token)
            parsed_word = BLANK
            clean_token = parse_without_punctuation(token)
            is_splittable = word and not is_proper_noun(word) and not is_english_word(word)

            if (
                COMBINE_SPLITWORDS and 
                (combined_word := parse_hyphenated_word(clean_token)) is not None
            ):
                parsed_word = token.replace(clean_token, combined_word, 1)
                parsed_word = '@' + parsed_word + '@'
            elif (
                COMBINE_SPLITWORDS and 
                (combined_word := parse_combinable_words(previous_token, word)) is not None
            ):
                parsed_word = token.replace(word, combined_word, 1)
                parsed_word = '|' + combined_word + '|'
                remove_previous_token = True
            elif (SEPARATE_DOUBLEWORDS and is_splittable and 
                (split_doubleword := parse_doubleword(token)) is not None
            ):
                parsed_word = token.replace(word, split_doubleword, 1)
                parsed_word = ":" + parsed_word + ':'
                remove_previous_token = True

            if remove_previous_token:
                parsed_line.pop()
                remove_previous_token = False
            if parsed_word:
                parsed_line.append(parsed_word)
            else:
                parsed_line.append(token)

            previous_token = token
        parsed_lines.append(SPACE.join(parsed_line))
    return parsed_lines

print("actu-alizes")