from typing import List, Tuple
import re
import Levenshtein as lev
from fantastic.exercises.utils import find_all_sentences, flatten_regex


def find_choices_in_guideline(
    guideline: str,
    guideline_separators: dict,
    end_last_choice_patterns: List[str],
    replacing_symbol: str = "§",
    compare_choices_threshold: float = 0.5,
    has_choices_threshold: float = 0.3
    ):
    """
    Returns the choices in the guideline or an empty list if no choices are found.

    Parameters:
        guideline (str): The string in which we look for choices.
        guideline_separators (dict): The dictionary containing as keys the possible regex patterns matching a
        choice separator in the guideline (ordered from highest to lowest priority) and as values a list of all
        the regex patterns beginning with the key regex and representing a case where the key regex does not match
        a choice separator.
        (ex: {"\\sou\\s": "\\sou\\sbien"} means " ou " is considered as a separator only if not followed by "bien")
        end_last_choice_patterns (List[str]): the list of possible regex patterns matching the end of the last
        choice in the guideline
        replacing_symbol (str) (default: "§"):  A string to specify the symbol replacing all separators spoted
        in guideline
        compare_choices_threshold (float) (default: 0.5): A float between 0 and 1 to tune the output of the
        heuristic compare_choices
        has_choices_threshold (float) (default: 0.3): A float between 0 and 1 to tune the output of the
        heuristic has_choices
    Returns:
        choices (List[List[str]]): The choices in the guideline
    """
    # if not is_board_exercise(guideline):
    sentences = find_all_sentences(guideline)
    sentence_choice = __find_sentence_choice(sentences, guideline_separators)
    last_choice = __find_last_choice(sentence_choice, guideline_separators, end_last_choice_patterns)
    choices = __find_other_choices(
        sentence_choice,
        last_choice,
        guideline_separators,
        replacing_symbol,
        compare_choices_threshold
        )
    choices.reverse()  # choices found from last to first
    if not __has_choices(guideline, choices, has_choices_threshold):
        return []
    # else:
    #    choices = find_board_column_names(guideline)
    return [choices] #hence (len(choices) == 1) means same choices everywhere


def __find_sentence_choice(sentences: List[str], guideline_separators: dict):
    """
    Returns the sentence containing the choices (based on the hypothesis that
    all choices are in the same sentence of the guideline)

    Parameters:
        sentences (List[str]): The sentences composing the guideline
        guideline_separators (dict): The dictionary containing as keys the possible regex patterns matching a
        choice separator in the guideline (ordered from highest to lowest priority) and as values a list of all
        the regex patterns beginning with the key regex and representing a case where the key regex does not match
        a choice separator.
        (ex: {"\\sou\\s": "\\sou\\sbien"} means " ou " is considered as a separator only if not followed by "bien")
    Returns:
        sentence_chosen (str): The sentence which contains the choices
    """
    if not sentences:
        return sentences
    sentence_chosen = sentences[0]
    separator_regex_list = list(guideline_separators.keys())
    index_best_pattern = len(separator_regex_list) - 1
    for sentence in sentences:
        for index, pattern in enumerate(separator_regex_list):
            if not index_best_pattern: # can't find better pattern
                return sentence_chosen
            if index >= index_best_pattern:
                break
            if re.search(pattern, sentence):
                index_best_pattern = index
                sentence_chosen = sentence
    return sentence_chosen


