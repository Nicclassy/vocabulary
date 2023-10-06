import re

WORD_SEARCH_PATTERN = re.compile(r"[a-zA-Z]+")
CAPWORDS_PATTERN = re.compile(r"(?<=[A-Za-z][a-z])(?=[A-Z][a-z])")
WORD_PATTERN = re.compile(r"^[a-zA-Z]+$")

WHITESPACE_PATTERN = re.compile(r"^\s+$")
WHITESPACE_HYPHEN_PATTERN = re.compile(r"- ?\n ?")
WHITESPACE_TXT_PATTERN = re.compile(r"(\n(?= ))|(\n(?<= ))")
DOUBLE_SPACE_PATTERN = re.compile(r" (?= )")
NEWLINE_PATTERN = re.compile(r"[\t ]\n(?![A-Z])")

HYPHEN_PATTERN = re.compile(r"(['\"](?=\.))|((?<=\.)['\"])")
NUMBER_PATTERN = re.compile(r"\d")
CITATION_NUMBER_PATTERN = re.compile(r"((?<=[A-Za-z\'\"])\d+)|(\d+(?=[A-Za-z\'\"]))|((?<=\.)\d)")
LINE_SPLIT_PATTERN = re.compile(r"(?<=[a-z])(?<!pp)(?<![A-Z\.])\.(?=[ \n])")

BRACKETED_NUMBERS_PATTERN = re.compile(r"\(.*\d.*\)")
DOT_IN_BRACKETS_PATTERN = re.compile(r"\(\.?\)")
CF_PATTERN = re.compile(r"\(cf.*?\)")
AUTHOR_CITATION_PATTERN = re.compile(r"\([A-Z].+\)")

JSTOR_TERMS_PATTERN = re.compile(r"This.+?https://about.jstor.org/terms", flags=re.DOTALL)