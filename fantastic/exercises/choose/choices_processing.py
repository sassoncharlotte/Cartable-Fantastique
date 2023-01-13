from typing import List
import re
from fantastic.exercises.utils import compute_separators_pattern_black, search_common_symbols

def final_clean_choices(
    choices: List[List[str]], non_separators: List[str], repl_symbol: str = "§"
):
    """
    Returns the cleaned choices that will be displayed in the html

    Parameters:
        choices (List[List[str]]): The list containing the list of choices
        repl_symbol (str) (default: "§"): A symbol to use for some sub operations on the choices
    Returns:
        clean_choices (List[str]): The list containing the cleaned choices
    """
    clean_choices = []
    if not choices:
        return []
    choices = choices[0]  #[[choice 1, choice2, etc.]] (hence (len(choices) == 1) means same choices everywhere)
    choice_ref = choices[0]
    pattern = compute_separators_pattern_black(non_separators)
    for choice in choices:
        clean_choices.append(pattern.sub(repl_symbol, choice.strip()))
    non_symbols = [symbol for symbol in non_separators if symbol not in ["'", "’", "-"]]
    common_symbols = search_common_symbols(clean_choices, non_symbols)
    if "-" in common_symbols:
        if re.match(r"\w+-$", choice_ref):
            clean_choices = [choice[:-1] for choice in clean_choices]
        if re.match(r"^-\w+", choice_ref):
            clean_choices = [choice[1:] for choice in clean_choices]

    clean_choices = clean_multi_words_choices(clean_choices, common_symbols, repl_symbol)
    return clean_choices


def clean_multi_words_choices(
    choices: List[str], common_symbols: List[str], repl_symbol: str = "§"
):
    """
    Cleans choices with multiples words

    Parameters:
        choices (List[List[str]]): The list containing the list of choices
        common_symbols (List[str]): A list of symbols common to all choices
        repl_symbol (str) (default: "§"): A symbol to use for some sub operations on the choices
    Returns:
        clean_choices (List[str]): The list containing the cleaned choices
    """
    if sum([len(choice.strip().split()) for choice in choices]) <= len(choices):
        # if all choices are composed of one word :
        return choices
    if repl_symbol in common_symbols:
        choices = [
            re.search(re.escape(repl_symbol) + ".+" + re.escape(repl_symbol), choice)[
                0
            ][1:-1]
            for choice in choices
        ]  # allows to spot patterns such as "Singulier (S) ou Pluriel (P)"
    choices_split = [choice.strip().split() for choice in choices]
    clean_choices = []
    for choice_split in choices_split:
        if len(choice_split) > 1:
            for index, elem in enumerate(choice_split[:-1]):
                if "d’" in elem and "’" in common_symbols:
                    choice_split[index] = re.sub(r"d’", "", elem)
                if elem == "de" or elem == "au":
                    choice_split[index] = ""
        clean_choices.append(re.sub(r"\s{2,}", " ", " ".join(choice_split)))
        #subs successive spaces by 1 space
    return clean_choices

def choices_to_html(choices: List[List[str]]):
    """
    Generate html part of the choices

    Parameters:
        choices (List[List[str]]): The list containing the lists of couple of choices to
        display in each fill char of the exercise
        (different from the final_clean_choices)
    Returns:
        html_choices_list (List[str]): The list containing the html strings associated to
        each place where to select choices
    """
    button_choice_html = '<td>\n<button class="word mc_button_choice color{}" \
                        onclick="setChoiceValue(this)" id_mc_button="mc_button_{}" \
                        id_mc_menu="mc_menu_{}">{}</button>\n</td>\n'
    html_choices_list = []
    for i, couple_choices in enumerate(choices):
        number_of_choices = len(couple_choices)
        html_choices = f'<div class="mc_menu" id="mc_menu_{i}" \
                        display: none; position:absolute;>\n<table>\n<tbody>\n'
        for j in range(number_of_choices):
            if j == 0:
                html_choices += "<tr>\n"
            elif not j % 2: # to print 2 choices per line
                html_choices += "</tr>\n<tr>\n"
            html_choices += button_choice_html.format(j % 3, i, i, choices[i][j])
        html_choices += "</tr>\n</tbody>\n</table>\n</div>"
        html_choices_list.append(html_choices)
    return html_choices_list
