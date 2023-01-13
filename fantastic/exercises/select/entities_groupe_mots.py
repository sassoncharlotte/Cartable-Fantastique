from configparser import ConfigParser
import re
from typing import Tuple
from fantastic.exercises.select.select_class import Select
from fantastic.exercises.utils import replace_starting_from_the_end


class EntitiesGroupeMots(Select):
    js_script_path="../js/select_for_types_with_frame.js"

    def __init__(self, path: str, config: ConfigParser) -> None:
        Select.__init__(self, path, config)

    def text_to_html_groupe_mots(
        self,
        entities_list: list,
        html_output: str,
        word_id_count: int,
        entity_id_count: int,
    ) -> Tuple[str, int, int]:
        """Parameters:
        - entities_list: list of groups of words
        - html_output: current value of the html version of the "énoncé"
        - word_id_count: current value of word id
        - entity_id_count: current value of entity id

        Returns:
        new value of word_id_count and entity_id_count
        html_output: html version of the text.
        -> each word is inside a span with class word, each space in a span with a class space
        -> a word and a space are inside a class with an id to color words.
        -> selectable group is in a span with class 'framed_entities',
                a color number and an id that are used in the js script to change the color of the background"""

        for entity in entities_list:
            html_output_temp = ""

            words_list = entity.split(" ")

            for word in words_list:

                if word == self.symbol:
                    # nothing is done
                    continue

                if re.search(r"\w\.$", word):
                    # we don't want the number of the sentence to be selectable
                    html_output_temp += (
                        f"<span id='word{word_id_count}'> <span class='word'>"
                        + word
                        + "</span> <span class='space'> </span> </span>"
                    )

                elif len(words_list) == 1:
                    # the "group of word" to select is actually a word
                    # so we put the class framed_entities on the word
                    html_output_temp += (
                        f"<span class='framed_entities' color_number = 0"
                        f" id = 'entity{entity_id_count}'> <span class='word' id='word{word_id_count}'>"
                        + word
                        + "</span> </span> <span class='space'> </span>"
                    )
                    entity_id_count += 1

                else:
                    html_output_temp += (
                        f"<span id='word{word_id_count}'> <span class='word'>"
                        + word
                        + "</span> <span class='space'> </span> </span>"
                    )
                word_id_count += 1

            if len(words_list) > 1:
                # removing the last character of the html output temp if it is a space
                html_output_temp_cleaned = replace_starting_from_the_end(
                    html_output_temp, "<span class='space'> </span>", "", 1
                )

                # adding a span with class 'framed_entities' around the bunch of words that are selectables
                html_output_temp = (
                    f"<span color_number = 0 class = 'framed_entities' id = 'entity{entity_id_count}'>"
                    + html_output_temp_cleaned
                    + "</span> <span class='space'> </span>"
                )
                entity_id_count += 1

            html_output += html_output_temp
        return html_output, word_id_count, entity_id_count
