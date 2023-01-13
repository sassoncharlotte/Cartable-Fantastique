from configparser import ConfigParser
from typing import Tuple
import json
from fantastic.exercises.select.entities_groupe_mots import EntitiesGroupeMots
from fantastic.exercises.select.entities_phrases import EntitiesPhrases
from fantastic.exercises.utils import (
    splits_to_sentences,
    clean_entities_spaces,
    entities_if_symbols,
)


class CocheIntrus(EntitiesGroupeMots, EntitiesPhrases):
    """Class to adapt CocheIntrus exercices"""

    output_folder_name: str = "coche_intrus"

    def __init__(self, path: str, config: ConfigParser) -> None:
        EntitiesGroupeMots.__init__(self, path, config)
        EntitiesPhrases.__init__(self, path, config)
        self.displayed_colors_dict = json.loads(self.config.get("intrus", "displayed_colors_coche"))
        self.generic_sentence = self.config.get("intrus", "generic_sentence_default_coche").strip('"')
        self.specifiers_singular = json.loads(self.config.get("intrus", "specifiers_singular"))
        self.specifiers_plural = json.loads(self.config.get("intrus", "specifiers_plural"))
        self.specifiers_both = json.loads(self.config.get("intrus", "specifiers_both"))
        self.generic_sentence_singular = self.config.get("intrus", "generic_sentence_singular_coche").strip('"')
        self.generic_sentence_plural = self.config.get("intrus", "generic_sentence_plural_coche").strip('"')
        self.generic_sentence_both = self.config.get("intrus", "generic_sentence_both_coche").strip('"')

    def adapt_guideline(self, guideline: str) -> str:
        """Parameters:
        guideline
        Returns:
        adapted_guideline: version of the guideline with the generic sentence"""

        for i in range(len(self.list_of_guideline_tokens)):

            if self.list_of_guideline_tokens[i]["word"] in ["intrus", "int"]:
                # sometimes the POS tagger has bugs and "intrus" becomes "int ##rus"

                if (
                    self.list_of_guideline_tokens[i - 1]["word"]
                    in self.specifiers_plural
                ):
                    # there are several "intrus"
                    if i >= 3:
                        if (
                            self.list_of_guideline_tokens[i - 2]["word"] == "ou"
                            and self.list_of_guideline_tokens[i - 3]["word"] == "le"
                        ):
                            self.generic_sentence = self.generic_sentence_both
                        else:
                            self.generic_sentence = self.generic_sentence_plural

                elif (
                    self.list_of_guideline_tokens[i - 1]["word"] in self.specifiers_both
                ):
                    # the plurality of "intrus" is not specified
                    self.generic_sentence = self.generic_sentence_both

                elif (
                    self.list_of_guideline_tokens[i - 1]["word"]
                    in self.specifiers_singular
                ):
                    # there is only one "intrus"
                    self.generic_sentence = self.generic_sentence_singular

        adapted_guideline = ""
        guideline_list = splits_to_sentences(guideline)

        for i in range(len(guideline_list) - 1):
            # we keep every sentence except the last one
            adapted_guideline += guideline_list[i] + " "

        adapted_guideline += self.generic_sentence

        return adapted_guideline

    def colors_to_display(self) -> Tuple[int, dict]:
        return self.number_of_colors, self.displayed_colors_dict

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
            # the entities are sentences
            entities_list = splits_to_sentences(
                text, split_chars=EntitiesPhrases.sentences_separators
            )

            entities_list = clean_entities_spaces(entities_list)

            # getting the right path to js script
            self.js_script_path = EntitiesPhrases.js_script_path

            # convertion to html
            (
                html_output,
                word_id_count,
                entity_id_count,
            ) = self.text_to_html_coche_phrases(
                entities_list, html_output, word_id_count, entity_id_count
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
