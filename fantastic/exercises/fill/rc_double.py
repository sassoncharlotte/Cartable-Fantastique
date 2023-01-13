import re
import json
from configparser import ConfigParser
from uuid import uuid4

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import text_to_html, have_symbol


class RemplirClavierDouble(Fill):
    """exercises where sentences are rewrite with an editable part"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="remplir_clavier_double",
        )
        self.long_list_separators = json.loads(
            self.config.get("rc_double", "long_list_separators")
        )

    def adapt_guideline(self):
        """should adapt the guideline for some exercises"""

        guideline = super().find_guideline()
        guideline = guideline = guideline.replace("en gras", "en jaune")

        return guideline

    def convert_to_html(self):
        """get the raw text and output an html version of it"""

        # we get the data from json
        guideline = self.adapt_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        # list of sentences from exercise_text
        sentences = super().find_sentences()

        have_long_list_separators = [
            have_symbol(sentences, lls) for lls in self.long_list_separators
        ]

        if any(list(map(lambda s: re.search(r"^(\w\W\s*){1,}\s", s), sentences))):
            # we have a. and b.

            sentences = list(map(lambda s: s.replace("◆", "<br>"), sentences))

        elif any(have_long_list_separators):
            # list of lls
            lls = self.long_list_separators[have_long_list_separators.index(True)]

            # each insecable block is in fact separated by ◆
            splitted_sentences = sentences[0].split(lls)
            splitted_sentences = list(map(lambda s: s.strip(), splitted_sentences))
            # there is a missing space at the end of sentence
            splitted_sentences[-1] += " "
            # the split on ◆ removed them
            splitted_sentences = list(map(lambda s: s + lls, splitted_sentences))
            sentences = splitted_sentences

        else:
            # plain text
            pass

        # we add the editable part
        # text to html convert each word, but we need to manke changes before text to html
        # so we need to encapsulate what we want to give to the fill box in only one word : hex hash
        # replacement dict contains all change to be made after the conversion to html
        replacement, sentences_with_hash = ({}, [])
        for sentence in sentences:
            # we generate an unique id for the sentence, that we will not found in the text
            # because after the conversion to html, we'll replace the unique id by html code

            # looking at what's in bold
            bold_regex = r"\#gras\#(.+?)\#\/gras\#"
            regex_result = re.findall(bold_regex, sentence)
            # the nb of modifications to make is the number of things in bold
            nb_special_words = len(regex_result)

            # we go at least once in the loop
            for _ in range(max(1, nb_special_words)):
                first_id = uuid4().hex
                second_id = uuid4().hex
                third_id = uuid4().hex
                fourth_id = uuid4().hex

                cleaned_sentence = sentence.replace("#gras#", str(first_id), 1)
                cleaned_sentence = cleaned_sentence.replace(
                    "#/gras#", str(second_id), 1
                )

                hashed_sentence = sentence.replace("#gras#", str(third_id), 1)
                hashed_sentence = hashed_sentence.replace("#/gras#", str(fourth_id), 1)

                replacement[
                    str(first_id)
                ] = "<span class='framed' style='background-color:yellow'>"
                replacement[str(second_id)] = "</span>"
                replacement[str(third_id)] = "<span contenteditable='true'>"
                replacement[str(fourth_id)] = "</span>"

            sentences_with_hash.append(cleaned_sentence + "<br> ➞ " + hashed_sentence)

        # we conver to html the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guideline
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        sentences = text_to_html(sentences_with_hash, True)

        return guideline, additional_guideline, sentences, replacement

    def adapt(self):
        """specific adapatation for rc double"""
        super().adapt_html({"◆": " \n"})
        return self
