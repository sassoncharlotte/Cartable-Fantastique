from configparser import ConfigParser
import string
import json
from typing import Tuple
from nltk.stem.snowball import FrenchStemmer
from nltk import word_tokenize
from fantastic.exercises.select.entities_groupe_mots import EntitiesGroupeMots
from fantastic.exercises.select.entities_phrases import EntitiesPhrases
from fantastic.exercises.select.entities_mots import EntitiesMots
from fantastic.exercises.utils import (
    find_in_dict,
    splits_to_sentences,
    clean_entities_spaces,
    split_word,
    entities_if_symbols,
)
from fantastic.exercises.choose.explore_guideline import find_choices_in_guideline


class Classe(EntitiesMots, EntitiesPhrases, EntitiesGroupeMots):
    """Class to adapt Classe exercices"""

    output_folder_name: str = "classe"

    def __init__(self, path: str, config: ConfigParser) -> None:
        EntitiesGroupeMots.__init__(self, path, config)
        EntitiesPhrases.__init__(self, path, config)
        EntitiesMots.__init__(self, path, config)
        self.split_characters = self.config.get("classe", "split_characters").strip('"') + string.punctuation
        self.stemmed_verbs_to_replace = json.loads(self.config.get("classe","stemmed_verbs_to_replace"))
        self.verb_to_put = self.config.get("classe", "verb_to_put").strip('"')
        self.useless_noun_groups = json.loads(self.config.get("classe","useless_noun_groups"))
        self.guideline_separators = json.loads(config.get("classe", "guideline_separators"))
        self.end_last_choice_patterns = json.loads(config.get("classe", "end_last_choice_patterns"))

    def find_categories(self):
        """Returns the content of the tag "categories" that needs to be added to the xmls"""
        return find_in_dict(self.find_exercise(), str, "categories")


    def adapt_guideline(self, guideline: str) -> str:
        """Adapts the guideline adding the categories, the frames and the colors
        and replacing the verb with "colorie de la bonne couleur"."""

        # removing all the useless phrases of the guideline
        for useless_noun_group in self.useless_noun_groups:
            guideline = guideline.replace(useless_noun_group, "")

        adapted_guideline = guideline

        color_id = 0
        stemmer = FrenchStemmer()
        guideline_list = word_tokenize(adapted_guideline, language="french")

        for word in guideline_list:

            # taking the radical of the word
            stemmed_word = stemmer.stem(word)

            if stemmed_word in self.stemmed_verbs_to_replace:
                # word is a verb that we replace with "colorie"
                adapted_guideline = adapted_guideline.replace(word, self.verb_to_put)
                color_id += 1

        adapted_guideline_list = splits_to_sentences(adapted_guideline)
        adapted_guideline_list = clean_entities_spaces(adapted_guideline_list)

        for sentence in adapted_guideline_list:

            # capitalizing the sentences
            # .capitalize lowers every letter except the first one, sometimes we don't want that
            if len(sentence) > 1:
                new_sentence = sentence[0].upper() + sentence[1:]
            else:
                new_sentence = sentence[0].upper()

            adapted_guideline = adapted_guideline.replace(sentence, new_sentence)

        # adding the categories at the end of the guideline
        adapted_guideline = self.categories_added_guideline(adapted_guideline)

        return adapted_guideline

    def categories_added_guideline(self, guideline: str) -> str:
        """Adds a double dots at the end of the guideline followed by the categories to identify

        Parameters:
        guideline
        Returns:
        corrected guideline"""

        # finds the categories in the guideline
        categories = find_choices_in_guideline(guideline, self.guideline_separators, self.end_last_choice_patterns)
        end_guideline = ""

        if not categories:
            # the categories aren't in the guideline
            # than, they should be in the tag "categories"
            categories = self.find_categories()

            if categories:
                categories_list = splits_to_sentences(categories)
                categories_list = clean_entities_spaces(categories_list)

                for category in categories_list:
                    if len(category) > 1:
                        # cleaning the category
                        end_guideline += category[0].lower() + category[1:-1] + " "

                guideline = guideline[:-1] + " : " + end_guideline[:-1] + "."
        return guideline

    def colors_to_display(self) -> Tuple[int, dict]:
        """Calculates the number of colors to display according
        to the number of categories.

        Returns:
        - the number of colors to display
        - displayed_colors_dict: the dictionary of the colors to display"""

        _, displayed_colors_dict = self.determine_number_of_colors()
        number_of_colors = 1
        categories = self.get_categories_in_guideline()
        number_of_colors = len(categories)
        return max(number_of_colors, 2), displayed_colors_dict


    def get_categories_in_guideline(self) -> list:
        """Returns the list of categories that we need to color and frame in the guideline."""

        # getting the guideline
        guideline = self.find_guideline()

        # finding the categories in the guideline
        categories = find_choices_in_guideline(guideline, self.guideline_separators, self.end_last_choice_patterns)

        if not categories:
            # the categories aren't in the guideline
            # we find them in the tag "categories"
            categories = self.find_categories()

            if categories:
                # splitting to sentences and removing spaces at the end / begginning

                categories_guideline = []

                categories = splits_to_sentences(categories)
                categories = clean_entities_spaces(categories)

                for category in categories:
                    if len(category) > 1:
                        category = category[0].lower() + category[1:-1]
                    categories_guideline += [category]
                return categories_guideline
            return []

        return categories[0]


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

        guideline = self.find_guideline()

        if "phrase" in guideline:
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

        elif words_list == []:
            # the entities are words, punctuation, apostrophes...
            words_list = text.split(" ")

            words_list = clean_entities_spaces(words_list)

            # separating the word from the punctuation and the accents
            new_words_list = []
            for word in words_list:
                new_words_list += split_word(word, self.split_characters)

            # unifying the numbers
            for i in range(len(words_list)):
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

            # getting the right path to js script
            self.js_script_path = EntitiesMots.js_script_path

            # convertion to html
            html_output, word_id_count, entity_id_count = self.text_to_html_coche_mots(
                words_list, html_output, word_id_count, entity_id_count
            )

        else:
            # the entities are groups of words

            # getting the right path to js script
            self.js_script_path = EntitiesGroupeMots.js_script_path
            self.lines_per_page = 1
            words_list = clean_entities_spaces(words_list)

            # convertion to html
            html_output, word_id_count, entity_id_count = self.text_to_html_groupe_mots(
                words_list, html_output, word_id_count, entity_id_count
            )

        return html_output, word_id_count, entity_id_count
