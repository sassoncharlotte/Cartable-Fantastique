from configparser import ConfigParser
import json
import os
import fantastic.paths
from fantastic.exercises.utils import generate_nlp_gilf, generate_nlp_spacy
# Fill
from fantastic.exercises.fill.edit_phrase import EditPhrase
from fantastic.exercises.fill.expression_ecrite import ExpressionEcrite
from fantastic.exercises.fill.transforme_mot import TransformeMot
from fantastic.exercises.fill.rc_double import RemplirClavierDouble
from fantastic.exercises.fill.remplir_clavier import RemplirClavier
from fantastic.exercises.fill.transforme_phrase import TransformePhrase
from fantastic.exercises.fill.rc_cadre import RemplirClavierCadre
from fantastic.exercises.fill.rc_image import RemplirClavierImage
# Select
from fantastic.exercises.select.classe import Classe
from fantastic.exercises.select.cache_intrus import CacheIntrus
from fantastic.exercises.select.coche_groupe_mots import CocheGroupeMots
from fantastic.exercises.select.coche_intrus import CocheIntrus
from fantastic.exercises.select.coche_phrases import CochePhrases
from fantastic.exercises.select.coche_mots import CocheMots
# Choose
from fantastic.exercises.choose.choix_multiples import ChoixMultiples
from fantastic.exercises.choose.classe_cm import ClasseCM
from fantastic.exercises.choose.vrai_faux import VraiFaux
# Swap
from fantastic.exercises.swap.swap import Swap
# Show
from fantastic.exercises.show.texte import Texte


class_name_dict = {
    "Fill": {
        "ExpressionEcrite": ExpressionEcrite,
        "RC": RemplirClavier,
        "RCCadre": RemplirClavierCadre,
        "RCDouble": RemplirClavierDouble,
        "RCImage": RemplirClavierImage,
        "EditPhrase": EditPhrase,
        "TransformePhrase": TransformePhrase,
        "TransformeMot": TransformeMot,
    },
    "Select": {
        "Classe": Classe,
        "CacheIntrus": CacheIntrus,
        "CocheIntrus": CocheIntrus,
        "CocheMots": CocheMots,
        "CochePhrases": CochePhrases,
        "CocheGroupeMots": CocheGroupeMots,
    },
    "Choose": {
        "CM": ChoixMultiples,
        "ClasseCM": ClasseCM,
        "VraiFaux": VraiFaux,
    },
    "Swap": {
        "Swap": Swap,
    },
    "Show": {
        "Texte": Texte,
    },
}



def main():
    # loading the config to read the config file
    config = ConfigParser()
    config.read(os.path.join(fantastic.paths.FANTASTIC_DIR, "exercises", "data.cfg"))

    # loading the nlp models
    nlp_token_class = generate_nlp_gilf()
    nlp = generate_nlp_spacy()

    # path to the json directory
    path = fantastic.paths.JSON_DIR


    for file_path in os.listdir(path):
        with open(os.path.join(path, file_path), 'r', encoding='utf-8') as json_file:

            json_dict = json.load(json_file)

            # adapting only the exercise that are tagged
            if 'type' in json_dict.keys():

                exercise_type = json_dict["type"]

                for category in class_name_dict:
                    if exercise_type in class_name_dict[category]:

                        # gettin the class that we need to adapt the exercise
                        class_name = class_name_dict[category][exercise_type]

                        exercise_path = os.path.join(path, file_path)

                        exercises = class_name(exercise_path, config)

                        try:
                            exercises.create_template().load_json()

                            if json_dict["type"] in class_name_dict["Select"]:
                                exercises.adapt(nlp_token_class, nlp)

                            else:
                                exercises.adapt()

                            exercises.write_template()

                        except Exception as e:
                            print(f"{file_path} could not be adapted: {e}")

if __name__ == '__main__':
    main()
