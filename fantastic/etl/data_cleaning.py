import json
import os
import xmltodict
import pandas as pd

import fantastic.paths


def jsonify(xml_folder, json_folder) -> None:
    """transform every xml into json"""

    # list of all files (and not directories) in exs/
    ex_paths = [
        xml_file for xml_file in os.listdir(xml_folder) if xml_file.endswith("xml")
    ]

    # create the dir if necessary
    if not os.path.exists(json_folder):
        os.mkdir(json_folder)

    # going through every xml
    for ex_path in ex_paths:
        # getting xml
        with open(
            os.path.join(xml_folder, ex_path), mode="r", encoding="UTF-8"
        ) as xml_ex:
            obj = xmltodict.parse(xml_ex.read(), encoding="utf-8")

        # creating the json
        new_path = os.path.join(json_folder, ex_path.split(".")[0] + ".json")

        with open(new_path, mode="w", encoding="UTF-8") as json_ex:
            json.dump(obj, json_ex, indent=4, ensure_ascii=False)


def add_tag_to_json(json_folder, tag_file):
    """get tags from an excel and add them to the json"""

    # getting tags
    tags = pd.read_excel(tag_file)
    number_exercises = tags.shape[0]
    id_exercice = tags.keys()[0]
    type_exercice = tags.keys()[1]

    # going through every exercise with a tag
    tagged = []

    for i in range(number_exercises):
        json_filename = tags[id_exercice][i] + ".json"
        json_path = os.path.join(json_folder, json_filename)

        try:
            with open(json_path, mode="r", encoding="UTF-8") as opened_file:
                json_file = json.load(opened_file)
            with open(json_path, mode="w", encoding="UTF-8") as opened_file:
                json_file["type"] = tags[type_exercice][i]
                json.dump(json_file, opened_file, indent=4, ensure_ascii=False)
            tagged.append(json_filename)

        except FileNotFoundError as error_message:
            print(error_message)

    # looking at exercises without tags
    not_tagged = []

    for jsonfile in os.listdir(json_folder):
        if jsonfile not in tagged:
            not_tagged.append(jsonfile)
    return not_tagged


def cleaning_excel(path=fantastic.paths.UNTAGGED_EXCEL):
    """Removing the spaces at the end of some exercise types
    Replaced every exercise id that had a dash with the same id using an underscore"""

    file_name = path

    excel_df = pd.read_excel(file_name)

    nb_rows = excel_df.shape[0]

    for i in range(nb_rows):
        exercise_id = excel_df.iat[i, 0]

        # correction of the mistakes in the writting of the exercices number and page
        exercise_id.replace("-", "_")
        exercise_id.replace(" ", "")

    # creation of a modified Excel
    excel_df.to_excel(fantastic.paths.TAGGED_EXCEL, index=False)


def getting_infos_on_excel(searched_cat="CM", path=fantastic.paths.TAGGED_EXCEL):
    """Returns:
    categories_list (the list of categories),
    categories_dict (keys are the categories and values are the number of corresponding ex)
    exercises (the list of exercise of category 'searched_cat')"""

    file_name = path

    excel_df = pd.read_excel(file_name)

    nb_rows = excel_df.shape[0]

    categories_list = []
    # dictionary with the categories and the number of exercices corresponding
    categories_dics = (
        {}
    )

    for i in range(nb_rows):
        category = excel_df.iat[i, 1]

        if category not in categories_list:
            categories_list += [category]
            categories_dics[category] = 0
        if category in categories_list:
            categories_dics[category] += 1

    exercises = []
    for i in range(nb_rows):
        cat = excel_df.iat[i, 1]
        if cat == searched_cat:
            exercises += [excel_df.iat[i, 0]]

    return categories_list, categories_dics, exercises
