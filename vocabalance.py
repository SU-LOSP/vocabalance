#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup
import re
from collections import Counter
from math import log, exp


common_words = ("the all of that and he hath from for this will are is was "
                "which thou have my i when so but his her unto as a their to "
                "in with our we not me be you shall thy it what do thee him "
                "they on no make your by us upon am let then yet here some if "
                "how at give well where them an thus were say too nor than"
                ).split()


def is_speech_start(tag):
    element_name = tag.attrs.get("name")
    return tag.name == "a" and False if not element_name else element_name.startswith("speech")


class Speech:
    def __init__(self, start):
        self.speaker = start.text
        self.speech = start.findNextSibling("blockquote").text

    def __repr__(self):
        return self.speaker + "\n" + self.speech + "-------\n\n"

    def tokens(self):
        return tokenise(self.speech)

    def interesting_tokens(self):
        return [tok.lower().strip("\n ,!?.–;:\t-") for tok in self.tokens() if tok.strip("\n ,!?.–;:\t-")]


def get_speeches(soup):
    return [Speech(start) for start in soup.find_all(is_speech_start)]


token_delim_re = re.compile('([\n ,!?.–;:\t-]+|--)')
def tokenise(string):
    return [tok.strip("' \t\n") for tok in token_delim_re.split(string) if tok]


def main():
    import sys
    play = sys.argv[1]
    soup = BeautifulSoup(open("mit-plays/" + play + ".html", "r").read(), "html5lib")

    speeches = get_speeches(soup)

    speaker_words = {}
    for speech in speeches:
        speaker = speech.speaker
        if speaker not in speaker_words:
            speaker_words[speaker] = Counter()
        speaker_words[speaker].update(speech.interesting_tokens())

    all_words = Counter()
    for counter in speaker_words.values():
        all_words.update(counter)

    speaker_counts = Counter()
    speaker_counts.update({speaker: sum(words.values()) for speaker, words in speaker_words.items()})

    total_words = sum(all_words.values())

    with open("reports/"+play+"-amounts.csv", "w") as csv:
        print("Character", "Number of words spoken", "Number of speeches", sep=",", file=csv)
        for speaker, wordcount in speaker_counts.items():
            print(speaker, wordcount, len([speech for speech in speeches if speech.speaker == speaker]), sep=",", file=csv)
            sorted(speaker_counts.items(), key=lambda x: x[1])

    speaker_speeches = Counter()
    for speech in speeches:
        speaker_speeches[speech.speaker] += 1

    sorted(speaker_speeches.items(), key=lambda x: x[1])

    with open("reports/" + play + "-numbers.csv", "w") as csv:
        for speaker in speaker_speeches:
            print(speaker, speaker_speeches[speaker], speaker_counts[speaker], sep=",", file=csv)

    def stat(word, speaker):
        word_likelihood = (all_words[word]) / total_words
        speaker_likelihood = speaker_counts[speaker] / total_words
        word_speaker_likelihood = speaker_words[speaker][word] / all_words[word]
        return word_speaker_likelihood * (-log(speaker_likelihood)) * log(all_words[word])

    output = []
    for speaker, words in speaker_words.items():
        if speaker_counts[speaker]/total_words > 0.01:
            output.extend(((speaker, word, stat(word, speaker))
                           for word in words
                           if 3 < all_words[word]
                           and word not in common_words))

    threshold = 11
    with open("reports/" + play + ".csv", "w") as csv, open("reports/" + play + ".txt", "w") as txt:
        print("Character", "Word", "Count", "Significance", sep=",", file=csv)
        for speaker, word, value in sorted(output, key=lambda x: (x[0], x[2]), reverse=True):
            value *= 10
            if value > threshold:
                print(speaker.ljust(20), word.ljust(20), str(speaker_words[speaker][word]).ljust(5), "+" * int(value-threshold))
                print(speaker.ljust(20), word.ljust(20), str(speaker_words[speaker]).ljust(5), "+" * int(value-threshold), file=txt)
            print(speaker, word, speaker_words[speaker][word], value, sep=",", file=csv)

if __name__ == '__main__':
    main()
