from typing import List
import re
from fantastic.exercises.utils import compute_separators_pattern_black


def find_choices_in_add_guideline(
    chars: str, sentences: List[str],
    non_separators: List[str] = None,
    non_fill_chars = None,
    replacing_symbol: str = "§",
):
    """
    Returns choices in additional guideline (separators are supposed to be symbols)
    (expected form or additional guideline: "choice1 sep choice2 sep etc."
    or even "choice1 choice2 choice3/choice4")

    Parameters:
        chars (str): The string in which we look for choices.
        non_separators (List[str]) (default: None): A list of symbols characters considered as non separators
        (Should normally not contain the white space character " ")
        replacing_symbol (str) (default: "§"):  A string to specify the symbol replacing all separators spoted
        in chars
    Returns:
        choices (List[List[str]]): The choices in chars
    """
    choices = []
    if chars:
        if has_choices_as_sentences(chars, sentences, non_fill_chars):
            raw_choices = find_choices_as_sentences(chars)
            chars = replacing_symbol.join(raw_choices) # there might be several choices hidden in one element
        pattern = compute_separators_pattern_black(non_separators)
        if pattern.search(chars):
            choices = pattern.split(chars)
    clean_choices = clean_choices_add_guideline(choices)
    if not clean_choices:
        return clean_choices
    return [clean_choices]


def clean_choices_add_guideline(choices_list: List[str]):
    """
    Returns the choices after cleaning the choices list given (expected parameter form: ["word1", "word2", "",
    "word3", "", "", etc.] where choice1 is "word1 word2" and choice2 is "word3" etc.)

    Parameters:
        choices_list (List[str]): A raw list of strings containing the choices
    Returns:
        clean_list (List[str]): The clean choices
    """
    if not ("" in choices_list) or not choices_list:
        return choices_list  # already clean or empty
    if choices_list[-1] == "":
        choices_list.pop()

    clean_list = []
    index = 1
    start_index = 0
    while index < len(choices_list):
        if not (choices_list[index]) and choices_list[index - 1]:
            #if "something","":
            clean_list.append(" ".join(choices_list[start_index:index]))
        elif choices_list[index] and not choices_list[index - 1]:
            #elif "","something":
            start_index = index
        index += 1
    clean_list.append(" ".join(choices_list[start_index:]))
    return clean_list


def has_choices_as_sentences(chars: str, sentences: List[str], non_fill_chars: List[str]):
    """
    Returns whether choices are in the form "choice1. choice2. etc." or not.
    The only difficulty lies in the determination of whether the "." is part of
    the choices or acts as a separator
    """
    if re.search(r"[.?!]\.", chars):
        return True
    elif re.search(r"\.", chars):
        # . could be part of the choices
        pattern = compute_separators_pattern_black(non_fill_chars)
        exercise_text = " ".join(sentences)
        match_fill = pattern.search(exercise_text)
        if match_fill:
            fill_symbol = re.escape(match_fill[0])
            start, _ = match_fill.span()
            regex_end_sentence = fr"^{fill_symbol}\s?[A-Z«»]|^{fill_symbol}\s*$|^{fill_symbol}\s*(\w\W\s*){{1,}}\s"
            if not re.match(regex_end_sentence, exercise_text[start:]):
            # if not (... capitale letter) or (... «) or (... ») or (... (end)) or (... a.)
                return True
    return False


def find_choices_as_sentences(chars: str):
    """Returns the choices in chars when choices are hold as sentences in chars"""
    choices = re.split(r"\.", chars)
    for index, elem in enumerate(choices[:-1]):
        if not elem and index:
            choices[index-1] += "."
    return [choice for choice in choices if choice]
