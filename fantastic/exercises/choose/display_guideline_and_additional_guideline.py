from typing import List
import re
from fantastic.exercises.utils import (
    find_all_sentences,
    search_common_symbols,
    included,
)
from fantastic.exercises.choose.choices_processing import final_clean_choices

PRONOUN_LIST: List[str] = ["je", "j'", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"]
# could be put in a dict with key pronoun to generalize


def prepare_to_dipsplay_others(
    guideline: str,
    sentences: List[str],
    choices: List[str],
    non_fill_chars: List[str],
    non_separators: List[str],
    repl_symbol: str = "§",
    fill_symbol: str = "…",
):
    """
    Returns the lines to fill in the html with the choices found in the guideline or additional guideline

    Parameters:
        sentences (List[str]): The list of the different sentences composing the exercise
        choices (List[List[str]]): The list containing the choices
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        non_separators (List[str]): A list of symbols characters considered as non separators
        fill_symbol (str) (default: "…"): A string to specify the symbol replacing all fill symbols spoted
        in the sentences
    Returns:
        text_to_fill, choices (List[str], List[List[str]]): The lines to display with the different choices
    """
    text_to_show = __find_to_show_others(sentences, non_separators)
    text_to_fill = __prepare_to_fill_others(text_to_show, sentences, choices, non_fill_chars, fill_symbol)
    return __prepare_choices_others(guideline, choices, text_to_fill, non_separators, repl_symbol, fill_symbol)


def __find_to_show_others(sentences: List[str], non_separators: List[str]):
    """
    Returns the list of the different lines composing the displayed html
    (For now 1 line = 1 sentence or "a. word... sep word... sep word..." convert each word to fill as a line)

    Parameters:
        sentences (List[str]): The list of the different sentences composing the exercise
    Returns:
        text_to_show (List[str]): The list of strings representing each line displayed in the html
    """
    if len(sentences) == 1:
        sentences = find_all_sentences(sentences[0])
    separators = search_common_symbols(sentences, non_separators)
    text_to_show = []
    if separators:
        for sentence in sentences:
            for elt in re.split("[" + re.escape("".join(separators)) + "]", sentence):
                if elt:
                    text_to_show.append(elt)
    else:
        text_to_show = sentences
    return text_to_show


def __prepare_to_fill_others(
    text_to_show: List[str],
    sentences: List[str],
    choices: List[str],
    non_fill_chars: List[str],
    non_separators: List[str],
    fill_symbol: str = "…",
):
    """
    Returns the list of the different lines composing the displayed html after preparing them
    by filling the places to put the choices by a fill symbol

    Parameters:
        text_to_show (List[str]): The list of strings representing each line displayed in the html
        sentences (List[str]): The list of the different sentences composing the exercise
        choices (List[List[str]]): The list containing the list of choices
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        non_separators (List[str]): A list of symbols characters considered as non separators
        fill_symbol (str) (default: "…"): A string to specify the symbol replacing all fill symbols
        spoted in the sentences
    Returns:
        text_to_fill (List[str]): The list of strings representing each line displayed in the html
    """
    text_to_fill = []
    if not sentences:
        return []
    if not re.search(r"^(\w\W\s*){1,}\s", sentences[0]):
        sentences = ["".join(sentences)]
    candidates_fill = search_common_symbols(sentences, non_fill_chars)
    if candidates_fill:
        text_to_fill = [re.sub(re.escape(candidates_fill[0]), fill_symbol, line) for line in text_to_show]
    else:
        # else determine where to place choices
        place = __find_place_others(choices, non_separators)
        if place == "next line":
            text_to_fill = [line.strip() + " ➞ " + fill_symbol for line in text_to_show]
        elif place == "end":
            text_to_fill = [line.strip() + fill_symbol for line in text_to_show]
        elif place == "start":
            index_start_line = spot_start_line(text_to_show)
            text_to_fill = [
                line[: index_start_line[i]] + fill_symbol + line[index_start_line[i] :].strip()
                for i, line in enumerate(text_to_show)
            ]
        elif place == "start space":
            index_start_line = spot_start_line(text_to_show)
            text_to_fill = [
                line[: index_start_line[i]] + fill_symbol + " " + line[index_start_line[i] :].strip()
                for i, line in enumerate(text_to_show)
            ]
        elif place == "space end":
            text_to_fill = [line.strip() + " " + fill_symbol for line in text_to_show]
    return text_to_fill


def __prepare_choices_others(
    guideline: str,
    choices: List[List[str]],
    text_to_fill: List[str],
    non_separators: List[str],
    repl_symbol: str = "§",
    fill_symbol: str = "…",
):
    """
    Prepare the choices to display by cleaning them and capitalizing when needed

    Parameters:
        choices (List[List[str]]): The list containing the list of choices
        text_to_fill (List[str]): The list of strings representing each line displayed in the html after
        preparation
        non_separators (List[str]): A list of symbols characters considered as non separators
        repl_symbol (str) (default: "§"): A symbol to use for some sub operations on the choices
        fill_symbol (str) (default: "…"): A string to specify the symbol replacing all symbols spoted
        in the sentences
    Returns:
        text_to_fill (List[str]): The list of strings representing each line displayed in the html
    """
    if choices:
        clean_choices = [choice.strip() for choice in choices[0]]
    if choices_in_guideline(guideline, choices):
        clean_choices = final_clean_choices(choices, non_separators, repl_symbol)
    final_choices = []
    for line in text_to_fill:
        for match in re.finditer(re.escape(fill_symbol), line):
            pos = match.span()[0]
            if pos < 2 or re.search(
                r"[.!?»]\s$|[.!?«]\s?[-–]\s$|^«?\s?[-–]\s$|^(\w\W\s*){1,}\s$", line[:pos],
            ):  # regex to determine if choice to capitalize
                final_choices.append([choice.capitalize() for choice in clean_choices])
            else:
                final_choices.append(clean_choices)
    return text_to_fill, final_choices


def __find_place_others(choices: List[List[str]], non_separators: List[str]):
    """
    Returns a string indicating where the choices should be added
    (ex: "im-" --> "start", "je" --> "start space", etc.)

    Parameters:
        choices (List[List[str]]): The list containing the list of choices as a single element
        non_separators (List[str]): A list of symbols characters considered as non separators
    Returns:
        (str)
    """
    if not choices:
        return ""
    return_list = ["start", "end", "next line", "start space", "space end"]
    choices = choices[0]  # choices encapsulated in a list
    choice_ref = choices[0]
    replacing_symbol = "§"
    to_search = [re.sub(r"[.?!]", replacing_symbol, choice) for choice in choices]
    common_symbols = search_common_symbols(to_search, non_separators)
    if "-" in common_symbols:
        if re.match(r"\w+-\s*$", choice_ref):
            return return_list[0]
        elif re.match(r"^\s*-\w+", choice_ref):
            return return_list[1]
    if replacing_symbol in common_symbols:
        return return_list[1]
    if included(choices, PRONOUN_LIST):
        return return_list[3]
    return return_list[2]


def spot_start_line(text_to_show: List[str]):
    """
    Returns the index of the position where to insert a fill character when expected at the
    the beginning of the line.
    (ex: "a.3) complet" --> 5)

    Parameters:
        text_to_show (List[str]): The list of strings representing each line displayed in the html
    Returns:
        index_dict (int): The index where to split to insert a fill character at the beginning of the line
    """
    index_dict = {}
    for i, line in enumerate(text_to_show):
        match_start_line = re.search(r"^(\w\W\s*){1,}", line)
        if match_start_line:
            index_dict[i] = match_start_line.span()[1]
        else:
            index_dict[i] = 0
    return index_dict


def choices_in_guideline(guideline: str, choices: List[List[str]]):
    """
    Returns whether the given choices are in the guideline of the exercise or not.
    (Could be defined in a more general form is_in_string(string, string_list)
    """
    if choices:
        choices = choices[0]
        for choice in choices:
            if not choice in guideline:
                return False
    return True
