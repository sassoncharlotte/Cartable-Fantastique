from configparser import ConfigParser
from typing import Tuple
from fantastic.exercises.select.entities_phrases import EntitiesPhrases
from fantastic.exercises.utils import (
    splits_to_sentences,
    clean_entities_spaces,
)


class CochePhrases(EntitiesPhrases):
    """Class to adapt CochePhrase exercices"""

    output_folder_name: str = "coche_phrases"

    def __init__(self, path: str, config: ConfigParser) -> None:
        EntitiesPhrases.__init__(self, path, config)


    def convert_to_html(
        self, text: str, html_output: str, word_id_count: int, entity_id_count: int
    ) -> Tuple[str, int, int]:
        """Gets the list of selectable entities and converts it to html.

        Parameters:
        - html_output: current value of the html of the exercice
        - word_id_count: current value of the id of words
        - entity_id_count: current value of the id of entities
        Returns:
        new value of word_id_count and entity_id_count
        html_output: html version of the text"""

        # storing the symbol, if there is one, to be able to clean the sentences later
        self.symbol = self.symbols_in_exercice(text)

        entities_list = splits_to_sentences(
            text, split_chars=EntitiesPhrases.sentences_separators
        )

        entities_list = clean_entities_spaces(entities_list)

        # getting the right path to js script
        self.js_script_path = EntitiesPhrases.js_script_path

        # convertion to html
        html_output, word_id_count, entity_id_count = self.text_to_html_coche_phrases(
            entities_list, html_output, word_id_count, entity_id_count
        )

        return html_output, word_id_count, entity_id_count
