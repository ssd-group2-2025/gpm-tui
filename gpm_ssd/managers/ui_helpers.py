from typing import Callable, Any
from valid8 import ValidationError


class UIHelpers:
    @staticmethod
    def read_input(prompt: str, builder: Callable) -> Any:
        while True:
            try:
                line = input(f'{prompt}: ')
                res = builder(line.strip())
                return res
            except (TypeError, ValueError, ValidationError) as e:
                print(e)

    @staticmethod
    def print_separator(width: int = 80):
        print('-' * width)

    @staticmethod
    def print_header(title: str, width: int = 80):
        UIHelpers.print_separator(width)
        print(f"{title:^{width}}")
        UIHelpers.print_separator(width)
