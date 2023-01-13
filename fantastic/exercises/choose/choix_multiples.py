from configparser import ConfigParser
from fantastic.exercises.choose.choose_class import Choose


class ChoixMultiples(Choose):
    """See Exercise class documentation to understand the different parameters"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        super().__init__(
            json_path,
            config,
            output_folder_name="choix-multiples"
        )
