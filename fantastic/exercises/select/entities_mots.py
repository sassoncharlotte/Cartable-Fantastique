from configparser import ConfigParser
import json
import re
from typing import Tuple
from fantastic.exercises.select.select_class import Select
from fantastic.exercises.utils import replace_starting_from_the_end


class EntitiesMots(Select):
    js_script_path="../js/select.js"

    def __init__(self, path: str, config: ConfigParser) -> None:
        Select.__init__(self, path, config)
        self.symbol = []
        self.remove_space_before = json.loads(self.config.get("entities_mots", "remove_space_before"))
        self.remove_space_after = json.loads(self.config.get("entities_mots", "remove_space_after"))

    def text_to_html_coche_mots(
        self,
        entities_list: list,
        html_output: str,
        word_id_count: int,
        entity_id_count: int,
    ) -> Tuple[str, int, int]:
        """Parameters:
        - entities_list: list of words, punctuation, accents...
        - html_output: current value of the html version of the "énoncé"
        - word_id_count: current value of word id
        - entity_id_count: current value of entity id

        Returns:
        new value of word_id_count and entity_id_count
        html_output: html version of the text.
        -> each word is inside a span with class word and class entities, a color number and an id
        -> each space in a span with a class space
        -> a word and a space are inside a class with an id to color words."""

        for word in entities_list:

            if word in self.remove_space_before:
                if html_output.split("<span class='space'> </span>")[-1] == " </span>":
                    # checking if the last character was a space
                    html_output = replace_starting_from_the_end(
                        html_output, "<span class='space'> </span>", "", 1
                    ) # we remove it

            if re.search(r"\w\.$", word):
                # we don't want the number of the sentence to be selectable
                html_output_temp = (
                    f"<span id='word{word_id_count}'> <span class='word'>"
                    + word
                    + "</span> <span class='space'> </span> </span>"
                )
                word_id_count += 1

            elif word in self.remove_space_after:
                # adding the html version of the word to the html but no span with class "space" after
                html_output_temp = (
                    f"<span id='word{word_id_count}'> <span class='word entities' color_number = 0"
                    f" id = 'entity{entity_id_count}'>"
                    + word
                    + "</span> </span>"
                )
                entity_id_count += 1
                word_id_count += 1

            else:
                html_output_temp = (
                    f"<span id='word{word_id_count}'> <span class='word entities' color_number = 0"
                    f" id = 'entity{entity_id_count}'>"
                    + word
                    + "</span> <span class='space'> </span> </span>"
                )
                entity_id_count += 1
                word_id_count += 1

            html_output += html_output_temp

        return html_output, word_id_count, entity_id_count
