import os
import pandas as pd

from fastapi import FastAPI, Form, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

import fantastic.paths
from fantastic.correction.backend.convert import (
    convert_type_to_class_name,
    CLASS_NAME_DICT,
    convert_class_name_to_type,
)
from fantastic.correction.backend.store import (
    generate_correction_output_folders,
    retrieve_css_and_js_files,
    store_in_corresponding_folder,
    remove_latest_treatment,
)
from fantastic.correction.backend.html_processing import (
    format_most_likely_tags,
    generate_html,
    generate_select_tags,
    head_body_html,
    open_xml,
    prepare_xml_to_display_html
)
from fantastic.correction.backend.tag_prediction import get_most_likely_tags, load_tagging_model
from fantastic.correction.app_init import export_to_csv
from fantastic.exercises.utils import generate_nlp_gilf, generate_nlp_spacy

# file_treatment_infos: A pd.DataFrame in which the latest operations through the correction interface are registered
# It allows to keep track of operations on next use and to access more easily to some files
file_treatment_infos = pd.read_csv(
    os.path.join(fantastic.paths.CORRECTION_DIR, "file_treatment_infos.csv"),
    converters={"category_path": str},
).set_index("id_exercise")
env = Environment(
    loader=FileSystemLoader(os.path.join(fantastic.paths.CORRECTION_DIR, "templates"))
)

HTML_CORRECTION_TEMPLATE = env.get_template("correction.html")
# CORRECTION_FEATURES: List of all features available as a classification treatment
# (hence resulting as a stored file in a correction folder)
CORRECTION_FEATURES = ["well_converted", "incorrectly_converted", "incorrectly_extracted"]
NUMBER_FEATURES = len(CORRECTION_FEATURES)
# APP_POST_FEATURES: The corresponding treatments sent by the post request in the parameter "action"
# First part should correspond to all classification treatments
# (hence bijection with CORRECTION_FEATURES with the same indexes !ORDER COUNTS!)
APP_POST_FEATURES = ["bonne conversion", "mauvaise conversion", "mauvaise extraction"] + \
["générer avec nouveau tag", "prédire le tag", "afficher le xml", "afficher le html"]
# CORRECTION_OUTPUT_DIRECTORY: The correction directory where files are classified
# and stored in from the correction interface
CORRECTION_OUTPUT_DIRECTORY = fantastic.paths.DATA_DIR
INDEX_EXERCISES = file_treatment_infos.index


# All the ML models are loaded before starting the application to do it only once
# (Too long to load otherwise)
nlp_token_class = generate_nlp_gilf()
nlp = generate_nlp_spacy()
tagging_model = load_tagging_model()


def find_successor_in_index(index_df: pd.Index, current: str):
    """
    Finds the successor of the current index in a pd.Index object
    (current could be in reality of any type as long as it is in the index)
    """
    number_indexes = len(index_df)
    index_int = index_df.get_loc(current)
    if index_int < number_indexes - 1:
        return index_df[index_int + 1]
    else:
        return index_df[0]


def find_predecessor_in_index(index_df: pd.Index, current: str):
    """
    Finds the predecessor of the current index in a pd.Index object
    (current could be in reality of any type as long as it is in the index)
    """
    number_indexes = len(index_df)
    index_int = index_df.get_loc(current)
    if index_int > 0:
        return index_df[index_int - 1]
    else:
        return index_df[number_indexes - 1]


app = FastAPI()
# Static files exported in the static folder of the application instance
app.mount(
    "/static", StaticFiles(directory=os.path.join(fantastic.paths.FANTASTIC_DIR, "correction", "static")), name="static"
)


@app.get("/", response_class=HTMLResponse)
def show_info():
    return "<p> Lancer localhost:port/correction/{id_exercise} pour afficher un exercice\n\
                Exemple: localhost:port/correction/17_9</p>"


@app.on_event("startup")
def startup_event():
    """Generates the correction output folder and its subfolders and retrieves
    the latest versions of css and js files when starting the application"""
    generate_correction_output_folders(
        fantastic.paths.OUTPUT_DIR, CORRECTION_OUTPUT_DIRECTORY, CORRECTION_FEATURES
    )
    retrieve_css_and_js_files(
        fantastic.paths.OUTPUT_DIR,
        os.path.join(fantastic.paths.FANTASTIC_DIR, "correction", "static"),
    )


@app.on_event("shutdown")
def shutdown_event():
    """Stores the latest operations of storage and conversion done for next use"""
    export_to_csv(file_treatment_infos, fantastic.paths.CORRECTION_DIR)


