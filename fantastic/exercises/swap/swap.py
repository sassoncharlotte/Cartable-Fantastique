from configparser import ConfigParser
import json
import os
import re
from typing import Tuple
from fantastic.exercises.exercise import Exercise
from fantastic.exercises.utils import (
    text_to_html,
    find_symbols,
    clean_entities_spaces,
    replace_starting_from_the_end,
    entities_if_symbols,
)


class Swap(Exercise):
    template_name: str = "swap"
    output_folder_name: str = "swap"

    def __init__(self, json_path: str, config: ConfigParser, lines_per_page: int = 1) -> None:
        Exercise.__init__(
            self, json_path, config, self.template_name, self.output_folder_name, lines_per_page
        )
        self.symbol: str = ""
        self.non_symbols_chars: list = json.loads(self.config.get("swap", "non_symbols_chars"))

    def adapt(self) -> None:
        """Principal function
        1. gets the data from the json file
        2. converts to html the guideline, additional guideline and exercise_text
        3. creates the html output from the jinja template and the html data"""

        # getting the data from json file
        guideline = self.find_guideline()
        additional_guideline = "".join(
            self.find_additional_guideline()
        )  # find additional guideline returns a tuple
        sentences = self.find_sentences()  # list of sentences from exercise_text

        # getting the html version of the guideline, additional guideline and exercise text
        guideline_html = text_to_html([guideline], False) if guideline != "" else ""
        additional_guideline_html = (
            text_to_html([additional_guideline], False)
            if additional_guideline != ""
            else ""
        )
        exercise_text_html = (
            self.__text_to_html_swap(sentences)
            if sentences and isinstance(sentences[0], str)
            else ""
        )

        # generating the output from the jinja template
        self.html_output = self.html_template.render(
            exercise_number=self.json_path.split(os.sep)[-1].split(".")[0],
            guideline=guideline_html,
            additional_guideline=additional_guideline_html,
            exercise_text_html=exercise_text_html,
            lines_per_page=self.lines_per_page,
        )


    def __symbols_in_exercice(self, text: str) -> str:
        """Searching for symbols in the "énoncé"."""
        symbols_list = find_symbols(text, self.non_symbols_chars)
        if len(symbols_list) != 0:
            return symbols_list[0]
        return ""


    def __text_to_html_swap(self, blocks: list) -> str:
        """Parameters:
        blocks: each block is a part of the "énoncé" that cannot be cut from one page to the next one.

        Output:
        html_output: html version of the text.
        -> each word is inside a span with class word and has an id.
        -> each space in a span with a class space.
        -> the swappable entities have:
        for the css style: a class framed_entities.
        for the swap.js script: a class framed_entities_id and
        an attribute frames_entities with value framed_entities_id."""

        block_id_count: int = 0
        word_id_count: int = 0  # we generate different ids for each word
        html_output: str = ""

        for block in blocks:
            html_output += f"<span class='block' id='block{block_id_count}'>"

            # we generate the html version of the block
            html_output, word_id_count = self.__block_to_html(
                block, html_output, word_id_count, block_id_count
            )

            # if there is a space at the end of the block, we remove it
            if not html_output.split("<span class='space'> </span>")[-1]:
                html_output = replace_starting_from_the_end(
                    html_output, "<span class='space'> </span>", "", 1
                )

            block_id_count += 1

            html_output += "<br/></span>"
        return html_output

    def __block_to_html(
        self, text: str, html_output: str, word_id_count: int, block_id_count: int
    ) -> Tuple[str, int]:
        """Gets the list of swappable entities and converts it to html.

        Parameters:
        - html_output: current value of the html of the exercice
        - word_id_count: current value of the id of words
        - block_id_count: number of the block
        Returns:
        new value of word_id_count
        html_output: html version of the text"""

        # searching for symbols in the "énoncé" and spliting on symbol
        self.symbol = self.__symbols_in_exercice(text)
        words_list = entities_if_symbols(text, self.symbol)

        if words_list:
            # the entities are groups of words
            words_list = clean_entities_spaces(words_list)

            # convertion to html
            html_output, word_id_count = self.__words_list_to_html(
                words_list, html_output, word_id_count, block_id_count
            )

        else:
            # there aren't any symbol to split on, we couldn't get the list of entities
            html_output = ""
        return html_output, word_id_count

    def __words_list_to_html(
        self,
        entities_list: list,
        html_output: str,
        word_id_count: int,
        block_id_count: int,
    ) -> Tuple[str, int]:
        """Parameters:
        - entities_list: list of groups of words
        - html_output: current value of the html version of the "énoncé"
        - word_id_count: current value of word id
        - entity_id_count: current value of entity id

        Returns:
        new value of word_id_count
        html_output: html version of the text.
        -> each word is inside a span with class word, each space in a span with a class space
        -> a word and a space are inside a class with an id to color words.
        -> selectable groups are in a span with class 'framed_entities',
                a color number and an id that are used in the js script to change the color of the background.
                They also have an onClick attribute"""

        if re.search(r"\w\.$", entities_list[0]):
            # we don't want the number of the sentence to be swappable
            html_output += (
                f"<span id='word{word_id_count}'><span class='word'>"
                + entities_list[0]
                + "</span> <span class='space'> </span> </span>"
            )
            word_id_count += 1

        if len(entities_list) > 1:

            for entity in entities_list[1:]:
                # each entity is a clickable group of words / word of the exercise
                html_output_temp = ""

                words_list = entity.split(" ")

                for word in words_list:

                    if word == self.symbol:
                        # nothing is done
                        continue

                    if len(words_list) == 1:
                        # the "group of word" to swap is actually a word
                        # so we put the class framed_entities on the word and framed_entities_id on the word
                        html_output_temp += (
                            f"<span class='framed_entities framed_entities_{block_id_count}' framed_entities = 'framed_entities_{block_id_count}' onclick = 'myFunction(this)'> <span class='word' id='word{word_id_count}'>"
                            + word
                            + "</span> </span> <span class='space'> </span>"
                        )
                    else:
                        html_output_temp += (
                            f"<span id='word{word_id_count}'><span class='word'>"
                            + word
                            + "</span> <span class='space'> </span> </span>"
                        )
                    word_id_count += 1

                if len(words_list) > 1:
                    # removing the last character of the html output temp if it is a space
                    html_output_temp_cleaned = replace_starting_from_the_end(
                        html_output_temp, "<span class='space'> </span>", "", 1
                    )
                    # adding a span with class 'framed_entities' and 'framed_entities_id' around the bunch of words that are selectables
                    html_output_temp = (
                        f"<span class = 'framed_entities framed_entities_{block_id_count}' framed_entities = 'framed_entities_{block_id_count}' onclick = 'myFunction(this)'>"
                        + html_output_temp_cleaned
                        + "</span> <span class='space'> </span>"
                    )

                html_output += html_output_temp

        return html_output, word_id_count
