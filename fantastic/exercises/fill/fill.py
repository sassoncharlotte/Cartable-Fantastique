import os
import json

from configparser import ConfigParser

from fantastic.exercises.exercise import Exercise
from fantastic.exercises.utils import text_to_html


class Fill(Exercise):
    """parent class of categories:
    RC, RCCadre, RCDouble, RCImage, EditPhrase, TransformePhrase, TransformeMot, ExpressionEcrite"""

    def __init__(
        self,
        json_path: str,
        config: ConfigParser,
        lines_per_page: int = 3,
        template_name: str = "",
        output_folder_name: str = "",
    ) -> None:
        Exercise.__init__(
            self, json_path, config, template_name, output_folder_name, lines_per_page
        )
        self.upstream_replacement: dict = json.loads(
            self.config.get("fill", "upstream_replacement")
        )

    def convert_to_html(self):
        """get the raw text and output an html version of it"""

        # we get the data from json
        guideline = super().find_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        sentences = super().find_sentences()

        # we convert to html the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guidelines
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        sentences = text_to_html(sentences, True)

        # None is replacement dict
        return guideline, additional_guideline, sentences, None

    def adapt_html(self, replacement: dict = None) -> None:
        """modify html to correctly handle specific graphical elements of that exercise type"""

        # we do not want mutable default arguments
        upstream_replacement = (
            self.upstream_replacement if replacement is None else replacement
        )

        # downstream replacement as it is sent by convert_to_html
        (
            guideline,
            additional_guideline,
            exercise_text,
            downstream_replacement,
        ) = self.convert_to_html()
        downstream_replacement = (
            {} if downstream_replacement is None else downstream_replacement
        )

        replacement = dict(
            downstream_replacement, **upstream_replacement
        )  # merge two dicts

        for filler, replacer in replacement.items():
            exercise_text = exercise_text.replace(filler, replacer)

        self.html_output = self.html_template.render(
            ex_nb=self.json_path.split(os.sep)[-1].split(".")[0],
            exercise_text="".join(exercise_text),
            additional_guideline=additional_guideline,
            guideline=guideline,
            lines_per_page=self.lines_per_page,
        )
