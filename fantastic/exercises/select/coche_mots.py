from configparser import ConfigParser
import string
from typing import Tuple
from fantastic.exercises.select.entities_mots import EntitiesMots
from fantastic.exercises.select.entities_groupe_mots import EntitiesGroupeMots
from fantastic.exercises.utils import (
    clean_entities_spaces,
    split_word,
    entities_if_symbols
)

class CocheMots(EntitiesMots, EntitiesGroupeMots):
    """Class to adapt CocheMots exercices"""

    output_folder_name: str = "coche_mots"

    def __init__(self, path: str, config: ConfigParser) -> None:
        EntitiesMots.__init__(self, path, config)
        EntitiesGroupeMots.__init__(self, path, config)
        self.split_characters = self.config.get("coche_mots", "split_characters") + string.punctuation


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

        # searching for symbols in the "énoncé" and spliting on symbol
        self.symbol = self.symbols_in_exercice(text)
        words_list = entities_if_symbols(text, self.symbol)

        if words_list == []:
            # the entities are words, punctuation, apostrophes...
            words_list = text.split(" ")
            words_list = clean_entities_spaces(words_list)

            # getting the right path to js script
            self.js_script_path = EntitiesMots.js_script_path

            # separating the word from the punctuation and the accents
            new_words_list = []
            for word in words_list:
                new_words_list += split_word(word, self.split_characters)

            # unifying the numbers
            for i in range(len(new_words_list) - 1):
                if (
                    new_words_list[i][-1].isdigit()
                    and new_words_list[i + 1][0].isdigit()
                ):
                    new_words_list[i] = new_words_list[i] + new_words_list[i + 1]
                    new_words_list.remove(new_words_list[i + 1])
            words_list = new_words_list

            # unifying the sentences' numbers
            if len(words_list) > 1 and words_list[1] == ".":
                words_list[0] = words_list[0] + words_list[1]
                words_list.remove(words_list[1])

            # convertion to html
            html_output, word_id_count, entity_id_count = self.text_to_html_coche_mots(
                words_list, html_output, word_id_count, entity_id_count
            )

        else:
            # the entities are groups of words
            self.lines_per_page = 1
            words_list = clean_entities_spaces(words_list)

            # getting the right path to js script
            self.js_script_path = EntitiesGroupeMots.js_script_path

            # convertion to html
            html_output, word_id_count, entity_id_count = self.text_to_html_groupe_mots(
                words_list, html_output, word_id_count, entity_id_count
            )

        return html_output, word_id_count, entity_id_count
