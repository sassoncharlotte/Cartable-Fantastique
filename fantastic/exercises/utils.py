from typing import List, Tuple
import re
import spacy
from spacy.lang.fr import French
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from transformers.pipelines.token_classification import TokenClassificationPipeline


def find_in_dict(json_dict: dict, object_type: type, key: str):
    """
    Returns the value found at the specified string key in json_dict if the value type
    matches the object_type specified, otherwise returns an empty object_type instance

    Parameters:
        json_dict (dict): The dictionnary to explore
        object_type (type): The object type expected at key
        key (str): The wanted key to check
    Returns:
        answer (object_type): the value associated to the key if it exists and instance
        of object_type
    """
    try:
        answer = object_type()
        if not isinstance(json_dict, dict):
            return answer
        if key in json_dict:
            if isinstance(json_dict[key], object_type):
                answer = json_dict[key]
    except TypeError:
        return None
    return answer


def find_symbols(chars: str, non_symbols_chars: List[str] = None):
    """
    Returns the list of unique symbols found in chars knowing the list of symbols
    non expected to be detected

    Parameters:
        chars (str): The string to process
        non_symbols_chars (List[str]): The list of unique symbols not expected to be detected
    Returns:
        candidates (List[str]): The List of unique symbols found in chars
    """
    if non_symbols_chars is None:
        non_symbols_chars = []
    candidates = [c for c in chars if not (c.isalnum()) and c not in non_symbols_chars]
    candidates_set = set(candidates)
    return list(candidates_set)


def replace_symbols(chars: str, symbols: List[str] = None, replacing_symbol: str = "§"):
    """
    Returns A string where all symbols specified have been replaced by a unique replacing
    symbol (The replacing symbol should never be found in a string initially)
    (Use re.sub is better)
    Parameters:
        chars (str): The string to process
        symbols (List[str]): The list of symbols to replace
        replacing_symbol (str): A string to specify the symbol replacing all symbols spoted
        in chars
    Returns:
        replaced_chars (str): The processed string chars
    """
    if symbols is None:
        symbols = []
    number_chars = len(chars)
    replaced_chars = ""
    index = 0
    while index < number_chars:
        is_symbol = False
        for symbol in symbols:
            length_symbol = len(symbol)
            if (
                index <= number_chars - length_symbol
                and chars[index : index + length_symbol] == symbol
            ):
                replaced_chars += replacing_symbol
                is_symbol = True
                index += length_symbol
        if not is_symbol:
            replaced_chars += chars[index]
            index += 1
    return replaced_chars


def multi_split(chars: str, split_chars: List[str], replacing_symbol: str = "§"):
    """
    Returns A list containing all pieces of an input string chars splitted on all
    split characters given
    (Use re.split is better)
    Parameters:
        chars (str): The string to process
        split_chars (List[str]): The list of patterns to split on
        replacing_symbol (str): A string to specify the symbol replacing all patterns spoted
        in chars
    Returns:
        (List[str])
    """
    replaced_chars = replace_symbols(
        chars, split_chars, replacing_symbol
    )  # first we replace the patterns
    # which allows to split on patterns of more than one character like "ou"
    return replaced_chars.split(replacing_symbol)


def text_to_html(text: list, is_exercise: bool = False) -> str:
    """ input: text in the form of list of insecable strings
    output: each word is inside a span with class word, each space in a span with a class space and
            a word and a space inside a class with an id to color words,
            each insecable part in a span with class block
    if we are marking inside an exercise, we want to mark blocks with id"""

    # we generate different ids for each word and each block
    word_id_count: int = 0
    block_id_count: int = 0
    html_output: str = ""

    # we go through each block
    for block in text:

        # if it is a an exercise, we mark block as we'll move them from pages to pages
        if is_exercise:
            html_output += f"<span class='block' id='block{str(block_id_count)}'>"
            block_id_count += 1
        else:
            html_output += "<span class='block'>"

        words_list = block.split(" ")
        for word in words_list:
            if is_exercise:
                html_output += (
                    f"<span id='word{str(word_id_count)}'>\n"
                    + f"<span class='word'>{word}</span>\n"
                    + "<span class='space'> </span>\n </span>\n"
                )
                word_id_count += 1
            else:
                html_output += (
                    f"<span class='word'>{word}</span>"
                    + " <span class='space'> </span>"
                )

        html_output += "<br/></span>"

    return html_output


