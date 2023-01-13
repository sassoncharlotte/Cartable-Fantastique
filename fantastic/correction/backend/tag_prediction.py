import os
import xml.etree
import fantastic.paths
import tagging.train_models


def load_tagging_model():
    """load best model of tagging"""

    # load transformers
    tagging.train_models.load_transformers()

    # best model
    model = tagging.train_models.load_model(
        model_type="camembert",
        model_path=os.path.join(fantastic.paths.TAG_DIR, "models", "best_model"),
    )

    return model


def get_most_likely_tags(tagging_model, id_exercise: str):
    """
    Using tagging ML model, determine what are the most likely tags
    Output is a dict with as keys the classes and as value the
    predicted probability
    """

    # we first get the xml
    with open(
        os.path.join(fantastic.paths.XML_DIR, f"{id_exercise}.xml"),
        mode="r",
        encoding="UTF-8",
    ) as opened_file:
        # we get the content from the xml
        xml_ex = xml.etree.ElementTree.parse(opened_file)
        root = xml_ex.getroot()
        content = xml.etree.ElementTree.tostring(root, encoding="unicode", method="xml")

    # then we predict output with a ml model
    top_categories = tagging.train_models.predict(
        model=tagging_model, input_data=content, nb_cats=16
    )

    return top_categories
