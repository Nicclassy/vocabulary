import os
from string import punctuation, digits

from colorama import Back
from nltk.corpus import words

FOLDER_DIR = os.path.dirname(os.path.dirname(__file__))
os.chdir(FOLDER_DIR)

SAVED_FILE_PREFIX = "saved"
SAVED_FILES_DIRECTORY = os.path.join(FOLDER_DIR, SAVED_FILE_PREFIX)
POINT_FILES_DIRECTORY = os.path.join(FOLDER_DIR, "points")

DOUBLEWORD_SEPARATOR = ' '
FILENAME_SEPARATOR = '-'

DEFAULT_WORD_COUNTS_FILENAME = "word_counts"
WORD_COUNTS_FILENAME = "word_counts.txt"
JSTOR_FILE = "bad_jstor.txt"

TXT = "txt"
FILE_EXTENSION = ".txt"
PDF_FILE_EXTENSION = ".pdf"
GPT_SUFFIX = GPT_PREFIX = "gpt"

REMOVABLE_CHARACTERS = punctuation + digits
WORDS_CORPUS = frozenset(map(str.lower, words.words()))

BLANK = ''
SPACE = ' '
COMMA = ','
HYPHEN = '-'

POINT_PREFIX = "- "
POINT_SUFFIX = ".\n"
DELETE_KEY = '\x7f'
ESCAPE_KEY = '\x1b'
RIGHT_ARROW_KEY = '\x1b[C'
LEFT_ARROW_KEY = '\x1b[D'
ENTER_KEY = '\n'

COMMAND_KEY = '/'
COMMAND_PROMPT = "> "
GPT_SEPARATOR = '-' * 100 + '\n'

FORWARD_KEYS = {ENTER_KEY, RIGHT_ARROW_KEY}
BACKWARD_KEYS = {LEFT_ARROW_KEY}

COMMAND_MAPPING = {
    "test": (0,),
    "bad": (0,),
    "jump": (1, str.isdigit),
    "preview": (1, str.isdigit),
}

REMOVE_NUMBERS = True
COMBINE_SPLITWORDS = True
SEPARATE_DOUBLEWORDS = True
SPLIT_BY_FREQUENCY = True

GREEN = Back.GREEN
RED = Back.RED
BLUE = Back.BLUE
RESET = Back.RESET

COMPLETE_COLOUR = GREEN
INCOMPLETE_COLOUR = RED
SIDE_QUEST_COLOUR = BLUE

MIN_DOUBLEWORD_LENGTH = 5
PROGRESS_BAR_LENGTH = 50
MAX_GPT_CHARACTERS = 4096
INVALID_WORD_RATIO = 0.5