def find_all_sentences(text: str):
    """
    Returns the list of all the full sentences found in a text
    (full sentence = finished by .,!,? or » and followed by a Capital letter)

    Parameters:
        text (str): The string to process

    Returns:
        sentences (List[str]): The list of full sentences composing the text
    """
    if not text:
        return []
    pattern = re.compile(r"[.?!»]\s[A-Z\W]")
    end_sentences = pattern.findall(text)
    sentences = pattern.split(text)
    if sentences[-1] == str():
        sentences.pop()
    start_sentences = ""
    number_end_sentences = len(end_sentences)
    for i in range(number_end_sentences):
        if end_sentences[i][-1] != "»":  # à préciser
            sentences[i] = (
                start_sentences + sentences[i] + end_sentences[i][:-1]
            ).strip()
            start_sentences = end_sentences[i][-1]
        else:
            sentences[i] = (start_sentences + sentences[i] + end_sentences[i]).strip()
            start_sentences = ""
    if len(sentences) > number_end_sentences:
        sentences[number_end_sentences] = (
            start_sentences + sentences[number_end_sentences]
        ).strip()
    return sentences


def compute_separators_pattern_black(non_separators_chars: List[str] = None):
    """
    Returns a pattern that identifies all symbols except the non separators characters given
    (Black list approach --> See White list approach if more appropriate)

    Parameters:
        non_separators_chars (List[str]): The list of symbols considered as non separators

    Returns:
        pattern (re.Pattern): A regex pattern allowing the detection of separators
    """
    if non_separators_chars is None:
        non_separators_chars = ["'", "’", "?", ".", "!", "-", "–", "…", "«", "»", ";", ":", ","]
    pattern = re.compile(r"[^\w" + re.escape("".join(non_separators_chars)) + "]")
    return pattern


def compute_separators_pattern_white(separators_list: List[str] = None):
    """
    Returns a pattern containing all the patterns given (to give as raw strings)
    (White list approach --> See Black list approach if more appropriate)

    Parameters:
        patterns_list: (List[str]) (default: None): A list of some patterns (to store as raw strings)

    Returns:
        pattern (re.Pattern): A regex pattern containing the patterns given
    """
    if separators_list is None:
        separators_list = [r"\sou\s", r",", r"[-–]"]
    pattern = re.compile("|".join(separators_list))
    return pattern


def search_common_chars(chars_sentences: List[List[str]]):
    """
    Returns the common characters in a list of lists of characters
    (ex: [[".","?"]["?",":"]] --> ["?"])

    Parameters:
        chars_sentences (List[List[[str]]): The list of list of characters to process

    Returns:
        common_chars (List[str]): The list of common characters found
    """
    if not chars_sentences:
        return []
    common_chars = []
    chars_ref = chars_sentences[0]
    for char_ref in chars_ref:
        if all_has_char(char_ref, chars_sentences):
            common_chars.append(char_ref)
    return common_chars


def all_has_char(char_ref: str, chars_sentences: List[List[str]]):
    """
    Returns whether all the list of lists of characters contains the given
    reference character or not

    Parameters:
        char_ref (str): The reference character to look for in chars_sentences
        chars_sentences (List[List[[str]]): The list of list of characters to process

    Returns:
        (bool)
    """
    for chars_sentence in chars_sentences:
        if not char_ref in chars_sentence:
            return False
    return True


def search_common_symbols(sentences: List[str], non_symbols_chars: List[str] = None):
    """
    Returns whether all the list of lists of characters contains the given
    reference character or not

    Parameters:
        char_ref (str): The reference character to look for in chars_sentences
        chars_sentences (List[List[[str]]): The list of list of characters to process

    Returns:
        (bool)
    """
    chars_sentences = []
    pattern = compute_separators_pattern_black(non_symbols_chars)
    for sentence in sentences:
        chars_sentences.append(set(pattern.findall(sentence)))
    return search_common_chars(chars_sentences)


