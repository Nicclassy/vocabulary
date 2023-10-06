import os
import sys
from typing import Optional

from src.constants import (
    COMMAND_MAPPING, 
    INCOMPLETE_COLOUR, 
    COMPLETE_COLOUR,
    POINT_PREFIX, 
    RESET,
    SIDE_QUEST_COLOUR,
    JSTOR_FILE
)
from src.processing import clear_screen
from src.parsing import parse_line

class PointList:

    def __init__(self, points: list[str]):
        self.__points = points
        self.__n_points = len(points)
        self.__index = 0
        self.__point_number = 1
        self.__has_other_point = False
        self.__other_point = None

    @property
    def has_other_point(self) -> bool:
        return self.__has_other_point

    @property
    def point_number(self) -> Optional[int]:
        return None if self.__has_other_point else self.__point_number
    
    def get_completion_percentage(self) -> Optional[float]:
        return None if self.__has_other_point else self.__point_number / self.__n_points

    def forward(self):
        self.__point_number += 1
        self.__index += 1

    def backward(self):
        decrement = 1 * (self.__index != 0)
        self.__point_number -= decrement
        self.__index -= decrement

    def get_point_at_index(self, index: int) -> str:
        return parse_line(self.__points[index], remove_newlines=True)

    def current(self) -> str:
        return self.__other_point or self.get_point_at_index(self.__index)
    
    def has_points(self) -> bool:
        return self.__index < self.__n_points
    
    def set_other_point(self, point: Optional[str]):
        self.__has_other_point = point is not None
        self.__other_point = point

    def handle_command(self, command: str):
        if not command:
            return 
        
        command_name, *args = command.split()
        if (command_info := COMMAND_MAPPING.get(command_name)) is None:
            other_point = (
                "Invalid point. Choose a command from the list below:\n"
                + "\n".join(COMMAND_MAPPING)
            )
            self.set_other_point(other_point)
            return

        expected_argc, *validations = command_info
        if expected_argc != (argc := len(args)):
            other_point = "Incorrect arg count."

        elif not all(validations[i](args[i]) for i in range(argc)):
            other_point = "Not all arguments are valid."

        elif command_name == "test":
            other_point = "Testing!"

        elif command_name == "jump":
            jump_points = int(args[0])
            new_point_number = self.__point_number + jump_points
            if 0 <= new_point_number < self.__n_points:
                self.__point_number = new_point_number
                self.__index = new_point_number - 1
                return
            else:
                other_point = (
                    f"Jump must between {self.__n_points - jump_points} "
                    f"and {self.__n_points}."
                )

        elif command_name == "preview":
            last_point = self.__point_number + int(args[0])
            other_point = ""
            if 0 <= last_point < self.__n_points:
                for i in range(self.__point_number, last_point):
                    other_point += POINT_PREFIX + self.get_point_at_index(i) + '\n'
            else:
                other_point = (
                    f"Preview quantity must be between {self.__n_points - last_point}"
                    f"and {last_point}."
                )

        elif command_name == "bad":
            point = self.get_point_at_index(self.__index)
            with open(JSTOR_FILE, "a") as jstor_file:
                jstor_file.write(POINT_PREFIX + point + '\n')
            
            self.forward()
            return
                
        self.set_other_point(other_point)


class PointCLI:

    SEPARATOR = ' '
    PROGRESS_BAR = ' '
    NO_POINT = '*'
    NO_PERCENT = '?'
    PERCENT = '%'
    RATIO_SEPARATOR = '|'

    ORIGIN = (0, 0)
    SEPARATOR_COUNT = 2
    DEFAULT_MESSAGE = "Press any key to continue"

    def __init__(self, progress_bar_row: int = 3, 
                 progress_bar_length: int = 10, line_separator: str = "-"):
        self.__progress_bar_row = progress_bar_row
        self.__progress_bar_length = progress_bar_length
        self.__line_separator = line_separator
        self.__n_columns, self.__n_rows = os.get_terminal_size()
        self.__write_position = PointCLI.ORIGIN
        self.__message = PointCLI.DEFAULT_MESSAGE

    def set_message(self, message: str):
        self.__message = message

    def numeric_completion(self, line_number: Optional[int], total_points: int) -> str:
        if line_number is None:
            return f"[{PointCLI.NO_POINT}{PointCLI.RATIO_SEPARATOR}{total_points}]"
        return f"[{line_number}|{total_points}]"
    
    def percentage_completion(self, completion_percentage: Optional[float]) -> str:
        if completion_percentage is None:
            return PointCLI.NO_PERCENT + PointCLI.PERCENT
        return str(int(completion_percentage * 100)) + PointCLI.PERCENT

    def progress_bar(self, completion_percentage: Optional[float]) -> str:
        if completion_percentage is None:
            return f"[{SIDE_QUEST_COLOUR}{PointCLI.PROGRESS_BAR * self.__progress_bar_length}{RESET}]"
        
        n_complete_bars = int(self.__progress_bar_length * completion_percentage)
        n_incomplete_bars = self.__progress_bar_length - n_complete_bars
        return (f"[{COMPLETE_COLOUR}{PointCLI.PROGRESS_BAR * n_complete_bars}"
                f"{INCOMPLETE_COLOUR}{PointCLI.PROGRESS_BAR * n_incomplete_bars}{RESET}]")
    
    def display_features(self, completion_percentage: float, line_number: int, total_points: int):
        numeric_completion = self.numeric_completion(line_number, total_points)
        percentage_completion = self.percentage_completion(completion_percentage)
        progress_bar = self.progress_bar(completion_percentage)
        total_length = (self.__progress_bar_length 
                        + len(percentage_completion)
                        + len(numeric_completion) + self.SEPARATOR_COUNT)
        combined_features = (progress_bar + self.SEPARATOR + percentage_completion
                             + self.SEPARATOR + numeric_completion)
        self.move_from_corner(2, total_length + 1)
        sys.stdout.write(combined_features)

    def display_message(self):
        sys.stdout.write(self.__message)

    def draw_line(self):
        sys.stdout.write(self.__line_separator * self.__n_columns + "\n")

    def move_cursor_to_position(self, row: int, column: int):
        self.__write_position = (row, column)
        sys.stdout.write(f"\033[{row};{column}H")

    def move_to_progress_bar_row(self):
        self.move_tail_rows(self.__progress_bar_row)

    def move_tail_rows(self, n_rows: int):
        self.__write_position = (self.__n_rows - n_rows, 0)
        self.move_cursor_to_position(*self.__write_position)

    def move_from_corner(self, n_rows: int, n_columns: int):
        position = (self.__n_rows - n_rows, self.__n_columns - n_columns)
        self.move_cursor_to_position(*position)
    
    def update(self):
        self.__n_columns, self.__n_rows = os.get_terminal_size()
        self.__write_position = PointCLI.ORIGIN
        self.move_cursor_to_position(*self.__write_position)
        self.clear()

    clear = staticmethod(clear_screen)