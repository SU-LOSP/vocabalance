#!/usr/bin/env python3
# coding: utf-8

from xml.dom.minidom import parse
from xml.dom import Node
import re
import os
from collections import Counter
from math import log, exp

from nltk.stem.snowball import EnglishStemmer


common_words = ("the all of that and he hath from for this will are is was "
                "which thou have my i when so but his her unto as a their to "
                "in with our we not me be you shall thy it what do thee him "
                "they on no make your by us upon am let then yet here some if "
                "how at give well where them an thus were say too nor than"
               ).split()


def isInSpeech(tag):
    cur = tag
    while cur.parentNode:
        cur = cur.parentNode
        if cur.nodeType != Node.ELEMENT_NODE:
            return True
        if cur.tagName == "stage" or cur.tagName == "speaker":
            return False


def main():
    import sys
    input_play = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir)
    xml = parse(input_play)

    stemmer = EnglishStemmer()

    speaker_speeches = {}
    speaker_words = {}
    for speech in xml.getElementsByTagName("sp"):
        who = speech.getAttribute("who")
        speaker_speeches.setdefault(who, []).append(speech)
        if not who:
            print("Speech without owner!")
            print(speech.toxml())
            print("\n\n\n")
            continue
        words_counter = speaker_words.setdefault(who, Counter())
        for word in speech.getElementsByTagName("w"):
            if not isInSpeech(word):
                continue
            if not word.firstChild:
                print("Word without child:", word.toxml())
                print("in speech: ", speech.toxml())
                print("\n\n\n")
            wordStr = word.firstChild.nodeValue or ""
            wordStr = stemmer.stem(wordStr)
            words_counter.update([wordStr])

    all_words = Counter()
    for counter in speaker_words.values():
        all_words.update(counter)

    speaker_counts = Counter()
    speaker_counts.update({speaker: sum(words.values()) for speaker, words in speaker_words.items()})

    total_words = sum(all_words.values())

    os.chdir(output_dir)

    with open("character-stats.csv", "w") as csv:
        print("Character", "Number of words spoken", "Number of speeches", sep=",", file=csv)
        for speaker, wordcount in speaker_counts.items():
            print(speaker, wordcount, len(speaker_speeches[speaker]), sep=",", file=csv)

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
    with open("speaker-words.csv", "w") as csv, open("significance-graph.txt", "w") as txt:
        print("Character", "Word", "Count", "Significance", sep=",", file=csv)
        for speaker, word, value in sorted(output, key=lambda x: (x[0], x[2]), reverse=True):
            value *= 10
            if value > threshold:
                print(speaker.ljust(20), word.ljust(20), str(speaker_words[speaker][word]).ljust(5), "+" * int(value-threshold))
                print(speaker.ljust(20), word.ljust(20), str(speaker_words[speaker]).ljust(5), "+" * int(value-threshold), file=txt)
            print(speaker, word, speaker_words[speaker][word], value, sep=",", file=csv)

if __name__ == '__main__':
    main()