def __find_last_choice(sentence_choice: str, guideline_separators: dict, end_last_choice_patterns: List[str]):
    """
    Returns the last_choice (from left to right) (empirically easier to find than the first_choice)
    (Many exceptions like "où ou ou bien")

    Parameters:
        choice_sentence (str): The sentences containing the choices
        guideline_separators (dict): The dictionary containing as keys the possible regex patterns matching a
        choice separator in the guideline (ordered from highest to lowest priority) and as values a list of all
        the regex patterns beginning with the key regex and representing a case where the key regex does not match
        a choice separator.
        (ex: {"\\sou\\s": "\\sou\\sbien"} means " ou " is considered as a separator only if not followed by "bien")
        end_last_choice_patterns (List[str]): the list of possible regex patterns matching the end of the last
        choice in the guideline
    Returns:
        last_choice (str): The last_choice in the choice_sentence
    """

    def __clean_last_choice(last_choice: str, pattern_end: re.Pattern):
        """ Cleans the last_choice"""
        last_choice = pattern_end.split(last_choice)[0]
        last_choice = re.sub(r"\s{2,}", " ", last_choice)
        return last_choice.strip()

    sentence_choice_flat = re.sub(r"\s", " " * 2, sentence_choice)
    for separator_regex, separator_exceptions_list in guideline_separators.items():
        flattened_separator_regex = flatten_regex(separator_regex)
        flattened_exceptions_regex = [flatten_regex(exception) for exception in separator_exceptions_list]
        exceptions_pattern = re.compile("|".join(flattened_exceptions_regex))
        match_separator_list = [match for match in re.finditer(flattened_separator_regex, sentence_choice_flat)]
        match_separator_list.reverse()
        for match_separator in match_separator_list:
            start, end= match_separator.span()
            if not exceptions_pattern.pattern or not exceptions_pattern.match(sentence_choice_flat[start:]):
                last_choice = sentence_choice_flat[end:]
                pattern_end = re.compile("|".join(end_last_choice_patterns))
                return __clean_last_choice(last_choice, pattern_end)
    return ""


def compare_choices(choice_candidate: str, choice_ref: str, threshold: float = 0.5):
    """
    Returns whether the choice candidate is acceptable or not in comparison
    to a reference choice (heuritic)

    Parameters:
        choice_candidate (str): The candidate choice we want to classify
        choice_ref (str): The reference choice we will for comparison
        threshold (float): A float between 0 and 1 to tune the output
    Returns:
        (bool) : Whether the candidate is accepted or not
    """
    list_test = choice_candidate.split()
    list_ref = choice_ref.split()
    if len(list_test) == 1:
        return True
    score = 0
    for i in range(len(list_test) - 1):
        if not list_test[i] in list_ref:
            score += lev.distance(list_test[i], list_ref[i])
    if score <= threshold * len(choice_ref):
        return True
    return False


