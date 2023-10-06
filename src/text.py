import os
import sys
import threading

import time

from getkey import getkey

from src.constants import (
    FILENAME_SEPARATOR,
    GPT_PREFIX,
    GPT_SUFFIX,
    POINT_PREFIX,
    FOLDER_DIR,
    POINT_SUFFIX,
    PROGRESS_BAR_LENGTH,
    COMMAND_PROMPT,
    DELETE_KEY,
    ESCAPE_KEY,
    COMMAND_KEY,
    FORWARD_KEYS,
    BACKWARD_KEYS,
    MAX_GPT_CHARACTERS,
    GPT_SEPARATOR,
)
from src.patterns import LINE_SPLIT_PATTERN
from src.processing import (
    get_files_in_directory,
    get_saved_points_filename,
    has_points,
    is_txt,
    get_txt_filename,
    get_file_count,
    get_points_output_filepath,
)
from src.parsing import parse_fulltext, parse_text
from src.document import DocumentProcessor
from src.points import PointCLI, PointList

class TextProcessor(DocumentProcessor):

    def __init__(self, folder_name: str, path: str = FOLDER_DIR):
        super().__init__(folder_name, path)
        self._filename_generator = self.generate_txt_filenames
        if not os.path.isdir(self._txt_folder_path):
            os.mkdir(self._txt_folder_path)
        self._total_file_count = get_file_count(self._txt_folder_path)

    def txt_files(self) -> str:
        return list(self._filename_generator())

    def has_generated_txt_files(self) -> bool:
        return len(os.listdir(self._txt_folder_path)) > 0
    
    def process_file(self, filename: str):
        self._file_count += 1
        print(f"Processing file {self._file_count}/{self._total_file_count}")
        formatted_text = self.get_txt_file_text(filename)
        words = self.parse_text(formatted_text)
        self.add_word_counts(words)
    
    def write_point_to_file(self, point: str, filename: str):
        with open(filename, "a+") as points_file:
            points_file.write(POINT_PREFIX + point + '\n')

    def generate_txt_files(self):
        if not os.path.isdir(self._txt_folder_path):
            os.mkdir(self._txt_folder_path)

        for pdf_file_name in self.generate_pdf_filenames():
            txt_file_name = get_txt_filename(pdf_file_name)
            txt_file_path = os.path.join(self._txt_folder_path, txt_file_name)
            if not os.path.exists(txt_file_path):
                formatted_pdf_text = self.get_formatted_pdf_text(pdf_file_name)
                with open(txt_file_path, "w") as txt_file:
                    txt_file.write(formatted_pdf_text)
                print("Created new text file entitled", txt_file_name)

    def gpt_divide_points(self, gpt_folder: str, filename: str):
        formatted_text = parse_text(self.get_txt_file_text(filename))
        file_points = LINE_SPLIT_PATTERN.split(formatted_text)
        gpt_filename = os.path.join(gpt_folder, GPT_PREFIX + FILENAME_SEPARATOR + filename)
        n_divisions = 0
        with open(gpt_filename, "w") as gpt_file:
            n_characters = 0
            for point in file_points:
                point_length = len(point)
                if point_length + n_characters > MAX_GPT_CHARACTERS:
                    n_divisions += 1
                    gpt_file.write(str(n_divisions) + GPT_SEPARATOR)
                    n_characters = point_length
                else:
                    n_characters += point_length
                gpt_file.write(point + '\n')

    def gptify(self):
        if not self.has_generated_txt_files():
            self.generate_txt_files()

        gpt_folder = os.path.join(self._path, self._folder_name + GPT_SUFFIX)
        os.mkdir(gpt_folder)
        threads = []
        for filename in self._filename_generator():
            thread = threading.Thread(
                target=self.gpt_divide_points, args=(gpt_folder, filename)
            )
            thread.start()
        
        for thread in threads:
            thread.join()     

class PointProcessor(TextProcessor):

    def __init__(self, folder_name: str, path: str = FOLDER_DIR):
        super().__init__(folder_name, path)
        if not self.has_generated_txt_files():
            self.generate_txt_files()

    def points(self, filename: str):
        assert is_txt(filename), "Must be a text file"
        fulltext = parse_fulltext(self.get_txt_file_text(filename))
        saved_filename = get_saved_points_filename(filename)
        points_output_filepath = get_points_output_filepath(saved_filename)
        point_list = PointList(fulltext)
        n_points = len(fulltext)

        display = PointCLI(progress_bar_row=3, progress_bar_length=PROGRESS_BAR_LENGTH)
        display.update()
        while point_list.has_points():
            point = point_list.current()
            completion_percentage = point_list.get_completion_percentage()
            display.clear()
            display.draw_line()
            print(point + POINT_SUFFIX)
            display.move_to_progress_bar_row()
            display.draw_line()
            display.display_message()
            display.display_features(completion_percentage, point_list.point_number, n_points)
            display.move_tail_rows(1)
            display.draw_line()

            if point_list.has_other_point:
                point_list.set_other_point(None)

            forward = True
            key = getkey()
            if key == DELETE_KEY:
                display.update()
                break
            elif key == ESCAPE_KEY:
                display.update()
                exit()
            elif key == COMMAND_KEY:
                sys.stdout.write(COMMAND_PROMPT)
                point_list.handle_command(input())
                forward = False
            elif key in BACKWARD_KEYS:
                point_list.backward()
                forward = False
            elif key not in FORWARD_KEYS:
                self.write_point_to_file(point, points_output_filepath)

            display.update()
            if forward:
                point_list.forward()

    def points_from_files(self):
        if not self.has_generated_txt_files():
            self.generate_txt_files()

        for pdf_filename in get_files_in_directory(self._folder_path):
            txt_filename = get_txt_filename(pdf_filename)
            if not has_points(txt_filename):
                self.points(txt_filename)