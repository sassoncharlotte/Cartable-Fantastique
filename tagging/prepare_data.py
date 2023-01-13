import json
import os
import xml.etree
import numpy as np
import pandas as pd

import fantastic.paths
from fantastic.exercises.utils import find_all_sentences, find_in_dict


def get_data_from_excel():
    """returns a raw df from the excel"""

    types_df = pd.read_excel(fantastic.paths.TAGGED_EXCEL)

    return types_df


def get_data_from_json(types_df: pd.DataFrame):
    """get all the info from jsons"""

    # creating a new col for content for types_df
    types_df["content"] = pd.Series(np.zeros(len(types_df["exerciseID"])))

    # list of all json files
    ex_paths = [
        json_file
        for json_file in os.listdir(fantastic.paths.JSON_DIR)
        if json_file.endswith("json")
    ]

    for ex_path in ex_paths:

        with open(
            os.path.join(fantastic.paths.JSON_DIR, ex_path), mode="r", encoding="UTF-8"
        ) as opened_file:

            json_ex = json.load(opened_file)

            # getting exercise
            exercise = find_in_dict(json_ex, dict, "exercice")

            # getting guideline
            guideline = find_in_dict(exercise, str, "consigne")

            # getting exercise text
            dict_found = find_in_dict(exercise, dict, "enonce")
            if not dict_found:
                exercise_text = find_in_dict(exercise, str, "enonce")
            else:
                exercise_text = dict_found

            # getting additional_guideline
            additional_guideline = find_in_dict(exercise, str, "noteSC").join(
                find_in_dict(exercise_text, str, "#text")
            )

            # getting sentences
            if isinstance(exercise_text, dict):
                ol_case = find_in_dict(exercise_text, dict, "ol")
                if ol_case:
                    sentences = find_in_dict(ol_case, list, "li")
                sentences = []
            else:
                sentences = find_all_sentences(exercise_text)
            sentences_str = "".join(sentences)

            # getting remaining
            remaining = find_in_dict(exercise, str, "rest")

            # the content we'll put in data
            content = f"{guideline} {additional_guideline} {sentences_str} {remaining}"

            # we put the content in the dataframe
            ex_nb = ex_path.split(".")[0]
            if not types_df.loc[types_df["exerciseID"] == ex_nb, :].empty:
                index = types_df.index[types_df["exerciseID"] == ex_nb]
                types_df.loc[index, ["content"]] = content

    return types_df


def get_data_from_xml(types_df: pd.DataFrame):
    """get all the info from xmls"""

    # creating a new col for content for types_df
    total_nb_ex = len(types_df["exerciseID"])
    types_df["content"] = pd.Series(np.zeros(total_nb_ex))

    ex_paths = [
        json_file
        for json_file in os.listdir(fantastic.paths.XML_DIR)
        if json_file.endswith("xml")
    ]

    for ex_path in ex_paths:

        with open(
            os.path.join(fantastic.paths.XML_DIR, ex_path), mode="r", encoding="UTF-8"
        ) as opened_file:

            # we get the content from the xml
            xml_ex = xml.etree.ElementTree.parse(opened_file)
            root = xml_ex.getroot()
            content = xml.etree.ElementTree.tostring(
                root, encoding="unicode", method="xml"
            )

            # we put the content in the dataframe
            ex_nb = ex_path.split(".")[0]
            if not types_df.loc[types_df["exerciseID"] == ex_nb, :].empty:
                index = types_df.index[types_df["exerciseID"] == ex_nb]
                types_df.loc[index, ["content"]] = content

    return types_df


def clean_df(types_df: pd.DataFrame):
    """everything to clean the data"""

    # removing useless infos like comments and guideline changes
    types_df = types_df[["exerciseID", "exerciseType", "content"]]

    # removing useless col
    types_df = types_df.drop(columns=["exerciseID"])

    # renaming columns
    types_df = types_df.rename(columns={"content": "text", "exerciseType": "labels"})
    types_df = types_df.reindex(columns=["text", "labels"])

    return types_df


def keep_only_top_cats(types_df: pd.DataFrame, number_cats: int):
    """removing small cats with few examples"""

    # keeping only most popular types
    most_popular_types = (
        types_df.groupby("exerciseType")
        .count()
        .sort_values(by="content", ascending=False)
        .head(number_cats)
    )
    most_popular_types = most_popular_types.index.values.tolist()

    types_df.loc[
        ~types_df["exerciseType"].isin(most_popular_types), ["exerciseType"]
    ] = "Autres"

    return types_df


def keep_only_big_cats(types_df: pd.DataFrame):
    """replacing small cats by big cats"""

    type_to_big_category = {
        "select": [
            "CocheMots",
            "CochePhrase",
            "Classe",
            "CocheGroupeMots",
            "CocheIntrus",
            "CacheIntrus",
        ],
        "swap": ["GroupeEchange"],
        "choose": ["CM", "VraiFaux", "Associe", "ClasseCM"],
        "fill": [
            "EditPhrase",
            "RC",
            "ExpressionEcrite",
            "TransformePhrase",
            "TransformeMot",
            "RCImage",
            "RCCadre",
            "RCDouble",
        ],
        "show": ["Texte"],
    }

    nb_rows = types_df.shape[0]

    for i in range(nb_rows):
        exercise_type = types_df.iat[i, 1]

        big_cat = ""
        for key in type_to_big_category:
            if exercise_type in type_to_big_category[key]:
                big_cat = key
        if not big_cat:
            big_cat = "Autres"
        types_df.iat[i, 1] = big_cat

    return types_df


def save_to_csv(types_df: pd.DataFrame, path: str) -> None:
    """save data to csv"""

    # loading the data into a csv
    types_df.to_csv(path, encoding="utf-8", index=False)

    return None


def get_data(
    data_type: str = "tagged",
    big_cats: bool = False,
    number_cats: int = 10,
    save: bool = False,
    save_path: str = "",
):
    """getting data from excel and exercises
    data_type :
    * 'tagged' for raw xml data
    * 'untagged' for data without tags
    big_cats : use of big cats or regular cats
    number_cats : for big cats false only
    save_path : for saving true only"""

    types_df = get_data_from_excel()

    if data_type == "tagged":
        types_df = get_data_from_xml(types_df)
    elif data_type == "untagged":
        types_df = get_data_from_json(types_df)
    else:
        raise ValueError("given data type does not exist")

    if big_cats:
        types_df = keep_only_big_cats(types_df)
    else:
        types_df = keep_only_top_cats(types_df, number_cats=number_cats)

    types_df = clean_df(types_df)

    if save:
        save_to_csv(types_df, save_path)

    return types_df


if __name__ == "__main__":

    data = get_data(
        data_type="tagged",
        big_cats=False,
        number_cats=15,
        save=True,
        save_path=os.path.join(fantastic.paths.TAG_DIR, "data", "CAM_tagged_data_16.csv"),
    )
