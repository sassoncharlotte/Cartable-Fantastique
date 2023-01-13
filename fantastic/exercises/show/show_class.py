import os
from configparser import ConfigParser
from fantastic.exercises.exercise import Exercise
from fantastic.exercises.utils import text_to_html


class Show(Exercise):
    """See Exercise class documentation to understand the different parameters"""
    def __init__(
        self,
        json_path: str,
        config: ConfigParser,
        template_name: str = "show",
        output_folder_name: str = "",
        lines_per_page: int = 3,
    ) -> None:
        super().__init__(
            json_path, config, template_name, output_folder_name, lines_per_page
        )

    def adapt_guideline(self):
        """adapts the guideline to the html format"""
        return self.find_guideline()

    def convert_to_html(self):
        """Converts the exercise content after processing to a string with the html format"""
        # we get the data from json
        guideline = self.find_guideline()
        additional_guideline = "".join(
            self.find_additional_guideline()
        )  # find additional guideline returns a tuple
        sentences = self.find_sentences()
        # we html mark the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline], False)
        additional_guideline = (
            text_to_html([additional_guideline], False)
            if additional_guideline != ""
            else ""
        )  # we want it to be empty if there are no additional guideline
        exercise_text = text_to_html(sentences, True)
        self.html_output = self.html_template.render(
            exercise_number=self.json_path.split(os.sep)[-1].split(".")[0],
            exercise_text=exercise_text,
            additional_guideline=additional_guideline,
            guideline=guideline,
            lines_per_page=self.lines_per_page,
        )
        return self

    def adapt(self) -> None:
        """adapts the content of the json to an html version to display on a navigator"""
        self.convert_to_html()