def sep_sentences(sentences: List[str], separators: List[str]):
    """
    Returns a list containing all the pieces composing the exercise by order after
    splitting each sentence on its sperators

    Parameters:
        sentences (List[str]): The sentences to process
        seprators (List[str]): The list of separators to split the sentences in pieces

    Returns:
        pieces (List[str]): The list of ordered pieces obtained by splitting ecah sentence
        one after the other
    """
    pieces = []
    for sentence in sentences:
        for piece in re.split("[" + re.escape("".join(separators)) + "]", sentence):
            pieces.append(piece)
    return pieces


def cut_string(string: str, index_split: Tuple[int], link_string: str = ""):
    """
    Cuts the string at index_split and links the two obtained pieces with a link string
    (ex: ("hello", (0,4), "pop") --> "popo")
    Parameters:
        string (str): The list of the different sentences composing the exercise
        index_split (Tuple[int]]): The tuple (start, end) to split on
        link_string (str) (default: ""): the link string to recompose a new string
    Returns:
        (str)
    """
    return string[: index_split[0]] + link_string + string[index_split[1] :]


def has_symbols(chars: str, non_symbols: List[str] = None):
    """
    Returns whether a string contains a symbol or not given non symbols characters

    Parameters:
        chars (str): The string to process
        non_symbols (List[str])(default: None): A list of symbols characters considered as non symbols

    Returns:
        (bool): A boolean representing whether chars contains symbols or not
    """
    pattern = compute_separators_pattern_black(non_symbols)
    if pattern.search(chars):
        return True
    return False


def has_sentence(text: str):
    """Returns whether a text contains a sentence or not"""
    pattern = compute_separators_pattern_white([r"[.?!]\s", r"[.?!]$"])
    if pattern.search(text):
        return True
    return False


def has_to_fill(text: str, non_fill_chars: List[str] = None):
    """
    Returns whether a string contains a fill symbol or not given non fill symbols characters

    Parameters:
        text (str): The string to process
        non_symbols (List[str])(default: None): A list of symbols characters considered as non symbols

    Returns:
        (bool): A boolean representing whether chars contains symbols or not
    """
    pattern = compute_separators_pattern_black(non_fill_chars)
    if pattern.search(text):
        return True
    return False


def included(list1: list, list2: list):
    """
    Returns whether list1 is included in list2 or not
    """
    for elt in list1:
        if not elt in list2:
            return False
    return True


def flatten_regex(raw_regex: str):
    """
    Returns a flattened regex (replaces spaces and \\s by \\s\\s
    if in the middle of the raw regex given.
    To use when flattening a string and searching in it (doubling white spaces)
    (ex: \\sou\\sbien\\s --> \\sou\\s\\sbien\\s)
    Allows you to match both "ou bien" in " ou  bien  ou  bien " in flattened string
    """
    flattened_regex = re.sub(r"\\s",r"\\s\\s", raw_regex)
    if re.match(r"^\\s", flattened_regex):
        flattened_regex = flattened_regex[2:]
    if re.search(r"\\s$", flattened_regex):
        flattened_regex = flattened_regex[:-2]
    return flattened_regex


def replace_symbols_for_sentences(
    text: str, symbols=[".", "!", "?"], replacing_symbol="$"
) -> str:
    replaced_text = ""

    # replacing all symbols in the text with the replacing symbol
    for char in text[:-1]:
        replaced_text += char
        if char in symbols:
            replaced_text += replacing_symbol

    replaced_text += text[-1]
    return replaced_text


def splits_to_sentences(
    text: str, split_chars=[".", "!", "?"], replacing_symbol="$"
) -> list:
    """Parameters:
    - text: a text.
    - split_chars: the characters we want to split on.
    - replacing_symbol: we replace these characters with this symbol,
    that is supposed to never be found in the text.
    Returns:
    sentences: the list of sentences of the text."""
    replaced_chars = replace_symbols_for_sentences(text, split_chars, replacing_symbol)
    sentences = replaced_chars.split(replacing_symbol)
    return sentences


def generate_nlp_spacy() -> French:
    """Nlp model of spacy"""
    nlp = spacy.load("fr_core_news_sm")
    return nlp


