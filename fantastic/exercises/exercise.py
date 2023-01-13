from configparser import ConfigParser
import json
import os
from jinja2 import Environment, FileSystemLoader
import fantastic.paths
from fantastic.exercises.utils import find_all_sentences, find_in_dict






class Exercise:
    """
    Class attributes:
        json_path (str): The path of the json of the exercise
        config (ConfigParser): An object containing the variables stored in a .cfg file
        (must always be data.cfg if all variables in it)
        template_name (str): The name of the template jinja to use to generate the html
        output_folder_name: (str) : A string representing the name of the subfolder of the
        output folder in which to store the exercise (same value for the same Child type)
        (ex: ChoixMultiples --> choix_multiples)
        lines_per_page: (int): the lines to display per page in the html
    """

    def __init__(
            self,
            json_path: str,
            config: ConfigParser,
            template_name: str = "",
            output_folder_name: str = "",
            lines_per_page: int = 3
        ) -> None:
        self.json_path = json_path
        self.json = {}
        self.template_name = template_name
        self.output_folder_name = output_folder_name
        self.html_template = ""
        self.html_output = ""
        self.lines_per_page = lines_per_page
        self.config = config

    def load_json(self):
        """loads the json of the exercise and stores it in the attribute json"""
        with open(self.json_path, 'r', encoding='UTF-8') as json_file:
            self.json = json.load(json_file)
        return self

    def create_template(self):
        """create the template to fill to generate the html in the output of the conversion"""
        env = Environment(loader = FileSystemLoader(fantastic.paths.TEMPLATE_DIR)) # loading the jinja templates
        self.html_template = env.get_template(self.template_name + ".html") # loading the specific html template
        return self

    def write_template(self) -> None: # writing the template to the html and css files
        """Stores the completed template in a html file in the output folder"""
        filename = self.json_path.split(os.sep)[-1].split('.')[0]
        with open(os.path.join(fantastic.paths.OUTPUT_DIR,\
            self.output_folder_name, filename + ".html"), 'w', encoding='utf-8') as file:
            file.write(self.html_output)

    def find_exercise(self):
        """Returns the whole exercise in a dict"""
        return find_in_dict(self.json, dict, "exercice")

    def find_guideline(self):
        """Returns the guideline in a string"""
        return find_in_dict(self.find_exercise(), str, "consigne")

    def find_exercise_text(self):
        """Returns the exercise text either as a string or a dict """
        dict_found = find_in_dict(self.find_exercise(), dict, "enonce")
        if not dict_found:
            return find_in_dict(self.find_exercise(), str, "enonce")
        return dict_found

    def find_additional_guideline(self):
        """
        Returns the additionnal guideline in a tuple of strings
        (Due to the fact that tha additionnal guideline can be in two
        different places)
        """
        notesc_try = find_in_dict(self.find_exercise(), str, "noteSC")
        text_try = find_in_dict(self.find_exercise_text(), str, "#text")
        return notesc_try, text_try

    def find_sentences(self):
        """
        Returns the full sentences composing the exercise_text in a list
        (full sentence = finished by .,!,? or » and followed by a Capital letter)
        """
        exercise_text = self.find_exercise_text()
        if isinstance(exercise_text, dict):
            ol_case = find_in_dict(self.find_exercise_text(),dict, "ol")
            if ol_case:
                return find_in_dict(ol_case, list, "li")
            return []
        return find_all_sentences(exercise_text)

    def find_remaining(self):
        """
        Returns the remaining content of the exercise
        """
        exercise = self.find_exercise()
        return find_in_dict(exercise, str, "rest")
    