@app.get("/correction/{id_exercise}", response_class=HTMLResponse)
def get_html_content(*, id_exercise: str = Path(..., regex=r"^\d{1,4}_\d{1,2}")):
    """Displays the exercise with id_exercise in the navigator"""
    conversion_type = file_treatment_infos.loc[id_exercise].at["exercise_type"]
    file_treatment_infos.at[id_exercise, "conversion_type"] = conversion_type  # reset conversion type to original type
    html_output = generate_html(file_treatment_infos, id_exercise, nlp_token_class, nlp)
    head, body = head_body_html(html_output)
    html_tags = generate_select_tags(CLASS_NAME_DICT, convert_type_to_class_name(conversion_type))
    successor = find_successor_in_index(INDEX_EXERCISES, id_exercise)
    predecessor = find_predecessor_in_index(INDEX_EXERCISES, id_exercise)
    return HTML_CORRECTION_TEMPLATE.render(
        head=head,
        body=body,
        tags=html_tags,
        to_show="Afficher le XML",
        result="",
        successor=successor,
        predecessor=predecessor,
    )


@app.post("/correction/{id_exercise}", response_class=HTMLResponse)
def form_post(
    *,
    id_exercise: str = Path(..., regex=r"^\d{1,4}_\d{1,2}"),
    new_tag: str = Form(None),
    action: str = Form(...)
):
    """
    Does the operations requested when pressing buttons or bind keys

    Parameters:
        id_exercise (str): The id of the exercise to correct
        new_tag (str): the new tag to convert the exercise to (ex: tag = "VraiFaux")
        action (str): The action to do (ex: "Bonne Conversion")
    """
    result = ""
    index_action = APP_POST_FEATURES.index(action.lower())

    if index_action < NUMBER_FEATURES:  # classification cases = same treatment
        html_output = generate_html(file_treatment_infos, id_exercise, nlp_token_class, nlp)
        type_exercise = file_treatment_infos.loc[id_exercise].at["conversion_type"]  # latest conversion type
        category_correction = CORRECTION_FEATURES[index_action]  # class of correction selected by user
        remove_latest_treatment(file_treatment_infos, CORRECTION_OUTPUT_DIRECTORY, id_exercise, category_correction)
        store_in_corresponding_folder(
            html_output,
            os.path.join(CORRECTION_OUTPUT_DIRECTORY, "correction_output"),
            CORRECTION_FEATURES,
            index_action,
            type_exercise,
            id_exercise,
        )
        file_treatment_infos.at[id_exercise, "category_path"] = os.path.join(category_correction, type_exercise)  # store new treatment
        result = "Fichier enregistré en tant que " + action.lower() +"!"
    elif index_action == NUMBER_FEATURES:  # new tag case = other treatment
        file_treatment_infos.at[id_exercise, "conversion_type"] = convert_class_name_to_type(new_tag)  # store new conversion type
        html_output = generate_html(file_treatment_infos, id_exercise, nlp_token_class, nlp)
    elif index_action == NUMBER_FEATURES + 1: # prediction case
        top_categories = get_most_likely_tags(tagging_model, id_exercise)
        result = format_most_likely_tags(top_categories)
        html_output = generate_html(file_treatment_infos, id_exercise, nlp_token_class, nlp)
    elif index_action == NUMBER_FEATURES + 2: # display xml case
        xml_output = open_xml(id_exercise)
        xml_render = prepare_xml_to_display_html(xml_output)
        conversion_type = file_treatment_infos.loc[id_exercise].at["conversion_type"]
        html_tags = generate_select_tags(CLASS_NAME_DICT, convert_type_to_class_name(conversion_type))
        successor = find_successor_in_index(INDEX_EXERCISES, id_exercise)
        predecessor = find_predecessor_in_index(INDEX_EXERCISES, id_exercise)
        return HTML_CORRECTION_TEMPLATE.render(
                head="",
                body=xml_render,
                tags=html_tags,
                to_show = "Afficher le HTML",
                result=result,
                successor=successor,
                predecessor=predecessor,
            )
    elif index_action == NUMBER_FEATURES + 3: #display html case
        html_output = generate_html(file_treatment_infos, id_exercise, nlp_token_class, nlp)

    head, body = head_body_html(html_output)
    conversion_type = file_treatment_infos.loc[id_exercise].at["conversion_type"]
    html_tags = generate_select_tags(CLASS_NAME_DICT, convert_type_to_class_name(conversion_type))
    successor = find_successor_in_index(INDEX_EXERCISES, id_exercise)
    predecessor = find_predecessor_in_index(INDEX_EXERCISES, id_exercise)
    return HTML_CORRECTION_TEMPLATE.render(
        head=head,
        body=body,
        tags=html_tags,
        to_show = "Afficher le XML",
        result=result,
        successor=successor,
        predecessor=predecessor,
    )
