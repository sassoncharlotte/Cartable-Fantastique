from configparser import ConfigParser
import os
import re
from transformers.pipelines.token_classification import TokenClassificationPipeline
from spacy.lang.fr import French
import fantastic.paths
# Fill
from fantastic.exercises.fill.edit_phrase import EditPhrase
from fantastic.exercises.fill.expression_ecrite import ExpressionEcrite
from fantastic.exercises.fill.transforme_mot import TransformeMot
from fantastic.exercises.fill.rc_double import RemplirClavierDouble
from fantastic.exercises.fill.remplir_clavier import RemplirClavier
from fantastic.exercises.fill.transforme_phrase import TransformePhrase
from fantastic.exercises.fill.rc_cadre import RemplirClavierCadre
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



CLASS_NAME_DICT = {
    # Fill
        "ExpressionEcrite": ExpressionEcrite,
        "RemplirClavier": RemplirClavier,
        "RemplirClavierCadre": RemplirClavierCadre,
        "RemplirClavierDouble": RemplirClavierDouble,
        "EditPhrase": EditPhrase,
        "TransformePhrase": TransformePhrase,
        "TransformeMot": TransformeMot,
    # Select
        "Classe": Classe,
        "CacheIntrus": CacheIntrus,
        "CocheIntrus": CocheIntrus,
        "CocheMots": CocheMots,
        "CochePhrases": CochePhrases,
        "CocheGroupeMots": CocheGroupeMots,
    # Choose
        "ChoixMultiples": ChoixMultiples,
        "ClasseCM": ClasseCM,
        "VraiFaux": VraiFaux,
    # Swap
        "Swap": Swap,
    # Show
        "Texte": Texte
    }

EXERCISE_TYPE_DICT = {
    # Fill
        "ExpressionEcrite": "expression_ecrite",
        "RemplirClavier": "remplir_clavier",
        "RemplirClavierCadre": "rc_cadre",
        "RemplirClavierDouble": "rc_double",
        "EditPhrase": "edit_phrase",
        "TransformePhrase": "transforme_phrase",
        "TransformeMot": "transforme_mot",
    # Select
        "Classe": "classe",
        "CacheIntrus": "cache_intrus",
        "CocheIntrus": "coche_intrus",
        "CocheMots": "coche_mots",
        "CochePhrases": "coche_phrases",
        "CocheGroupeMots": "coche_groupe_mots",
    # Choose
        "ChoixMultiples": "choix-multiples",
        "ClasseCM": "classe-cm",
        "VraiFaux": "vrai-faux",
    # Swap
        "Swap": "swap",
    # Show
        "Texte": "texte"
}

select_subclasses: list = ["Classe","CacheIntrus", "CocheIntrus", "CocheMots", "CochePhrases", "CocheGroupeMots"]

def convert_type_to_class_name(exercise_type: str):
    """Convert the output folder name assiociated to a class to its real name class"""
    elems = re.split(r"[-_\s]",exercise_type)
    class_name = ""
    for elem in elems:
        if len(elem) <= 2:
            if elem.lower() == "rc":
                class_name += "RemplirCadre"
            else:
                class_name += elem.upper()
        else:
            class_name += elem.capitalize()
    return class_name

def convert_class_name_to_type(class_name: str):
    """Convert the class name to the output folder name assiociated to the class"""
    return EXERCISE_TYPE_DICT[class_name]

def generate_conversion_from_tag(id_exercise: str, tag: str, nlp_token_class: French = None, nlp: TokenClassificationPipeline = None):
    """Generates the conversion of an exercise in a certain type (tag)"""
    def init_exercise(id_exercise: str, tag: str):
        """ initializes a new instance of the exercise with the given type (tag)"""
        if not tag in CLASS_NAME_DICT:
            return None
        json_path = os.path.join(fantastic.paths.JSON_DIR, id_exercise + ".json")
        config = ConfigParser()
        config.read(os.path.join(fantastic.paths.FANTASTIC_DIR, "exercises", "data.cfg"))
        return CLASS_NAME_DICT[tag](json_path, config)

    exercise = init_exercise(id_exercise, tag)
    if not exercise:
        return ""
    exercise.load_json()
    exercise.create_template()
    if tag in select_subclasses:
        exercise.adapt(nlp_token_class, nlp)
    else:
        exercise.adapt()
    return exercise.html_output
