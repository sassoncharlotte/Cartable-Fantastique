from typing import List
import os
import shutil
import pandas as pd


def generate_correction_output_folders(
    output_folder_path: str,
    correction_output_directory: str,
    correction_features: List[str],
):
    """
    Generates the correction output folder and all its subfolders
    The structure is the following:
    correction_output_folder>correction_feature>exercise_type>exercise_file
    """
    exercise_types = [cat for cat in os.listdir(output_folder_path)]
    has_js = "js" in exercise_types
    has_css = "css" in exercise_types
    old_wd = os.getcwd()
    os.chdir(correction_output_directory)
    create_folder_from_current("correction_output")
    for feature in correction_features:
        create_folder_from_current(f"correction_output/{feature}")
        for exercise_type in exercise_types:
            create_folder_from_current(f"correction_output/{feature}/{exercise_type}")
        if has_js:
            copy_files(
                os.path.join(output_folder_path, "js"),
                os.path.join("correction_output", feature, "js"),
            )
        if has_css:
            copy_files(
                os.path.join(output_folder_path, "css"),
                os.path.join("correction_output", feature, "css"),
            )
    os.chdir(old_wd)
    return None


def retrieve_css_and_js_files(output_folder_path: str, target_directory: str):
    """
    Retrieves the css and js files to the /static folder before mounting them
    (in case some modifications to the css and js files in the output directory have been made)
    """
    if "js" in os.listdir(output_folder_path):
        create_folder_from_current(os.path.join(target_directory, "js"))
        copy_files(
            os.path.join(output_folder_path, "js"), os.path.join(target_directory, "js")
        )
    if "css" in os.listdir(output_folder_path):
        create_folder_from_current(os.path.join(target_directory, "css"))
        copy_files(
            os.path.join(output_folder_path, "css"),
            os.path.join(target_directory, "css"),
        )
    return None


def create_folder_from_current(path_folder: str):
    """
    Creates a folder from current working directory if does not exist at path:
    cwd>path_folder
    """
    if not os.path.exists(path_folder):
        os.mkdir(path_folder)
    return None


def copy_files(src_folder: str, target_folder: str):
    """
    Copies all files from the src_folder to the target_folder
    (Care to define paths from the current working directory)
    """
    for file_path in [
        os.path.join(src_folder, to_copy) for to_copy in os.listdir(src_folder)
    ]:
        target_file = file_path.split(os.sep)[-1]
        shutil.copyfile(file_path, os.path.join(target_folder, target_file))
    return None


def store_in_corresponding_folder(
    file_render: str,
    correction_output_directory: str,
    correction_features: List[str],
    index_feature: int,
    subfolder: str,
    filename: str,
):
    """
    Stores the file_render as an html file in the corresponding folder
    path form:
    cwd>path_correction_output_directory>correction_feature>type_conversion>filename.html
    """
    feature = correction_features[index_feature]
    with open(
        os.path.join(
            correction_output_directory, feature, subfolder, filename + ".html"
        ),
        "w",
        encoding="utf-8",
    ) as html_correction_output:
        html_correction_output.write(file_render)
    return None


def remove_latest_treatment(
    file_treatment_infos: pd.DataFrame,
    correction_output_directory: str,
    exercise_id: str,
    category: str,
):
    """
    Removes the latest treatment done to the exercise through the correction interface by deleting the corresponding
    file stored in the correction_output_folder
    """
    latest_treatment = file_treatment_infos.loc[exercise_id].at["category_path"]
    conversion_type = file_treatment_infos.loc[exercise_id].at["conversion_type"]
    new_treatment = os.path.join(category, conversion_type)
    if not latest_treatment or new_treatment == latest_treatment:
        pass
    else:
        latest_treatment_path = os.path.join(
            os.path.join(correction_output_directory, "correction_output"),
            latest_treatment,
            exercise_id + ".html",
        )
        if os.path.exists(latest_treatment_path):
            os.remove(latest_treatment_path)
    return

def export_to_csv(file_infos: pd.DataFrame, correction_folder: str):
    """exports a pandas DataFrame file infos as csv to the correction folder path given"""
    file_infos.to_csv(os.path.join(correction_folder,"file_treatment_infos.csv"), encoding="utf-8", index=True)
    return None
