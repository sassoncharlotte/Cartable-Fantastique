import json

import re
from configparser import ConfigParser

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import have_symbol, text_to_html


class RemplirClavier(Fill):
    """exercises consisting of usually … to replace with an editable content"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="remplir_clavier",
        )
        self.list_break_separators: list = json.loads(
            self.config.get("remplir_clavier", "list_break_separators")
        )
        self.long_list_separators: list = json.loads(
            self.config.get("remplir_clavier", "long_list_separators")
        )
        self.fillers: list = json.loads(self.config.get("remplir_clavier", "fillers"))
        self.trash: list = json.loads(self.config.get("remplir_clavier", "trash"))

    def convert_to_html(self):
        """get the raw text and output an html version of it"""

        # we get the data from json
        guideline = super().find_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        # list of sentences from exercise_text
        sentences = super().find_sentences()

        # we add an editable part to each sentence

        # getting condition on long list separators
        have_long_list_separators = [
            have_symbol(sentences, lls) for lls in self.long_list_separators
        ]

        if any(list(map(lambda s: re.search(r"^(\w\W\s*){1,}\s", s), sentences))):
            # we have a. and b.

            # we replace list break separator, essentially "◆"
            for list_break_separator in self.list_break_separators:
                sentences = list(
                    map(
                        lambda s, lbs=list_break_separator: s.replace(lbs, "<br>"),
                        sentences,
                    )
                )

        elif any(have_long_list_separators):
            # list of lls, lls='◆' usually
            lls = self.long_list_separators[have_long_list_separators.index(True)]

            # each insecable block is in fact separated by ◆
            splitted_sentences = sentences[0].split(lls)
            splitted_sentences = list(
                map(lambda s: s.strip() + " ", splitted_sentences)
            )
            # there is a missing space at the end of sentence
            splitted_sentences[-1] += " "
            # the split on ◆ removed them
            splitted_sentences = list(map(lambda s: s + lls, splitted_sentences))
            sentences = splitted_sentences

        else:
            # plain text
            pass

        # we convert to html the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guideline
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        sentences = text_to_html(sentences, True)

        return guideline, additional_guideline, sentences, None

    def adapt(self):
        """specific adapatation for RC"""

        replacement_dict = {}
        for filler in self.fillers:
            replacement_dict[filler] = "<span contenteditable='true'> </span>"
        for to_delete in self.trash:
            replacement_dict[to_delete] = ""

        super().adapt_html(replacement_dict)

        return self
