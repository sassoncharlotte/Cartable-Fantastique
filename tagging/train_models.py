import logging
import os
import torch
import numpy as np
import pandas as pd
from scipy.special import softmax
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from simpletransformers.classification import ClassificationModel

import fantastic.paths


def load_data(path_name: str):
    """load csv from tagging/data"""

    data_path = os.path.join(fantastic.paths.TAG_DIR, "data", path_name)

    return pd.read_csv(data_path)


def load_transformers():
    """logging to transformers"""

    logging.basicConfig(level=logging.INFO)
    transformers_logger = logging.getLogger("transformers")
    transformers_logger.setLevel(logging.WARNING)

def get_label_dict(nb_cats:int):
    """returns the label dict"""

    label_dict = {
        'Autres': 0,
        'CM': 1,
        'RC': 2,
        'EditPhrase': 3,
        'ExpressionEcrite': 4,
        'TransformePhrase': 5,
        'TransformeMot': 6,
        'CocheMots': 7,
        'CochePhrase': 8,
        'Classe': 9,
        'RCImage': 10,
        'Associe': 11,
        'RCCadre': 12,
        'CacheIntrus': 13,
        'CocheGroupeMots': 14,
        'RCDouble': 15,
        'VraiFaux': 16,
        'GroupeEchange': 17,
        'Texte': 18,
        'CocheIntrus': 19,
        'ClasseCM': 20
    }

    new_label_dict = {}
    for k,v in label_dict.items():
        if v < nb_cats:
            new_label_dict[k] = v
        
    return new_label_dict


def prepare_data(data: pd.DataFrame, nb_cats:int):
    """split data into train and eval data"""

    label_dict = get_label_dict(nb_cats)
    data.replace(label_dict, inplace=True)

    train_data, eval_data = train_test_split(data, test_size=0.25)

    return train_data, eval_data


def create_model(
    nb_cats: int,
    model_type: str = "camembert",
    model_name: str = "camembert-base",
    model_args: dict = None,
    use_cuda: bool = False,
):
    """setting up a model from transformers"""

    # model config
    if model_args is None:
        model_args = {"num_train_epochs": 3}

    # Create a ClassificationModel
    model = ClassificationModel(
        model_type, model_name, num_labels=nb_cats, args=model_args, use_cuda=use_cuda
    )

    return model


def load_model(
    model_type: str = "camembert",
    model_path: str = os.path.join(
        fantastic.paths.TAG_DIR, "tagging", "models", "best_model"
    ),
):
    """loading a saved model"""

    use_cuda = torch.cuda.is_available()
    model = ClassificationModel(model_type, model_path, use_cuda=use_cuda)

    return model


def train_model(model, train_data: pd.DataFrame):
    """using simple transformers"""

    # Train the model
    model.train_model(train_data)

    return model


def evaluate_model(model, eval_data: pd.DataFrame, nb_cats: int):
    """evaluate model according to different metrics"""

    # evaluate the model
    result, model_outputs, wrong_predictions = model.eval_model(eval_data)

    # actual and predicted labels
    actual = np.array(eval_data["labels"])
    pred = np.argmax(model_outputs, axis=1)

    # labels as they are in data
    labels = range(nb_cats)
    # target names are labels are they should be displayed
    label_dict = get_label_dict(nb_cats)
    sorted_labels = sorted(label_dict.items(), key=lambda item: item[1])
    target_names = [x for x, y in sorted_labels]

    # computing different metrics
    accuracy = np.sum(
        (np.argmax(model_outputs, axis=1) - np.asarray(eval_data["labels"])) == 0
    ) / len(eval_data)

    matrix = confusion_matrix(actual, pred, labels=labels)

    report = classification_report(
        actual, pred, labels=labels, target_names=target_names
    )

    return accuracy, matrix, report


def predict(model, input_data: str, nb_cats: int):
    """predict the output of a model on a data point"""

    # predict
    predictions, raw_outputs = model.predict([input_data])

    # transforming outputs into a proper dict
    output_dict = {k: raw_outputs[0][k] for k in range(nb_cats)}

    # we add labels to the output dict
    label_dict = get_label_dict(nb_cats)
    inv_label_dict = {v: k for k, v in label_dict.items()}
    labeled_output_dict = {inv_label_dict[k]: v for k, v in output_dict.items()}

    # getting probabilities from outputs using softmax
    prob_list = softmax([v for k, v in labeled_output_dict.items()])

    # creating the probability dict
    prob_dict = {}
    labeled_output_list = list(labeled_output_dict.items())

    for i in range(nb_cats):
        label = labeled_output_list[i][0]
        prob = prob_list[i]
        prob_dict.update({label: prob})

    sorted_prob_dict = {
        k: v for k, v in sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    }

    # getting the most probable categories
    top_cats = {}
    for k, v in sorted_prob_dict.items():
        top_cats[k] = v

    return top_cats


if __name__ == "__main__":

    data = load_data("CAM_tagged_data_16.csv")

    load_transformers()

    train_data, eval_data = prepare_data(data, 16)

    model = load_model(
        model_type="camembert",
        model_path=os.path.join(
            fantastic.paths.TAG_DIR, "models", "best_model"
        ),
    )

    accuracy, matrix, report = evaluate_model(model=model, eval_data=eval_data, nb_cats=16)

    top_cats = predict(
        model=model, input_data="<exercice>", nb_cats=16
    )

    print("accuracy = ", accuracy)
    print(top_cats)