def __find_other_choices(
    sentence_choice: str,
    last_choice: str,
    guideline_separators: dict,
    replacing_symbol: str = "§",
    compare_choices_threshold: float = 0.5
    ):
    """
    Returns the choices in the sentence containing the choices knowing the last choice

    Parameters:
        sentence_choice (str): The sentence containing the choices
        last_choice (str): The last choice in the sentence (from left to right)
        guideline_separators (dict): The dictionary containing as keys the possible regex patterns matching a
        choice separator in the guideline (ordered from highest to lowest priority) and as values a list of all
        the regex patterns beginning with the key regex and representing a case where the key regex does not match
        a choice separator.
        (ex: {"\\sou\\s": "\\sou\\sbien"} means " ou " is considered as a separator only if not followed by "bien")
        replacing_symbol (str) (default: "§"):  A string to specify the symbol replacing all separators spoted
        in guideline
        compare_choices_threshold (float) (default: 0.5): A float between 0 and 1 to tune the output of the
        heuristic compare_choices
    Returns:
        choices (List[str]): The list containing the raw choices
    """

    def __set_indicator(last_choice: str):
        """
        Returns an indicator that will be used to stop the research of the other
        choices and get more precisely where the first choice is hidden.

        Here indicator is an integer, it could be defined differently, however the
        2 following funnctions have to be changed in accordance to a change of the indicator.
        """
        indicator = len(last_choice.split())
        if re.match(r"ou bien", last_choice):
            indicator = 1
        return indicator

    def __is_candidate_first_choice(candidate: str, to_explore: List[str], indicator: int):
        """Returns whether the candidate is the official candidate for the
        first_choice or not knowing the indicator and the list to explore to find choices"""
        if candidate == to_explore[-1] or len(candidate.split()) > indicator + 1:
            return True
        return False

    def __find_first_choice_candidate(candidate: str, indicator: str):
        """Returns the more precise candidate for the first choice hidden
        in candidate w.r.t the indicator"""
        return " ".join(candidate.split()[-indicator:])

    def __to_explore_list(sentence_choice_flat: str, all_separator_spans: List[Tuple[int]]):
        """Returns the list of choice candidates by splitting the sentence given on the
        identified choice separators"""
        sentence_choice_to_split = ""
        index_start = 0
        for separator_span in all_separator_spans:
            sentence_choice_to_split += re.sub(
                r"\s{2}",
                " ",
                sentence_choice_flat[index_start:separator_span[0]] + replacing_symbol
                )
            index_start = separator_span[1]
        to_explore = sentence_choice_to_split.split(replacing_symbol)[:-1]
        return to_explore

    def __find_all_separator_spans(sentence_choice_flat: str, guideline_separators: dict):
        """Returns a list containg the spans (re.Match.span()) of all the choice separators"""
        all_separator_spans = []
        for separator_regex, separator_exceptions_list in guideline_separators.items():
        # for each separator pattern
            flattened_separator_regex = flatten_regex(separator_regex)
            flattened_exceptions_regex = [flatten_regex(exception) for exception in separator_exceptions_list]
            exceptions_pattern = re.compile("|".join(flattened_exceptions_regex))
            match_separator_list = [match for match in re.finditer(flattened_separator_regex, sentence_choice_flat)]
            separator_span_list = []
            for match_separator in match_separator_list:
                start, end= match_separator.span()
                if not exceptions_pattern.pattern or not exceptions_pattern.match(sentence_choice_flat[start:]):
                    # add as separator of choices only if is not part of an associated exception pattern
                    separator_span_list.append((start, end))
            all_separator_spans.extend(separator_span_list)
        all_separator_spans.sort()
        return all_separator_spans


    choices = [last_choice]
    indicator = __set_indicator(last_choice)
    sentence_choice_flat = re.sub(r"\s", " " * 2, sentence_choice) #allows to find two occurences of patterns following
    # each other. (ex: " ou ou " --> "  ou  ou  ")
    all_separator_spans = __find_all_separator_spans(sentence_choice_flat, guideline_separators)
    to_explore = __to_explore_list(sentence_choice_flat, all_separator_spans)
    to_explore.reverse()
    for candidate in to_explore:
        if __is_candidate_first_choice(candidate, to_explore, indicator):
            first_choice_candidate = __find_first_choice_candidate(candidate, indicator)
            if compare_choices(first_choice_candidate, last_choice, compare_choices_threshold):
                choices.append(first_choice_candidate.strip())
            return choices
        choices.append(candidate.strip())
    return choices


def __has_choices(sentence_choice: str, choices: List[str], threshold: float = 0.3):
    """
    Returns whether the sentence supposed to contain the choices truly
    contains them or not knowing the choices found (heuritic)
    (Needs to be improved)

    Parameters:
        sentence_choice (str): The sentence supposed to contain the choices
        choices (List[str]): The choices found in sentence_choice
        threshold (float): A float between 0 and 1 to tune the output
    Returns:
        (bool) : Whether the sentence supposed to contain the choices truly contains them or not
    """
    if len(choices) == 1:
        return False
    guideline_test = ", ".join(choices)
    if lev.distance(sentence_choice, guideline_test) <= threshold * len(sentence_choice):
        return False
    return True


def is_board_exercise(guideline: str):
    """Returns whether the original exercise is displayed as a board or not"""
    raise NotImplementedError


def find_board_column_names(guideline: str):
    """
    Returns the choices when they are column names of a board in the original exercise

    Parameters:
        guideline (str): The guideline of the exercise after extraction
    Returns:
        choices (List[str]) : The choices found in the guideline
    """
    raise NotImplementedError
