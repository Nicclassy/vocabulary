import os
import sys
import time
from typing import Any, Callable, Generator

from src.constants import (
    COMMA,
    FOLDER_DIR,
    PDF_FILE_EXTENSION,
    SAVED_FILE_PREFIX,
    WORD_COUNTS_FILENAME,
    WORDS_CORPUS,
    POINT_FILES_DIRECTORY,
    DEFAULT_WORD_COUNTS_FILENAME,
    SAVED_FILES_DIRECTORY,
    FILE_EXTENSION,
)
from src.patterns import WORD_PATTERN

def is_word(token: str) -> bool:
    return WORD_PATTERN.fullmatch(token) and len(token) > 1

def is_proper_noun(token: str) -> bool:
    return not token.islower()

def is_english(word: str) -> bool:
    return word.lower() in WORDS_CORPUS or word.lower() in WORD_COUNTS

def is_english_word(word: str) -> bool:
    return is_word(word) and is_english(word)

def is_pdf(filename: str):
    return filename.endswith(PDF_FILE_EXTENSION)

def is_txt(filename: str):
    return filename.endswith(FILE_EXTENSION)

def has_points(filename: str) -> bool:
    saved_points_filename = get_saved_points_filename(filename)
    return os.path.exists(
        os.path.join(POINT_FILES_DIRECTORY, saved_points_filename)
    )

def get_file_count(directory: str) -> int:
    return len(os.listdir(directory))

def get_txt_filename(pdf_file_name: str) -> str:
    return get_base_filename(pdf_file_name) + FILE_EXTENSION

def get_word_frequency(word: str) -> int:
    return WORD_COUNTS.get(word, 0)

def get_files_in_directory(directory: str) -> Generator[str, None, None]:
    yield from filter(lambda file: not file.startswith("."), os.listdir(directory))

def get_base_filename(filename: str) -> str:
    if "." not in filename:
        return filename
    return filename.rsplit(".", maxsplit=1)[0]

def get_saved_points_filename(filename: str) -> str:
    base_filename = get_base_filename(filename)
    return f"{SAVED_FILE_PREFIX}-{base_filename}{FILE_EXTENSION}"

def get_word_counts_output_path() -> str:
    default_filename = DEFAULT_WORD_COUNTS_FILENAME + FILE_EXTENSION
    default_filename_path = os.path.join(SAVED_FILES_DIRECTORY, default_filename)
    if not os.path.isfile(default_filename_path):
        return default_filename_path
    
    count = 1
    filename = DEFAULT_WORD_COUNTS_FILENAME + str(count) + FILE_EXTENSION
    filename_path = os.path.join(SAVED_FILES_DIRECTORY, filename)
    while os.path.isfile(filename_path):
        count += 1
        filename = DEFAULT_WORD_COUNTS_FILENAME + str(count) + FILE_EXTENSION
        filename_path = os.path.join(SAVED_FILES_DIRECTORY, filename)

    return filename_path

def get_points_output_filepath(filename: str) -> str:
    if not os.path.exists(POINT_FILES_DIRECTORY):
        os.mkdir(POINT_FILES_DIRECTORY)
    
    filepath = os.path.join(POINT_FILES_DIRECTORY, filename)
    basepath = get_saved_points_filename(filepath)

    if os.path.exists(filepath):
        file_no = 1
        while os.path.exists(filepath := basepath + str(file_no) + FILE_EXTENSION):
            file_no += 1

    return filepath

def get_word_counts_from_file(relpath: str) -> dict[str, int]:
    filepath = os.path.join(FOLDER_DIR, relpath)
    word_counts = {}
    with open(filepath) as file:
        for line in file.readlines()[1:]:
            word, count = line.rstrip().split(COMMA)
            word_counts[word] = int(count)
    return word_counts

def log_time(function: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any):
        start_time = time.perf_counter()
        function(*args, **kwargs)
        end_time = round(time.perf_counter() - start_time, 2)

        formatted_time = ""
        hours, remainder = divmod(end_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        quantities = (int(hours), int(minutes), int(seconds))
        for quantity, measurement in zip(quantities, ("hours", "minutes", "seconds")):
            if quantity == 1:
                measurement = measurement[:-1]
            if quantity != 0:
                formatted_time += f"{quantity} {measurement}, "
        response = formatted_time[:-2] or "less than 1 second"
        print(f"Finished execution of {function.__qualname__!r} in {response}.")
    return wrapper

def clear_screen():
    sys.stdout.write("\033[2J")
    sys.stdout.flush()

WORD_COUNTS = get_word_counts_from_file(WORD_COUNTS_FILENAME)