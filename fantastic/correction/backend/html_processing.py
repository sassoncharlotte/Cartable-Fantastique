import re
import os
import pandas as pd
from transformers.pipelines.token_classification import TokenClassificationPipeline
from spacy.lang.fr import French
import fantastic.paths
from fantastic.correction.backend.convert import (
    generate_conversion_from_tag,
    convert_type_to_class_name,
)


def generate_html(
    file_treatment_infos: pd.DataFrame,
    id_exercise: str,
    nlp_token_class: French,
    nlp: TokenClassificationPipeline,
):
    """Generates the html of the exercise of id_exercise given the latest operations stored
    in the treatment_infos file"""
    type_exercise = file_treatment_infos.loc[id_exercise].at["exercise_type"]
    type_conversion = file_treatment_infos.loc[id_exercise].at["conversion_type"]
    if type_exercise == type_conversion:
        return open_html(file_treatment_infos, id_exercise)
    else:
        return generate_conversion_from_tag(
            id_exercise,
            convert_type_to_class_name(type_conversion),
            nlp_token_class,
            nlp,
        )


def open_html(file_treatment_infos: pd.DataFrame, id_exercise: str):
    """Open the html of the given exercise from the output directory"""
    exercise_type = file_treatment_infos.loc[id_exercise].at["exercise_type"]
    html_path = f"{fantastic.paths.OUTPUT_DIR}/{exercise_type}/{id_exercise}.html"
    with open(html_path, "r", encoding="UTF-8") as html_file:
        html_output = html_file.read()
    return html_output


def head_body_html(html_output: str):
    """
    returns as strings the head and the body of a string representing a html file
    """
    head = re.search(r"<head>(.+)</head>", html_output, flags=re.DOTALL)
    if head:
        head = replace_paths_by_folder_path(head[1])
    else:
        head = ""
    body = re.search(r"<body>(.+)</body>", html_output, flags=re.DOTALL)
    if body:
        body = replace_paths_by_folder_path(body[1])
    else:
        body = ""
    return head, body


def replace_paths_by_folder_path(html_content: str):
    """
    Adapts the paths of the scripts of the html to match the
    corresponding exported scripts versions by the application
    (exported at "./static/")
    """
    html_content = re.sub(r"\.\./css/", "/static/css/", html_content)
    html_content_cleaned = re.sub(r"\.\./js/", "/static/js/", html_content)
    return html_content_cleaned


def generate_select_tags(class_name_dict: dict, current: str = None):
    """
    Generate the options of the <select> html for the exercises tags.
    It sets each time the current tag of the exercise displayed as the
    default choice in the select bar
    """
    html_tags = ""
    for tag in class_name_dict.keys():
        if current == tag:
            html_tags += f'<option value={tag} selected="selected">{tag}</option>'
        else:
            html_tags += f"<option value={tag}>{tag}</option>"
    return html_tags


def format_most_likely_tags(top_categories: dict):
    """Returns the max_tags_to_display best predicted tags as a displayable string"""
    max_tags_to_display = 3
    to_display = ""
    count = 0
    for tag, prob in sorted(top_categories.items(), key=lambda item:item[1], reverse=True):
        if count < max_tags_to_display:
            to_display += f"{tag}: {round(100*prob,1)}%  "
        count += 1
    return to_display

def open_xml(id_exercise: str):
    """Returns the XML of the exercise with id_exercise as a string"""
    xml_path = os.path.join(fantastic.paths.XML_DIR, id_exercise + ".xml")
    with open(xml_path, "r", encoding="utf-8") as xml_file:
        xml_output = xml_file.read()
    return xml_output

def prepare_xml_to_display_html(xml_output: str):
    """Returns an HTML version of the XML file to display"""
    xml_to_display = re.sub(r"<", "&lt", xml_output)
    xml_to_display = re.sub(r">", "&gt", xml_to_display)
    xml_to_display = f"<textarea readonly>{xml_to_display}</textarea>"
    return xml_to_display
