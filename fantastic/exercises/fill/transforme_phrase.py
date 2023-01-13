import re
import json
from configparser import ConfigParser

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import text_to_html, have_symbol


class TransformePhrase(Fill):
    """exercises consisting of sentences that should be entirely transformed
    thus showing an editable box for each sentence"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="transforme_phrase",
        )
        self.long_list_separators: list = json.loads(
            self.config.get("transforme_phrase", "long_list_separators")
        )

    def convert_to_html(self):
        """get the raw text and output an html version of it"""
        # we get the data from json
        guideline = super().find_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        sentences = super().find_sentences()

        have_long_list_separators = [
            have_symbol(sentences, lls) for lls in self.long_list_separators
        ]
        if any(have_long_list_separators):
            lls = self.long_list_separators[have_long_list_separators.index(True)]
            regex_to_find_lls = "^(\w\W\s*){1,}\s|" + lls
        else:
            regex_to_find_lls = "^(\w\W\s*){1,}\s"

        # we add an editable part to each sentence
        if any(list(map(lambda s: re.search(regex_to_find_lls, s), sentences))):
            # we have a. and b. or a ◆
            sentences = list(map(lambda s: s + "<br> ➞ …", sentences))

        else:
            # plain text
            if len(sentences) > 0:
                sentences[-1] += "<br> ➞ …"

        # we convert to html the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guideline
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        sentences = text_to_html(sentences, True)

        return guideline, additional_guideline, sentences, None

    def adapt(self):
        """specific adaptation for this type of exercise"""
        super().adapt_html({"…": "<span contenteditable='true'> </span>"})
        return self