def generate_nlp_gilf() -> TokenClassificationPipeline:
    """Nlp model of hugging face"""
    tokenizer = AutoTokenizer.from_pretrained("gilf/french-postag-model")
    model = AutoModelForTokenClassification.from_pretrained("gilf/french-postag-model")
    nlp_token_class = pipeline(
        "ner", model=model, tokenizer=tokenizer, grouped_entities=True
    )
    return nlp_token_class


def index_words(guideline: str, categories: list) -> list:
    """Returns the indexes of the words that we need to frame and color in the guideline.

    Parameters:
    - guideline
    - categories: the different categories in the guideline
    Returns:
    - word_indexes_list: the list of the indexes of the categories in the guideline
    It has the form: [(n1, n2), (n3, n4) ...] with n1 the number of spaces before the first letter of word1
    and n2 the number of spaces before the last letter of word 1"""

    word_indexs_list = []
    index_dots = guideline.find(":")

    for category in categories:

        # searching for categories after a ":" if there is one, and
        # if not, in the whole guideline
        if index_dots != -1:
            # there is a ":"
            # so we want to search for the categories after the ":"
            index_set = (
                guideline.find(category, index_dots),
                guideline.find(category, index_dots) + len(category) - 1,
            )
        else:
            # we search for the categories in the whole guideline
            index_set = (
                guideline.find(category),
                guideline.find(category) + len(category) - 1,
            )

        word_indexs_list += [
            (guideline[: index_set[0]].count(" "), guideline[: index_set[1]].count(" "))
        ]
    return word_indexs_list


def clean_entities_spaces(entities_list: list) -> list:
    """Removes useless spaces at the extremities of list elements."""
    entities_list_cleaned = [entity.strip() for entity in entities_list]
    return entities_list_cleaned


def replace_starting_from_the_end(
    text: str, old_value: str, new_value: str, count: int
) -> str:
    """Like a replace function but starts from the end."""
    words = text.rsplit(old_value, count)
    return new_value.join(words)


def split_word(word: str, split_characters: str) -> list:
    """Splits the word if it contains any character of split_characters (punctuation, apostrophes...)

    Parameters:
    - word: a part of the text that was between two spaces
    - split characters: punctuation, parentheses, appostrophes,...
    that are not part of the word
    Returns:
    - the word splited so that every element of the list is a selectable entity"""

    if word[0] in split_characters:
        # the first letter of word is a split character (punctuation / apostrophe / ...)
        if len(word) == 1:
            return [word]
        return [word[0]] + split_word(word[1:], split_characters)

    for i in range(len(word) - 1):
        if word[i] in split_characters:
            # the letter at place i in word is in split characters
            splited_word = [word[:i], word[i]] + split_word(
                word[i + 1 :], split_characters
            )
            return splited_word

    if word[-1] in split_characters:
        # the last letter of word is a split characters (punctuation / apostrophe / ...)
        splited_word = [word[:-1], word[-1]]
        return splited_word

    return [word]


def entities_if_symbols(text: str, symbol: str) -> list:
    """Splits the text on the symbol if there is one.

    Parameters:
    - text: A part of the "énoncé"
    - symbol: a symbol that was found in the "énoncé" (like a ⬪)
    Returns:
    - if symbol "": an empty list
    - if not, a list of the selectable entities (the text splited on the symbol)"""

    if symbol:
        # we found some symbols
        entities_list = re.split("(%s)" % symbol, text)

        # searching for the number of the sentence (a., b., etc.)
        if re.search(r"^(\w\W\s){1,3}", entities_list[0]):
            match_object = re.search(r"^(\w\W\s){1,3}", entities_list[0])

            entities_list = [
                entities_list[0][: match_object.end() - 1],
                entities_list[0][match_object.end() :],
            ] + entities_list[1:]

        return entities_list

    return []


def have_symbol(sentences: list, symbol: str) -> bool:
    """tells if any of the sentence has the symbol"""

    return any([sentence.find(symbol) != -1 for sentence in sentences])


def replace_separators(text: str, separators: list, replacer: list) -> str:
    """we replace separators by a replacer"""

    return text.replace(separators, replacer)
