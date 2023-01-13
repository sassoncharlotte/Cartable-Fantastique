from typing import List
import re
from fantastic.exercises.utils import (
    compute_separators_pattern_black,
    compute_separators_pattern_white,
    has_symbols,
    has_to_fill,
    has_sentence
)

def find_choices_in_sentences(
    sentences: List[str],
    non_symbols: List[str],
    non_fill_chars: List[str],
    replacing_symbol: str = "§",
    split_chars: List[str] = None,
    exceptions_list: List[str] = None,
):
    """
    Returns the choices found in the sentences of the exercise text

    Parameters:
        sentences (List[str]): A list of the sentences composing the exercise_text
        non_symbols (List[str]): A list of symbols characters considered as non symbols
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        replacing_symbol (str) (default: "§"): A string to specify the symbol replacing all symbols spoted
        in the sentences
        split_chars: (List[str]) (default: None): A list of additional symbols to split on in split_in_pieces
        exceptions_list: (List[str]) (default: None): A list of all the patterns that could be separating the
        choices and not found by default

    Returns:
        choices (List[List[str]]): A list containing lists of choices corresponding each to one sentence
    """
    pieces_with_choices = []
    for sentence in sentences:
        sentence_split = split_in_pieces(sentence, split_chars)
        sentence_split.reverse()  # done to not identify "a." as the piece with the choices
        sentence_replace = [
            replace_symbols(piece, non_symbols, replacing_symbol)
            for piece in sentence_split
        ]
        for piece in sentence_replace:
            if has_choices(piece, non_fill_chars, non_symbols, replacing_symbol):
                pieces_with_choices.append(piece)
                break
    choices = __process_pieces(
        pieces_with_choices, non_fill_chars, exceptions_list, replacing_symbol
    )
    return choices


def split_in_pieces(sentence: str, split_chars: List[str] = None):
    """
    Returns the different pieces in which the choices of a given sentence could possibly be hidden
    (based on hypothesis that only one piece hold the choices)

    Parameters:
        sentence (str): The sentence to split
        split_chars: (List[str]) (default: None): A list of additional symbols to split on to seperate the pieces

    Returns:
        pieces (List[str]): A list containing the different pieces in which the choices of a given sentence
        could possibly be hidden
    """
    if split_chars:
        pattern = compute_separators_pattern_white([r"[.?!»]\s"] + split_chars)
    else:
        pattern = compute_separators_pattern_white([r"[.?!»]\s"])
    end_pieces = pattern.findall(sentence)
    pieces = pattern.split(sentence)
    for i, end_piece in enumerate(end_pieces):
        pieces[i] = pieces[i] + end_piece[0]
    return pieces


def replace_symbols(chars: str, non_symbols: List[str] = None, replacing_symbol: str = "§"):
    """
    Returns a string in which the symbols have been replaced by a unique replacing symbol
    Moreover all occurences of the first & last found symbols are replaced instead by 2 replacing
    symbols (the replacing symbol should never be found in an original sentence)
    (ex: "word1 (choice1/choice2) word2" --> "word1 §§choice1§choice2§§ word2")

    Parameters:
        chars (str): The string to process
        non_symbols (List[str])(default: None): A list of symbols characters considered as non symbols
        replacing_symbol (str) (default: "§"): A string to specify the symbol replacing all symbols
        spoted in the sentences

    Returns:
        replaced_chars (str): The string in which symbols have been replaced
    """
    replacing_symbol = re.escape(replacing_symbol)
    pattern_symbols = compute_separators_pattern_black(non_symbols)
    all_symbols = pattern_symbols.findall(chars)
    if not all_symbols:
        return chars
    first_last_symbols = [re.escape(all_symbols[0]), re.escape(all_symbols[-1])]
    pattern_without_first_last = compute_separators_pattern_black(non_symbols + first_last_symbols)
    replaced_chars = pattern_without_first_last.sub(replacing_symbol, chars)
    replaced_chars = re.sub("|".join(first_last_symbols), replacing_symbol * 2, replaced_chars)
    return replaced_chars


