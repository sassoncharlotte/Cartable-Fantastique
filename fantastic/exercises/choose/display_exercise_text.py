from typing import List
import re
from fantastic.exercises.utils import (
    find_all_sentences,
    search_common_symbols,
    cut_string
)


def prepare_to_dipsplay_exercise_text(
    sentences: List[str],
    choices: List[List[str]],
    non_fill_chars: List[str] = None,
    fill_symbol: str = "…",
):
    """
    Returns the lines to fill in the html with the choices found in the exercise text

    Parameters:
        sentences (List[str]): The list of the different sentences composing the exercise
        choices (List[List[str]]): The list containing the choices
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        fill_symbol (str) (default: "…"): A string to specify the symbol replacing all fill symbols spoted
        in the sentences
    Returns:
        text_to_fill, choices (List[str], List[List[str]]): The lines to display with the different choices
    """
    text_to_show = __find_to_show_exercise_text(sentences)
    text_to_fill = __prepare_to_fill_exercise_text(
        text_to_show, sentences, choices, non_fill_chars, fill_symbol
    )
    return __additional_treatment_exercise_text(choices, text_to_fill, fill_symbol)


def __find_to_show_exercise_text(sentences: List[str]):
    """
    Returns the list of the different lines composing the displayed html
    (For now 1 line = 1 sentence)

    Parameters:
        sentences (List[str]): The list of the different sentences composing the exercise
    Returns:
        text_to_show (List[str]): The list of strings representing each line displayed in the html
    """
    if len(sentences) == 1:
        sentences = find_all_sentences(sentences[0])
    text_to_show = sentences
    return text_to_show


def __prepare_to_fill_exercise_text(
    text_to_show: List[str],
    sentences: List[str],
    choices: List[List[str]],
    non_fill_chars: List[str] = None,
    fill_symbol: str = "…",
):
    """
    Returns the list of the different lines composing the displayed html after preparing them
    by filling the places to put the choices by a fill symbol
    (Most of the time 1 line = 1 sentence)

    Parameters:
        text_to_show (List[str]): The list of strings representing each line displayed in the html
        sentences (List[str]): The list of the different sentences composing the exercise
        choices (List[List[str]]): The list containing the choices
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        fill_symbol (str) (default: "…"): A string to specify the symbol replacing all symbols spoted
        in the sentences
    Returns:
        text_to_fill (List[str]): The list of strings representing each line displayed in the html
    """
    text_to_fill = []
    if not re.search(r"^(\w\W\s*){1,}\s", sentences[0]):
        sentences = ["".join(sentences)]
    candidates_fill = search_common_symbols(sentences, non_fill_chars)
    # sentences and not text to show because of the case where a sentence does not have a fill_char unlike the others
    # we could change that with search_common_symbols decision function being there are x sentences with the fill_char
    # with x being the number of couples of choices found by find_choices
    places = __find_place_exercise_text(text_to_show, choices)
    if candidates_fill:
        for i, place in enumerate(places):
            if place:
                text_to_fill.append("".join(cut_string(text_to_show[i], place)))
            else:
                text_to_fill.append(text_to_show[i])
        text_to_fill = [
            re.sub(re.escape(candidates_fill[0]), fill_symbol, line)
            for line in text_to_fill
        ]
    else:
        for i, place in enumerate(places):
            if place:
                text_to_fill.append(
                    "".join(cut_string(text_to_show[i], place, fill_symbol))
                )
    return text_to_fill


def __additional_treatment_exercise_text(
    choices: List[List[str]], text_to_fill: List[str], fill_symbol: str
):
    """
    Returns the lines to fill in the html with the prepared choices. If there
    are less choices than places to fill, it means some choices have to be filled
    in several places.

    Parameters:
        choices (List[List[str]]): The list containing the choices
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
    Returns:
        text_to_fill, choices (List[str], List[List[str]]): The lines to display with the different choices
    """
    total_number_place_to_fill = "".join(text_to_fill).count(fill_symbol)
    prepared_choices = choices
    if len(choices) < total_number_place_to_fill:
        prepared_choices = []
        for i, line in enumerate(text_to_fill):
            line_number_place_to_fill = line.count(fill_symbol)
            prepared_choices.extend([choices[i]] * line_number_place_to_fill)
    return text_to_fill, prepared_choices


def __find_place_exercise_text(sentences: List[str], choices: List[List[str]]):
    """
    Returns A list of tuple (start_pos, end_pos) for each sentence to replace by a filling symbol
    (used in the case where sentence is of the form "a. La cigale/La cigale et la fourmi chantent")

    Parameters:
        sentences (List[str]): The list of the different sentences composing the exercise
        choices (List[List[str]]): The list containing the choices
    Returns:
        span_list (List[Tuple[int]]): The pos of the different places to fill
    """
    span_list = []
    i = 0
    for sentence in sentences:
        pattern = re.compile(r"\W?" + r"\s*.\s*".join(choices[i]) + r"\W?")
        if pattern.search(sentence):
            span_list.append(pattern.search(sentence).span())
            i += 1
        else:
            span_list.append(())
    return span_list
