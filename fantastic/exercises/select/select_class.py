import json
import os
from typing import Tuple
from configparser import ConfigParser
from spacy.lang.fr import French
from transformers.pipelines.token_classification import TokenClassificationPipeline
from nltk.stem.snowball import FrenchStemmer
from nltk import word_tokenize
from fantastic.exercises.exercise import Exercise
from fantastic.exercises.utils import (
    text_to_html,
    find_symbols,
    splits_to_sentences,
    index_words,
    clean_entities_spaces,
    replace_starting_from_the_end,
)

class Select(Exercise):

    template_name = "select"

    def __init__(self, json_path: str, config: ConfigParser) -> None:

        Exercise.__init__(self, json_path, config, self.template_name, self.output_folder_name)

        self.js_script_path = ""
        self.number_of_colors = 1
        self.displayed_colors_dict = {}
        self.list_of_guideline_tokens = []
        self.list_of_guideline_tokens_spacy = []
        self.symbol = ""
        self.categories_in_guideline = []
        self.displayed_colors_dict_select = json.loads(self.config.get("select", "displayed_colors_dict"))
        self.possible_colors_in_guideline = json.loads(self.config.get("select", "possible_colors_in_guideline"))
        self.stemmed_verbs_guideline = json.loads(self.config.get("select", "stemmed_verbs_guideline"))
        self.verb_if_no_color_in_guideline = self.config.get("select", "verb_if_no_color_in_guideline").strip('"')
        self.verb_if_color_in_guideline = self.config.get("select", "verb_if_color_in_guideline").strip('"')
        self.useless_verb_groups = json.loads(self.config.get("select", "useless_verb_groups"))
        self.useless_verb_groups_replacement = self.config.get("select", "useless_verb_groups_replacement").strip('"')
        self.punctuation = self.config.get("select", "punctuation").strip('"')
        self.non_symbols_chars = json.loads(self.config.get("select", "non_symbols_chars"))


    def adapt(self, nlp_token_class: TokenClassificationPipeline, nlp: French) -> None:
        """Principal function
        1. gets the data from the json file
        2. tokenizes the guideline with two different nlp models
        3. determines the number of colors and the colors to display
        4. adapts the guidelines
        5. converts to html the guideline, additional guideline and exercise_text
        6. gets the path to the js script
        7. creates the html output from the jinja template and the html data"""

        # getting the data from json file
        guideline = self.find_guideline()
        additional_guideline = "".join(
            self.find_additional_guideline()
        )  # find additional guideline returns a tuple

        sentences = self.find_sentences()  # list of sentences from exercise_text

        # tokenizing guideline
        self.list_of_guideline_tokens = nlp_token_class(guideline)
        self.list_of_guideline_tokens_spacy = nlp(guideline)

        # determining nb of colors and a dict of colors to display
        self.number_of_colors, self.displayed_colors_dict = self.colors_to_display()

        # getting the list of categories in the guideline
        # for now it is only implemented for "Classe"
        self.categories_in_guideline = self.get_categories_in_guideline()

        # adapting guideline
        guideline = self.adapt_guideline(guideline)

        if self.categories_in_guideline:
            # it means that we need to color and frame some words in the guideline
            word_indexs_list = index_words(guideline, self.categories_in_guideline)
            guideline_html = (
                self.__text_to_html_guideline(guideline, word_indexs_list)
                if word_indexs_list
                else text_to_html([guideline], False)
            )

        else:
            # we don't need to color anything in the guideline
            guideline_html = text_to_html([guideline], False) if guideline != "" else ""

        # getting the html version of the additional guideline and exercise text
        additional_guideline_html = (
            text_to_html([additional_guideline], False)
            if additional_guideline != ""
            else ""
        )
        exercise_text_html = (
            self.__text_to_html_select(sentences)
            if sentences and isinstance(sentences[0], str)
            else ""
        )

        # getting the html of the script tag
        script_js = self.__get_js_script()

        # generating the output from the jinja template
        self.html_output = self.html_template.render(
            exercise_number=self.json_path.split(os.sep)[-1].split(".")[0],
            guideline=guideline_html,
            additional_guideline=additional_guideline_html,
            exercise_text_html=exercise_text_html,
            script_js=script_js,
            lines_per_page=self.lines_per_page,
        )


    def symbols_in_exercice(self, text: str) -> str:
        """Searching for symbols in the "énoncé"."""
        symbols_list = find_symbols(text, self.non_symbols_chars)
        if len(symbols_list) != 0:
            return symbols_list[0]
        return ""


    def __get_js_script(self) -> str:
        """Getting the html of the script tag that corresponds to the exercise."""
        displayed_colors_json = json.dumps(self.displayed_colors_dict)
        return f"<script id='script' type='text/javascript' src='{self.js_script_path}' number_of_colors='{self.number_of_colors}' displayed_colors_json='{displayed_colors_json}'> </script>"


    def adapt_guideline(self, guideline: str) -> str:
        """Replace the verbs with "colorie".

        Parameters: the guideline
        Returns: the new formulation of the guideline
        """

        # replacing the "recopie chaque phrase et" by "dans chaque phrase, "
        for useless_verb_group in self.useless_verb_groups:
            guideline = guideline.replace(
                useless_verb_group, self.useless_verb_groups_replacement
            )

        adapted_guideline = guideline
        color_id = 0
        stemmer = FrenchStemmer()
        guideline_list = word_tokenize(adapted_guideline, language="french")

        for word in guideline_list:

            # we take the radical of the word
            stemmed_word = stemmer.stem(word)

            if stemmed_word in self.stemmed_verbs_guideline:
                # the word is a verb that needs to be replaced with "colorie"

                if self.displayed_colors_dict == self.displayed_colors_dict_select:
                    # there is no color in the guideline
                    adapted_guideline = adapted_guideline.replace(
                        word,
                        self.verb_if_no_color_in_guideline
                        + str(self.displayed_colors_dict[str(color_id)]),
                    )

                else:
                    # there are colors in guideline
                    adapted_guideline = adapted_guideline.replace(
                        word, self.verb_if_color_in_guideline
                    )
                color_id += 1

        # cleaning of the result
        adapted_guideline_list = splits_to_sentences(adapted_guideline)
        adapted_guideline_list = clean_entities_spaces(adapted_guideline_list)

        # capitalizing the sentences
        for sentence in adapted_guideline_list:
            if len(sentence) > 1:
                new_sentence = (
                    sentence[0].upper() + sentence[1:]
                )  # .capitalize lowers every letter except the first one, sometimes we don't want that

                adapted_guideline = adapted_guideline.replace(sentence, new_sentence)

        return adapted_guideline

    def get_categories_in_guideline(self):
        """This method could be implemented for all types to color and frame
        the categories in the guideline. For now, it is only implemented for
        type "Classe"."""
        return []


    def colors_to_display(self) -> Tuple[int, dict]:
        """Getting the right colors to display."""
        number_of_colors, displayed_colors_dict = self.determine_number_of_colors()
        return number_of_colors, displayed_colors_dict


    def __text_to_html_guideline(self, guideline: str, word_indexes_list: list) -> str:
        """Generates the html of the guideline that have colors and frames on some words.

        Parameters:
        - guideline
        - word_indexes_list: the list of the indexes of the words that have to be framed and colored in the guideline
        it has the form : [(ind1, ind2), (ind3, ind4), ...] where ind1 is
        the number of spaces before the first letter of word1
        and ind2 the number of spaces before the last letter of word1

        Returns:
        html version of the guideline"""

        colors_dict = {
            "bleu": "blue_background",
            "rouge": "red_background",
            "vert": "green_background",
            "noir": "grey_background",
            "jaune": "yellow_background",
            "rose": "pink_background",
        }

        if len(word_indexes_list) > self.number_of_colors:
            # there is an error on either number_of_colors or word_indexes_list
            # there cannot be more words to color than the number_of_colors:
            # we don't take the whole list of word indexes
            word_indexes_list = word_indexes_list[: self.number_of_colors]

        html_output = "<span class='block'>"
        indice = 0
        ponctuation = ""

        words_list = guideline.split(" ")

        for i in range(len(words_list)):
            word = words_list[i]

            if word_indexes_list and i == word_indexes_list[0][0]:
                # we found a word that needs to be colored and framed
                color_class = colors_dict[self.displayed_colors_dict[str(indice)]]
                html_output += f"<span class='{color_class} framed'>"

            if len(word) > 1 and word[-1] in self.punctuation:
                # since we splited the guideline on the spaces, the punctuation is included in "word"
                # we remove the punctuation
                ponctuation = word[-1]
                word = word[:-1]

            # we add the word to the html_output
            html_output += f"<span class='word'>{word}</span>"

            if word_indexes_list and i == word_indexes_list[0][1]:
                # we reached the end of a group of word / word that needs to be colored
                del word_indexes_list[0]
                indice += 1
                html_output += "</span>" # closing of the span with the class "color_class"

            if ponctuation:
                # there was a punctuation (, or .) that we removed on the last word
                html_output += (
                    f"<span>{ponctuation}</span> <span class='space'> </span>"
                )
                ponctuation = ""

            else:
                html_output += "<span class='space'> </span>"

        html_output += "<br/></span>"

        return html_output


    def __text_to_html_select(self, blocks: list) -> str:
        """Parameters:
        blocks: each block is a part of the "énoncé" that cannot be cut from one page to the next one.

        Output:
        html_output: html version of the text.
        -> each word is inside a span with class word, each space in a span with a class space.
        -> a word and a space are inside a class with an id to color words.
        -> the selectable entities have a class "entities" or
        "framed_entities" (for entities that we want to display with a frame)"""

        block_id_count: int = 0
        word_id_count: int = 0  # we generate different ids for each word
        entity_id_count: int = 0  # we generate different ids for each clickable entity
        html_output: str = ""

        for block in blocks:
            html_output += f"<span class='block' id='block{block_id_count}'>"
            block_id_count += 1

            # we generate the html version of the block
            html_output, word_id_count, entity_id_count = self.convert_to_html(
                block, html_output, word_id_count, entity_id_count
            )

            # if there is a space at the end of the block, we remove it
            if not html_output.split("<span class='space'> </span>")[-1]:
                html_output = replace_starting_from_the_end(
                    html_output, "<span class='space'> </span>", "", 1
                )

            html_output += "<br/></span>"
        return html_output


    def __colors_in_guideline(self) -> dict:
        """If there are some colors in the guideline, we directy take these ones."""
        displayed_colors_dict = {}

        i = 0

        for word_dict in self.list_of_guideline_tokens:
            if word_dict["word"] in self.possible_colors_in_guideline:
                # a color is found
                displayed_colors_dict[str(i)] = word_dict["word"]
                i += 1

        return displayed_colors_dict


    def __number_of_verbs(self) -> int:
        """Counts the number of verbs in the guideline.
        The auxiliaries are not counted."""
        verbs = []
        indic = True # indicates if there is a relative pronoun directly before the verb

        for word_dict in self.list_of_guideline_tokens:

            if word_dict["entity_group"] == "V" and indic:
                verbs += [word_dict["word"]]

            if word_dict["entity_group"] == "V" and not indic:
                # this verb is preceded by a relative pronouns ("qui", "qu'", "dans lesquels", ...)
                # so we don't count it
                indic = True

            if word_dict["entity_group"] == "PROREL":
                indic = False

        for sent in self.list_of_guideline_tokens_spacy.sents:
            # we remove the auxiliaries from the verb list
            for token in sent:
                if token.tag_ == "AUX" and token.text in verbs:
                    verbs.remove(token.text)

        return len(verbs)


    def __number_of_nouns(self) -> int:
        """Counts the number of common nouns in the guideline."""
        nb_nouns = 0
        for word_dict in self.list_of_guideline_tokens:
            if word_dict["entity_group"] == "NC":
                nb_nouns += 1
        return nb_nouns


    def determine_number_of_colors(self) -> Tuple[int, dict]:
        """Looks at the guideline to deduce which colors to display.
        Returns:
        - number of colors
        - the dictionary of the colors to display"""

        # getting number of verbs and number of nouns in the guideline
        number_verbs = self.__number_of_verbs()
        number_nouns = self.__number_of_nouns()

        # getting the colors if there are some in the guideline
        displayed_colors_dict = self.__colors_in_guideline()

        if len(displayed_colors_dict.keys()) != 0:
            # we found colors in the guideline
            number_of_colors = len(displayed_colors_dict.keys())

        else:
            # we didn't find colors in the guideline : we put the default ones
            displayed_colors_dict = self.displayed_colors_dict_select
            if number_verbs != 0:
                number_of_colors = min(number_verbs, number_nouns)
            else:
                number_of_colors = self.number_of_colors
        return number_of_colors, displayed_colors_dict
