import re

from configparser import ConfigParser
from uuid import uuid4

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import text_to_html


class RemplirClavierCadre(Fill):
    """exercises consisting of finding verbes between parenthesis
    and adding a frame above the sentence with the verb"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="remplir_clavier_cadre",
        )

    def adapt_guideline(self):
        """should adapt the guideline for some exercises"""

        guideline = super().find_guideline()
        guideline = guideline = guideline.replace("entre parenthèses ", "")
        guideline = guideline.replace(" entre parenthèses", "")

        return guideline

    def convert_to_html(self):
        """get the raw text and output an html version of it readty to be adapted"""

        # we get the data from json
        guideline = self.adapt_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        # list of sentences from exercise_text
        sentences = super().find_sentences()

        # text to html convert each word, but we need to manke changes before text to html
        # so we need to encapsulate what we want to give to the fill box in only one word : hex hash
        # replacement dict contains all change to be made after the conversion to html
        replacement, sentences_with_hash = ({}, [])
        for sentence in sentences:
            # we initialize sentence_id in case of bad extracted xml
            sentence_id = 0
            # getting the verbs
            verbs = re.findall(r"\(.+?\)", sentence)
            sentence_with_hash = ""
            sentence_without_verb = sentence

            for verb in verbs:
                # verb contains parenthesis
                sentence_without_verb = sentence_without_verb.replace(f"{verb}", "…")

                # we generate an unique id for the sentence, that we will not found in the text
                # because after the conversion to html, we'll replace the unique id by html code
                sentence_id = uuid4().hex
                replacement[
                    str(sentence_id)
                ] = f"<span class='framed'>{verb[1:-1]}</span>"
                sentence_with_hash += str(sentence_id) + " "

            if sentence_id == 0:
                # no verb found
                sentences_with_hash.append(sentence)
            else:
                # verb found
                sentences_with_hash.append(
                    sentence_with_hash + "<br> " + sentence_without_verb
                )

        # we conver to html the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guideline
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        exercise_text = text_to_html(sentences_with_hash, True)

        return guideline, additional_guideline, exercise_text, replacement

    def adapt(self):
        """specific adaptation for this type of exercise"""
        super().adapt_html()
        return self
