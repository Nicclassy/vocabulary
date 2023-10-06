import os
import threading
import concurrent.futures
from collections import Counter
from typing import Callable, Generator, Optional

from pypdf import PdfReader

from src.constants import (
    TXT, 
    FOLDER_DIR,
    FILENAME_SEPARATOR, 
)
from src.processing import (
    is_pdf, 
    is_txt, 
    get_word_counts_output_path,
    get_file_count,
    log_time,
    clear_screen
)
from src.parsing import count_words, parse_text

class DocumentProcessor:

    def __init__(self, folder_name: str, path: str = FOLDER_DIR):
        self._folder_name = folder_name
        self._path = path
        self._folder_path = os.path.join(path, folder_name)
        self._txt_folder_path = self._folder_path + FILENAME_SEPARATOR + TXT

        self._file_count = 0
        self._word_counts = Counter()
        self._filename_generator: Optional[Callable] = None

    @property
    def txt_folder_path(self) -> str:
        return self._txt_folder_path
    
    @property
    def folder_path(self) -> str:
        return self._folder_path

    def get_sorted_word_counts(self) -> list[tuple]:
        return sorted(
            self._word_counts.items(), 
            key=lambda pair: (-pair[1], -len(pair[0]), pair[0])
        )
    
    def generate_pdf_filenames(self) -> Generator[str, None, None]:
        yield from filter(is_pdf, os.listdir(self._folder_path))

    def generate_txt_filenames(self) -> Generator[str, None, None]:
        yield from filter(is_txt, os.listdir(self._txt_folder_path))

    def get_binary_file_contents(self, filename: str):
        return open(os.path.join(self._folder_path, filename), "rb")

    def get_formatted_pdf_text(self, filename: str) -> str:
        binary_file = self.get_binary_file_contents(filename)
        reader = PdfReader(binary_file)
        text = "".join(page.extract_text() for page in reader.pages)
        binary_file.close()
        return parse_text(text)

    def get_txt_file_text(self, filename: str) -> str:
        filepath = os.path.join(self._txt_folder_path, filename)
        return open(filepath).read()
    
    def write_word_counts_to_file(self):
        output_file_path = get_word_counts_output_path()
        with open(output_file_path, "w") as word_counts_file:
            word_counts_file.write("word,count\n")
            for word, count in self.get_sorted_word_counts():
                word_counts_file.write(f"{word},{count}\n")
        print("Finished writing to file.")

    def add_word_counts(self, words: Counter):
        self._word_counts.update(words)

    def preview_files(self):
        file_names = self._filename_generator()
        for file_number, filename in enumerate(file_names, 1):
            file_text = self.get_formatted_pdf_text(filename)
            print(file_text)
            n_columns = os.get_terminal_size()[0]
            print(n_columns * "—")
            print(self.parse_words(file_text))
            print(n_columns * "—")
            print(f"Printed contents of {file_number + 1} with title {filename!r}")
            if input("Press any key to continue.").startswith("q"):
                return
            clear_screen()

    def process_file(self, _: str):
        pass

    @log_time
    def count_words_threaded(self, write_to_file: bool = True):
        threads: list[threading.Thread] = []
        for pdf_file_name in self._filename_generator():
            thread = threading.Thread(target=self.process_file, args=(pdf_file_name,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

        if write_to_file:
            self.write_to_file()

    @log_time
    def count_words(self, write_to_file: bool = True):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            file_names = self._filename_generator()
            executor.map(self.process_file, file_names)

        if write_to_file:
            self.write_to_file()

class PDFProcessor(DocumentProcessor):

    def __init__(self, folder_name: str, path: str = FOLDER_DIR):
        super().__init__(folder_name, path)
        self._filename_generator = self.generate_pdf_filenames
        self._file_count = get_file_count(self._folder_path)

    def process_file(self, filename: str):
        self._file_count += 1
        print(f"Processing file {self._file_count}/{self._file_count}")
        pdf_text = self.get_formatted_pdf_text(filename)
        words = count_words(pdf_text)
        self.add_word_counts(words)