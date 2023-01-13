from configparser import ConfigParser
from typing import List
import re
import os
import json
from nltk.stem.snowball import FrenchStemmer
from nltk import word_tokenize
from fantastic.exercises.exercise import Exercise
from fantastic.exercises.utils import text_to_html, index_words
from fantastic.exercises.choose.explore_guideline import find_choices_in_guideline
from fantastic.exercises.choose.explore_additional_guideline import (
    find_choices_in_add_guideline,
)
from fantastic.exercises.choose.explore_exercise_text import find_choices_in_sentences
from fantastic.exercises.choose.display_guideline_and_additional_guideline import (
    prepare_to_dipsplay_others,
)
from fantastic.exercises.choose.display_exercise_text import (
    prepare_to_dipsplay_exercise_text,
)
from fantastic.exercises.choose.choices_processing import (
    final_clean_choices,
    choices_to_html,
)
import fantastic.paths

config_file = ConfigParser()
config_file.read(os.path.join(fantastic.paths.FANTASTIC_DIR, "exercises", "data.cfg"))

class Choose(Exercise):
    """
    Class attributes:
        * template_name (str): The name of the template jinja to use to generate the html
        * non_separators (List[str]): A list of symbols characters considered as non separators
        * non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        * split_chars: (List[str]) : A list of additional symbols to split on in split_in_pieces
        in explore_exercise_text
        * exceptions_list: (List[str]): A list of all the patterns that could be separating the
        choices and not found by default in the exercise_text
        * replacing_symbol (str): A string to specify the symbol replacing all symbols spoted
        in the sentences
        * fill_symbol (str): A string to specify the symbol replacing all fill symbols
        spoted in the sentences
        * stemmed_verbs_to_replace (Dict[str]): A Dictionary containing as keys the stems of verbs to replace
        in the guideline and as values their corresponding replacement (ex: "écris" --> "choisis")
        * guideline_separators (dict): A Dictionary containing as keys the possible regex patterns matching a
        choice separator in the guideline (ordered from highest to lowest priority) and as values a list of all
        the regex patterns beginning with the key regex and representing a case where the key regex does not match
        a choice separator.
        (ex: {"\\sou\\s": "\\sou\\sbien"} means " ou " is considered as a separator only if not followed by "bien")
        * compare_choices_threshold (float) (default: 0.5): A float between 0 and 1 to tune the output of the
        heuristic compare_choices
        * has_choices_threshold (float) (default: 0.3): A float between 0 and 1 to tune the output of the
        heuristic has_choices
    """
    TEMPLATE_NAME: str = "choose"
    NON_SEPARATORS: List[str] = json.loads(config_file.get("choose","non_separators"))
    NON_FILL_CHARS: List[str] = json.loads(config_file.get("choose","non_fill_chars"))
    SPLIT_CHARS: List[str] = json.loads(config_file.get("choose","split_chars"))
    EXCEPTIONS_LIST: List[str] = json.loads(config_file.get("choose","exceptions_list"))
    REPLACING_SYMBOL: str = config_file.get("choose", "replacing_symbol").strip('"')
    FILL_SYMBOL: str = config_file.get("choose", "fill_symbol").strip('"')
    STEMMED_VERBS_TO_REPLACE: dict = json.loads(config_file.get("choose","stemmed_verbs_to_replace"))
    GUIDELINE_SEPARATORS: dict = json.loads(config_file.get("choose", "guideline_separators"))
    END_LAST_CHOICE_PATTERNS: List[str] = json.loads(config_file.get("choose", "end_last_choice_patterns"))
    COMPARE_CHOICES_THRESHOLD: float = json.loads(config_file.get("choose", "compare_choices_threshold"))
    HAS_CHOICES_THRESHOLD: float = json.loads(config_file.get("choose", "has_choices_threshold"))

    """See Exercise class documentation to understand the different parameters"""
    def __init__(
        self,
        json_path: str,
        config: ConfigParser,
        lines_per_page: int = 1,
        template_name: str = TEMPLATE_NAME,
        output_folder_name: str = "",
    ) -> None:
        super().__init__(
            json_path, config, template_name, output_folder_name, lines_per_page
        )
        self.choices = []


    def find_choices(self):
        """
        Returns the choices found in the exercise

        Parameters:
            See in class attributes the different parameters
        Returns:
            choices (List[List[str]]): A list containing lists of choices found
        """
        _, text_try = self.find_additional_guideline()
        sentences = self.find_sentences()
        # Some treatments needs to match white spaces
        non_separators_no_space = self.NON_SEPARATORS.copy()
        if " " in non_separators_no_space:
            non_separators_no_space.remove(" ")

        choices = find_choices_in_add_guideline(
            text_try,
            sentences,
            non_separators_no_space,
            self.NON_FILL_CHARS,
            self.REPLACING_SYMBOL,
        )  # first the function search in the "#text" field
        if not choices:  # if nothing is found
            choices = find_choices_in_guideline(
                self.find_guideline(),
                self.GUIDELINE_SEPARATORS,
                self.END_LAST_CHOICE_PATTERNS,
                self.REPLACING_SYMBOL,
                self.COMPARE_CHOICES_THRESHOLD,
                self.HAS_CHOICES_THRESHOLD,
                )
        if not choices:
            choices = find_choices_in_sentences(
                sentences,
                self.NON_SEPARATORS,
                self.NON_FILL_CHARS,
                self.REPLACING_SYMBOL,
                self.SPLIT_CHARS,
                self.EXCEPTIONS_LIST,
            )
        self.choices = choices
        return choices


    def prepare_to_display(
        self,
    ):  # must return Tuple (lines to display, choices to display)
        """
        Returns the lines & the choices to dusplay in the html

        Parameters:
            See in class attributes the different parameters
        Returns:
            to_display (Tuple[List[str], List[List[str]]]): A list containing lists of choices found
        """
        sentences = self.find_sentences()
        choices = self.choices.copy()
        number_couples_choices = len(choices) #each element of choices is a set of choices to fill in one place
        if number_couples_choices > 1:  # if choices in exercise text
            return prepare_to_dipsplay_exercise_text(
                sentences, choices, self.NON_FILL_CHARS, self.FILL_SYMBOL
            )
        else:
            return prepare_to_dipsplay_others(
                self.find_guideline(),
                sentences,
                choices,
                self.NON_FILL_CHARS,
                self.NON_SEPARATORS,
                self.REPLACING_SYMBOL,
                self.FILL_SYMBOL,
            )


    def adapt_guideline(self):
        """
        Returns the adapted guideline to display in the html

        Parameters:
            See in class attributes the different parameters
        Returns:
            adapted_guideline (str): The adaptation of the guideline
        """
        def __replace_and_capitalize(text: str, verb_to_replace: str, replacing_verb: str):
            """Replaces the verb_to_replace in a text by a replacing_verb and preserves capitalization"""
            if verb_to_replace[0].isupper():
                return text.replace(verb_to_replace, replacing_verb.capitalize())
            return text.replace(verb_to_replace, replacing_verb)

        adapted_guideline = self.find_guideline()
        stemmer = FrenchStemmer()
        guideline_list = word_tokenize(adapted_guideline, language="french")
        for word in guideline_list:
            stemmed_word = stemmer.stem(word)
            if stemmed_word in self.STEMMED_VERBS_TO_REPLACE:
                adapted_guideline = __replace_and_capitalize(
                    adapted_guideline,
                    word,
                    self.STEMMED_VERBS_TO_REPLACE[stemmed_word],
                    )
        return adapted_guideline


    def convert_to_html(self):
        """
        Returns the final string representing the html after computing it

        Parameters:
            See in class attributes the different parameters
        Returns:
            html_output (str): The final string to store ad html file
        """

        def __text_to_html_guideline(guideline: str, choices: List[List[str]]) -> str:
            """ Generates the html of the guidelines with the border on the background of the words that
            have the index of word_indexs_list """

            word_indexs_list = index_words(guideline, choices)

            html_output = ""
            indice = 0

            html_output += "<span class='block'>"

            words_list = guideline.split(" ")

            for i, word in enumerate(words_list):
                if word_indexs_list and i == word_indexs_list[0][0]:

                    html_output += "<span class='framed'>"

                html_output += f"<span class='word'>{word}</span>"
                if word_indexs_list and i == word_indexs_list[0][1]:
                    del word_indexs_list[0]
                    indice += 1
                    html_output += "</span>"

                html_output += "<span class='space'> </span>"

            html_output += "<br/></span>"

            return html_output

        # we get the data from json
        filler = self.FILL_SYMBOL
        non_separators = self.NON_SEPARATORS
        repl_symbol = self.REPLACING_SYMBOL
        guideline = self.adapt_guideline()
        additional_guideline = "".join(
            self.find_additional_guideline()
        )  # find additional guideline returns a tuple
        lines_to_display, choices_to_display = self.prepare_to_display()
        # we html mark the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline], False)
        choices = self.choices.copy()
        # conversion of the aditionnal guideline with the display of the choices in
        # it if possible ||
        #                \/
        if len(choices) == 1:
            if additional_guideline:
                additional_guideline = __text_to_html_guideline(
                    additional_guideline, choices[0]
                )
            else:
                choices_input = final_clean_choices(choices, non_separators, repl_symbol)
                choices_copy = choices_input.copy()
                choices_copy[-1] = "ou " + choices_copy[-1]
                additional_guideline = __text_to_html_guideline(
                    " ".join(choices_copy), choices_input
                )
        else:
            additional_guideline = (
                text_to_html([additional_guideline], False)
                if additional_guideline
                else ""
            )  # we want it to be empty if there is no additional guideline
        exercise_text = text_to_html(
            lines_to_display, True
        )  # html string of exercise_text
        html_choices = choices_to_html(
            choices_to_display
        )  # list html string of tables of choices
        pattern_span_fill = re.compile(
            fr"<span class='word'>([^<>]*{filler}[^<>]*)</span>"
        )
        # we need to add the button to show the choices at the right places
        # however there may be several choices in the same line so we need
        # to go through the lines to look for the fill chars and add the right
        # index of each fill char (role of pos_char)
        pos_char = 0
        start = 0
        new_sentences = ""
        for match in pattern_span_fill.finditer(exercise_text):
            pieces = re.split(re.escape(filler), match[1])
            number_of_pieces = len(pieces)
            span_fill_word = match.span()
            piece_text = exercise_text[start : span_fill_word[0]]
            start = span_fill_word[1]
            link_string = "<span class='word'>"
            for i, piece in enumerate(pieces):
                if piece:
                    link_string += piece
                if i != number_of_pieces - 1:
                    link_string += f'<button class="mc_button" id="mc_button_{pos_char}" \
                                    id_mc_menu="mc_menu_{pos_char}" \
                                    onclick="myFunction(this)">{filler}</button>'
                    pos_char += 1
            link_string += "</span>"
            new_sentences += piece_text + link_string
        new_sentences += exercise_text[start:]
        new_sentences += "\n".join(html_choices)
        self.html_output = self.html_template.render(
            exercise_number=self.json_path.split(os.sep)[-1].split(".")[0],
            exercise_text=new_sentences,
            additional_guideline=additional_guideline,
            guideline=guideline,
            lines_per_page=self.lines_per_page,
        )
        return self.html_output


    def adapt(self):
        """Adapts the exercise (to do after loading its JSON content)"""
        self.find_choices()
        self.convert_to_html()
        return None
