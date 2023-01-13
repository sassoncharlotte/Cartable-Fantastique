from configparser import ConfigParser

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import text_to_html


class ExpressionEcrite(Fill):
    """exercises consisting of just box to fill with text"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="expression_ecrite",
        )

    def convert_to_html(self):
        """get the raw text and output an html version of it"""

        # we get the data from json
        guideline = super().find_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        # list of sentences from exercise_text
        sentences = super().find_sentences()

        # when there are nothing in the exercise, it may leave an empty space that we remove
        if len(sentences) == 1:
            sentences = ["…"]
        else:
            sentences.append("…")

        # we conver to html the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guideline
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        sentences = text_to_html(sentences, True)

        return guideline, additional_guideline, sentences, {}

    def adapt(self):
        """specific adapatation for expression ecrite"""
        super().adapt_html({"…": "<span contenteditable='true'> </span>"})
        return self
