"""A language and wording manager for Aria. Only one LanguageManager should be active at a time.
"""

import os
from nltk.corpus import wordnet
from contextlib import redirect_stdout
import autocomplete
import speech_recognition as sr
import markovify

from . import config_utils, io_utils

markov = None
autocomplete = None
loaded_markovs = []

def load_autocomplete_data():
    """Loads autocomplete data from corpora."""
    global autocomplete
    folder_path = config_utils.get("aria_path") + "/data/corpora"
    namefile = folder_path + "/names.txt"
    wordfile1 = folder_path + "/corncob_lowercase.txt"
    wordfile2 = folder_path + "/words_alpha.txt"
    skfile = folder_path + "/sk.txt"
    lyricfile = folder_path + "/lyrics.txt"
    moviefile = folder_path + "/movies.txt"

    with redirect_stdout(open(os.devnull, "w")):
        autocomplete.load()

        names = " ".join(line.strip().lower() for line in open(namefile))
        autocomplete.models.train_models(names)

        words1 = " ".join(line.strip().lower() for line in open(wordfile1))
        autocomplete.models.train_models(words1)

        words2 = " ".join(line.strip().lower() for line in open(wordfile2))
        autocomplete.models.train_models(words2)

        sk = " ".join(line.strip().lower() for line in open(skfile))
        autocomplete.models.train_models(sk)

        lyrics = " ".join(line.strip().lower().replace('"', '').replace("'","") for line in open(lyricfile))
        autocomplete.models.train_models(lyrics)

        movies = " ".join(line.strip().lower().replace('"', '').replace("'","") for line in open(moviefile))
        autocomplete.models.train_models(movies)

        autocomplete.load()
    autocomplete = True


def synset(word):
    """Returns the first synset the given word."""
    return wordnet.synsets(word)[0]

def lemmas(word):
    """Returns the list of lemmas in the first synset of the given word."""
    return synset(word).lemmas()

def synonyms(word):
    """Returns a list of synonyms of the given word."""
    return [str(lemma.name()) for lemma in lemmas(word)]


def antset(word):
    """Returns the set of antonyms of the given word."""
    return lemmas(word)[0].antonyms()


def hyperset(word):
    """
    Returns the set of hypernyms of the given word.
    Hypernyms are more general terms than the supplied word.
    """
    return synset(word).hypernyms()

def hyperset(word):
    """
    Returns a list of hypernyms of the given word.
    Hypernyms are more general terms than the supplied word.
    """
    return [str(lemma.name()) for lemma in hyperset(word).lemmas()]


def hyposet(word):
    """
    Returns the set of hyponyms of the given word.
    Hyponyms are more specific terms than the supplied word.
    """
    return synset(word).hyponyms()

def hyposet(word):
    """
    Returns a list of hyponyms of the given word.
    Hyponyms are more specific terms than the supplied word.
    """
    return [str(lemma.name()) for lemma in hyposet(word).lemmas()]


def holoset(word):
    """
    Returns the set of holonyms of the given word.
    Holonyms are terms describing concepts that the given word has membership within.
    """
    return synset(word).holonyms()

def holoset(word):
    """
    Returns a list of holonyms of the given word.
    Holonyms are terms describing concepts that the given word has membership within.
    """
    return [str(lemma.name()) for lemma in holoset(word).lemmas()]


def define(word):
    """Returns the definition of the given word."""
    return synset(word).definition()

def complete_word(str):
    """Returns a list of possible completions given the current input string."""
    options = []

    str = str.lower()

    if autocomplete == None:
        load_autocomplete_data()
    
    try:
        str_parts = str.split(" ")
        if len(str_parts) >= 2:
            options = autocomplete.predict(str_parts[-2], str_parts[-1])
        else:
            options = autocomplete.predict_currword(str_parts[0])
        return [word[0] for word in options]
    except Exception as e:
        pass
    return []

def complete_line(str):
    global markov
    str = str.strip().lower()
    prediction = ""

    folder_path = config_utils.get("aria_path") + "/data/corpora"
    if markov == None:
        # Load the base markov model -- queries
        query_file = folder_path + "/queries.txt"
        queries = "\n".join(line.strip().lower().replace('"', '').replace("'","") for line in open(query_file))
        markov = markovify.NewlineText(queries, retain_original=False, state_size = 40)
    
    try:
        prediction =  markov.make_sentence_with_start(str)
    except:
        print("\n")
        io_utils.sprint("Please wait as I try to improve my predictive model...")
        while prediction == "":
            if "lyrics" not in loaded_markovs:
                lyric_file = folder_path + "/lyrics.txt"
                lyrics = "\n".join(line.strip().lower().replace('"', '').replace("'","") for line in open(lyric_file))
                markov_lyrics =  markovify.NewlineText(lyrics, retain_original=False, state_size = 40)
                markov = markovify.combine([ markov, markov_lyrics ])
                loaded_markovs.append("lyrics")

            elif "movies" not in loaded_markovs:
                movie_file = folder_path + "/movies.txt"
                movies = "\n".join(line.strip().lower().replace('"', '').replace("'","") for line in open(movie_file))
                markov_movies =  markovify.NewlineText(movies, retain_original=False, state_size = 40)
                markov = markovify.combine([ markov, markov_movies ])
                loaded_markovs.append("movies")

            else:
                io_utils.sprint("Sorry, I do not have a prediction for the rest of that line.")
                break

            try:
                prediction =  markov.make_sentence_with_start(str)
            except:
                pass

    return prediction