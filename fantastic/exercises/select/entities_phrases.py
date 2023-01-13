from configparser import ConfigParser
import json
from typing import Tuple
from fantastic.exercises.select.select_class import Select
from fantastic.exercises.utils import replace_starting_from_the_end


class EntitiesPhrases(Select):
    sentences_separators: list = [".", "!", "?"]
    js_script_path: str = "../js/select.js"

    def __init__(self, path: str, config: ConfigParser) -> None:
        Select.__init__(self, path, config)
        self.remove_space_before = json.loads(self.config.get("entities_phrases", "remove_space_before"))

    def text_to_html_coche_phrases(
        self,
        entities_list: list,
        html_output: str,
        word_id_count: int,
        entity_id_count: int,
    ) -> Tuple[str, int, int]:
        """Parameters:
        - entities_list: list of sentences
        - html_output: current value of the html version of the "énoncé"
        - word_id_count: current value of word id
        - entity_id_count: current value of entity id

        Returns:
        new value of word_id_count and entity_id_count
        html_output: html version of the text.
        -> each word is inside a span with class word, each space in a span with a class space
        -> a word and a space are inside a class with an id to color words.
        -> each sentence is in a span with class 'entities',
            a color number and an id that are used in the js script to change the color of the background"""

        for sentence in entities_list:
            html_output_temp = ""

            words_list = sentence.split(" ")

            for word in words_list:

                if word in self.remove_space_before:
                    if (
                        html_output_temp.split("<span class='space'> </span>")[-1]
                        == " </span>"
                    ):
                    # checking if the last character was a space
                        html_output_temp = replace_starting_from_the_end(
                            html_output_temp, "<span class='space'> </span>", "", 1
                        ) # we remove this space

                if word == self.symbol:
                    # nothing is done
                    continue

                html_output_temp += (
                    f"<span id='word{word_id_count}'><span class='word'>"
                    + word
                    + "</span> <span class='space'> </span> </span>"
                )
                word_id_count += 1

            if len(words_list) > 1:
                html_output_temp_cleaned = replace_starting_from_the_end(
                    html_output_temp, "<span class='space'> </span>", "", 1
                ) # we remove the last space if it is the last character of the sentence

                html_output_temp = (
                    f"<span color_number = 0 class = 'entities' id = 'entity{entity_id_count}'>"
                    + html_output_temp_cleaned
                    + "</span> <span class='space'> </span>"
                )
                entity_id_count += 1

            html_output += html_output_temp
        return html_output, word_id_count, entity_id_count
