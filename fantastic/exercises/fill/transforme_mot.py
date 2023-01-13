import json
import re
from configparser import ConfigParser

from fantastic.exercises.fill.fill import Fill
from fantastic.exercises.utils import text_to_html, have_symbol, replace_separators


class TransformeMot(Fill):
    """exercises consisting of sentences that should be entirely transformed
    thus showing an editable box for each sentence"""

    def __init__(self, json_path: str, config: ConfigParser) -> None:
        Fill.__init__(
            self,
            json_path,
            config,
            template_name="fill",
            output_folder_name="transforme_mot",
        )
        self.tense_indicators = json.loads(
            self.config.get("transforme_mot", "tense_indicators")
        )
        self.verbs_separators = json.loads(
            self.config.get("transforme_mot", "verbs_separators")
        )
        self.long_list_separators = json.loads(
            self.config.get("transforme_mot", "long_list_separators")
        )
        self.fillers = json.loads(self.config.get("transforme_mot", "fillers"))

    def convert_to_html(self):
        """get the raw text and output an html version of it"""

        # we get the data from json
        guideline = super().find_guideline()
        # find additional guideline returns a tuple
        additional_guideline = "".join(super().find_additional_guideline())
        # list of sentences from exercise_text
        sentences = super().find_sentences()

        # there are different types of adaptation to do

        have_tense_indicator = [
            have_symbol(sentences, ti) for ti in self.tense_indicators
        ]
        have_verbs_separator = [
            have_symbol(sentences, vs) for vs in self.verbs_separators
        ]
        have_long_list_separators = [
            have_symbol(sentences, lls) for lls in self.long_list_separators
        ]

        if any(have_tense_indicator) and any(have_verbs_separator):
            # cases like 'a. aller ; dire ➞ 1 re personne du singulier'
            # it concerns only 2 exercises in the Magnard ...
            # if we have a semicolon or comma, that means we have multiple verbs on that sentence
            tense_indicator = self.tense_indicators[have_tense_indicator.index(True)]
            verb_separator = self.verbs_separators[have_verbs_separator.index(True)]
            new_sentences = []

            for sentence in sentences:
                indication = sentence.split(tense_indicator)[
                    1
                ]  # tense and person usually
                # removing the a. or b.
                beginners = re.findall(r"^(\w\W\s*){1,}\s", sentence)
                sentence_beginning = f"{beginners[0]} " if len(beginners) > 0 else ""
                sentence_cleaned = re.sub(r"^(\w\W\s*){1,}\s", "", sentence, 1)
                verbs = sentence_cleaned.split(tense_indicator)[0].split(verb_separator)
                verbs = [verb.replace(" ", "") for verb in verbs]

                for count, verb in enumerate(verbs):
                    if count == 0:
                        new_sentences.append(
                            f"{sentence_beginning}{verb} {tense_indicator} {indication} <br> ➞ … <br>"
                        )
                    else:
                        new_sentences.append(
                            f"{verb} {tense_indicator} {indication} <br> ➞ … <br>"
                        )

            sentences = new_sentences

        elif any(have_long_list_separators):
            # here, everything should probably be separated by ◆
            # each sentence is not an insecable block, we need to recut in true blocks
            new_sentences = []
            # list of lls, lls='◆' usually
            lls = self.long_list_separators[have_long_list_separators.index(True)]

            for sentence in sentences:
                # each insecable block is in fact separated by lls
                splitted_sentences = sentence.split(lls)
                splitted_sentences = list(
                    map(lambda s: s.strip() + " ", splitted_sentences)
                )
                # there is a missing space at the end of sentence
                splitted_sentences[-1] += " "
                # the split on ◆ removed them
                splitted_sentences = list(map(lambda s: s + lls, splitted_sentences))

                have_fillers = [
                    have_symbol(sentences, filler) for filler in self.fillers
                ]

                if any(have_fillers):
                    # concerns only 1 ex of the Magnard...
                    # here, everything should be separated by lls and having ➞ filler
                    splitted_sentences = list(
                        map(
                            replace_separators,
                            splitted_sentences,
                            lls * len(splitted_sentences),
                            [""] * len(splitted_sentences),
                        )
                    )
                else:
                    splitted_sentences = list(
                        map(
                            replace_separators,
                            splitted_sentences,
                            lls * len(splitted_sentences),
                            ["➞ …"] * len(splitted_sentences),
                        )
                    )

                new_sentences += splitted_sentences

            sentences = new_sentences

        elif have_symbol(sentences, "➞"):
            # here, everything should probably be verb ➞ person and tense
            # we add a fill box at the end
            sentences = list(map(lambda s: s + "<br> ➞ …", sentences))

        else:
            # here, we have basic cases like ['a. prénom', 'b. personnage', 'c. montagne']
            # and we have badly extracted xml
            sentences = list(map(lambda s: s + " ➞ …", sentences))

        # we html mark the text of guideline, additional guideline and exercise_text
        guideline = text_to_html([guideline])
        # we want it to be empty if there are no additional guideline
        additional_guideline = (
            text_to_html([additional_guideline]) if additional_guideline != "" else ""
        )
        sentences = text_to_html(sentences, True)

        return guideline, additional_guideline, sentences, None

    def adapt(self):
        """specific adaptation for this type of exercise"""
        super().adapt_html({"…": "<span contenteditable='true'> </span>"})
        return self