def has_choices(piece: str, non_fill_chars: List[str], non_symbols: List[str], replacing_symbol: str = "§"):
    """
    Returns whether the piece in which symbols have been replaced by a replacing
    symbol holds the choices or not.

    Parameters:
        piece (str): A String potentially holding the choices of the corresponding sentence
        non_symbols (List[str]): A list of symbols characters considered as non symbols
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        replacing_symbol (str) (default: "§"): A string to specify the symbol replacing all symbols spoted
        in the sentences

    Returns:
        (bool): A boolean representing whether the piece holds the choices or not
    """
    pattern_choices_separator = re.compile(re.escape(replacing_symbol) * 2)
    if pattern_choices_separator.search(piece):
        for elem in pattern_choices_separator.split(piece):
            if not has_to_fill(elem,non_fill_chars):
    #  §§ separating words with no fill symbol => §§ separating choices
                return True
    if not has_symbols(piece, non_symbols):
    #  no symbols => separators are of another form (__handle_exception)
        return True
    return False


def __process_pieces(
    pieces: List[str],
    non_fill_chars: List[str],
    exceptions_list: List[str] = None,
    replacing_symbol: str = "§",
):
    """
    Returns the choices found in the each piece of pieces

    Parameters:
        pieces (List[str]): A list of the pieces containing the choices
        non_fill_chars (List[str]): A list of fill symbols characters considered as non symbols
        exceptions_list: (List[str]) (default: None): A list of all the patterns that could be separating
        the choices and not found by default
        replacing_symbol (str) (default: "§"): A string to specify the symbol replacing all symbols spoted
        in the sentences

    Returns:
        processed (List[List[str]]): A list containing lists of choices corresponding each to one piece
    """

    def __handle_exception(piece: str, pattern_exception: re.Pattern, replacing_symbol: str = "§"):
        """
        Returns the piece after replacing the exception patterns separating choices by a unique symbol
        easier to split on

        Parameters:
            piece (str): The string to process
            pattern_exception (re.Pattern): A pattern that contains all the exceptions patterns
            replacing_symbol (str) (default: "§"): A string to specify the symbol replacing all symbols
            spoted in the sentences

        Returns:
            piece (str): The piece after replacing the given exception patterns by the replacing symbol
        """
        escaped_repl = re.escape(replacing_symbol)
        not_escaped_repl = r"[^" + escaped_repl + r"]"
        regex_has_not_exception = not_escaped_repl + escaped_repl + not_escaped_repl
        if not re.search(regex_has_not_exception, piece):
            if pattern_exception.search(piece):
                piece = pattern_exception.sub(escaped_repl, piece)
        return piece

    pre_processed = []
    escaped_repl = re.escape(replacing_symbol)
    pattern_repl = re.compile(escaped_repl * 2)
    pattern_exception = compute_separators_pattern_white(exceptions_list)
    for piece in pieces:
        if piece:
            # exceptions separators replaced by a unique symbol
            piece = __handle_exception(piece, pattern_exception, replacing_symbol)
            if has_to_fill(piece, non_fill_chars + [replacing_symbol]) or has_sentence(piece):
                # choices of the form "word1 ... word2 (choices1/choice2)." or "word1 (choices1/choice2) choice2."
                regex_choices = escaped_repl * 2 + r".+?" + escaped_repl * 2
                pieces_to_split = [
                    re.sub(escaped_repl, escaped_repl * 2, match[2:-2]) # §§choice1§choice2§§ --> choice1§§choice2
                    for match in re.findall(regex_choices, piece)
                    ]
                if not pieces_to_split:
                # choices of the form choice1/choice2 word3 word4 etc.
                    pieces_to_split = find_choices_by_font(piece)
            elif not piece[-1].isalnum():
                # choices of the form "choice1 sep choice2 (split_char)"
                pieces_to_split = [re.sub(escaped_repl, escaped_repl * 2, piece[:-1].strip())]
            else:
                # ready to be splitted
                pieces_to_split = [piece]
            pre_processed.extend(pieces_to_split) #can add many couples of choices from one piece
    return [pattern_repl.split(piece) for piece in pre_processed]


def find_choices_by_font(piece: str):
    """Returns the choices in the piece of sentence by analysing the font"""
    raise NotImplementedError
