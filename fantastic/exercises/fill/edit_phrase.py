import re
from configparser import ConfigParser
from uuid import uuid4

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import text_to_html


class EditPhrase(Fill):
    """exercices consisting of sentences to change (on another line)"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="edit_phrase",
        )

    def convert_to_html(self):
        """get the raw text and output an html version of it readty to be adapted"""
        # we get the data from json
        guideline = super().find_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        # list of sentences from exercise_text
        sentences = super().find_sentences()

        # text to html convert each word, but we need to manke changes before text to html
        # so we need to encapsulate what we want to give to the fill box in only one word : hex hash
        # replacement dict contains all change to be made after the conversion to html
        replacement, sentences_with_hash = ({}, [])
        for sentence in sentences:
            # we generate an unique id for the sentence, that we will not found in the text
            # because after the conversion to html, we'll replace the unique id by html code
            sentence_id = uuid4().hex
            # removing the a. and others b.
            editable_part = re.sub(r"^(\w\W\s*){1,}\s", "", sentence, 1)
            # removing the (indication)
            editable_part = re.sub(r"\((.+?)\)", "", editable_part)

            replacement[
                str(sentence_id)
            ] = f"<span contenteditable='true'>{editable_part}</span>"
            sentences_with_hash.append(sentence + "<br> ➞ " + str(sentence_id))

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
        super().adapt_html({"…": "<span contenteditable='true'> </span>"})
        return self
