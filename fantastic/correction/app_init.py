import os
import re
import pandas as pd
import fantastic.paths
from fantastic.correction.backend.store import export_to_csv

OUTPUT_FOLDER_PATH: str = fantastic.paths.OUTPUT_DIR
CORRECTION_FOLDER_PATH: str = fantastic.paths.CORRECTION_DIR


def init_file_infos(output_folder_path: str):
    """
    Initalizes a pd.DataFrame to track operations done through the correction interface
    with following columns:
    - id_exercise : the id of the exercise
    - category_path : a path of the form "folder_feature_correction>exercise_type"
    (ex: well-converted/texte)
    - exercise_type: the type of the exercise stored in the output folder
    - conversion_type: the type of the exercise in the correction interface
    """
    file_infos = pd.DataFrame(
        columns=["id_exercise", "category_path", "exercise_type", "conversion_type"]
    )
    subfolder_paths = [
        os.path.join(output_folder_path, subfolder)
        for subfolder in os.listdir(output_folder_path)
        if not re.match(r"^\.|^css$|^js$", subfolder)
    ]
    for subfolder_path in subfolder_paths:
        exercise_type = subfolder_path.split(os.sep)[-1]
        for id_exercise in os.listdir(subfolder_path):
            file_infos = file_infos.append(
                {
                    "id_exercise": id_exercise.split(".")[0],
                    "category_path": None,
                    "exercise_type": exercise_type,
                    "conversion_type": exercise_type,
                },
                ignore_index=True,
            )
    file_infos = file_infos.set_index("id_exercise")
    return file_infos


def sort_file_infos(file_infos: pd.DataFrame):
    """Sorts the given DataFrame of tracking operations by id_exercises (ex: "5_4" < "6_2" < "6_3" > "7_2")"""
    return file_infos.sort_index(
        key=lambda x: x.map(lambda x: tuple(map(int, x.split("_"))))
    )


if __name__ == "__main__":
    #Initializes the file_treatment_infos DataFrame and stores it in the correction folder
    file_infos_init = init_file_infos(OUTPUT_FOLDER_PATH)
    file_infos_init = sort_file_infos(file_infos_init)
    export_to_csv(file_infos_init, CORRECTION_FOLDER_PATH)
