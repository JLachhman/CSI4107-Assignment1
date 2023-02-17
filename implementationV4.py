import os
import re
import string
import PorterStemmer

# Records the frequency of processed tokens found throughout the entire corpus
corpusTermFrequency = dict()

# Records the names of all documents in the corpus and the unique tokens contained in each
corpusDocumentVocabulary = dict()

# Reference to a list of stopwords provided by the professor in the assignment outline
stopwords = []
stopwordsFile = open("stopwords.txt", "r")
for words in stopwordsFile:
    stopwords.append(words)

# During the preprocessing stage, the first pass over the documents is
# conducted where each file is tokenized and stemmed, and unimportant
# HTML tags, punctuation, stopwords, and all text after the first paragraph
# is removed

def preprocessing():
    '''
    '''
    processedDoc = dict()
    documentID = ''
    # Pulls all files from collection folder
    for filenames in os.listdir("test_coll"):
        path = 'test_coll\\' + filenames
        # Pulls one file from set of files
        with open(path, "r") as file:
            lines = file.readlines()
            textTagReached = False # For indicating that <TEXT> HTML tag has been reached
            firstParagraphReached = False # For indicating that the first paragraph after <TEXT> HTML tag has been reached
            unpreprocessedWords = [] # List of unpreprocessed words
            # Parsing line-by-line begins
            for line in lines:
                # Checks if each line is non-empty before parsing
                if line.strip() == "":
                    continue
                # Checks for <DOCNO></DOCNO> HTML tags and removes them but saves the content between them
                elif (line.find('<DOCNO>') != -1):
                    line = re.sub('<DOCNO>'|'</DOCNO>', '', line)
                    line = line.strip()
                    documentID = line
                # Checks for <HEAD></HEAD> HTML tags and removes them but preprocesses the content between them
                elif (line.find('<HEAD>') != 1):
                    line = re.sub('<HEAD>'|'</HEAD>', '', line)
                    line = line.strip()
                    # Removes punctuation
                    line = line.translate(str.maketrans('', '', string.punctuation))
                    headerWords = line.split()
                    for words in headerWords:
                        unpreprocessedWords.append(words) 
                # Checks for <TEXT> and sets the flag enabling the preprocessing of the first text paragraph
                elif (line.find('<TEXT>') != -1):
                    textTagReached = True
                    break
                # Checks that we have entered the first paragraph to start adding words to the list of unpreprocessed words
                elif (textTagReached and not firstParagraphReached):
                    firstParagraphReached = True
                    line = line.strip()
                    for words in line:
                        unpreprocessedWords.append(words)
                # Checks that the second paragraph has not been entered by checking for whitespace presence referring to an indent
                elif (textTagReached and firstParagraphReached):
                    if (line==line.strip()):
                        for words in line:
                            unpreprocessedWords.append(words)
                    else:
                        # Checks unpreprocessed words for stopwords, non-alphanumerical strings,
                        # and stems the input string using PorterStemmer tool which returns the
                        # document's vocabulary
                        for word in unpreprocessedWords:
                            if (word in stopwords or not word.isalpha()):
                                continue
                            # Using PorterStemmer library, each stemmed word is added to corupus vocabulary
                            # if not present, and its term frequency is incremented
                            try:
                                ps = PorterStemmer()
                                stemmed = ps.stem(word)
                                corpusTermFrequency[stemmed] += 1
                                corpusDocumentVocabulary[documentID].append(stemmed) 
                                # Each term will be a novel encounter at some point, which will throw a KeyError
                                # because the term index in need of accessing does not exist yet. In that case,
                                # the term frequency is not incremented, instead it is given a value of 1 and an
                                # index in the document vocabulary
                            except KeyError:
                                stemmed = ps.stem(word)
                                corpusTermFrequency[stemmed] = 1
                                try:
                                    corpusDocumentVocabulary[documentID].append(stemmed)
                                except:
                                    corpusDocumentVocabulary[documentID] = [stemmed]
                        # The document preprocessing ends after the first paragraph of text is read
                        # to help with efficiency
                        break
    return index(corpusDocumentVocabulary, corpusTermFrequency)

def index(corpusDocumentVocabulary, corpusTermFrequency):
    '''
    An inverted index can be constructed using nested dictionaries where each key is a token
    in the vocabulary from the preprocessing function, and the value represents the document 
    frequency which points to a 2D-array storing the document, and term frequency in that document
    '''

    invertedIndex = dict()
    sortedVocabulary = sorted(corpusTermFrequency.keys())
    termsPerDocument = corpusDocumentVocabulary.values()


    for token in sortedVocabulary:
        # Each token points to a dictionary
        invertedIndex[token] = dict()
        # Each token's dictionary has a key representing a token's document frequency
        documentFrequency = 0
        for term in termsPerDocument:
            if token == term:
                documentFrequency += 1

        invertedIndex[token][documentFrequency] = [documentID, termFrequency]
        # Each token's dictionary has a value represented by a 2D-array that contains
        # a document id containing the term, and the term frequency for that document

    # df represents the document frequency, that is how many documents consist of a specific token
    tokens = corpusTermFrequency.items()
    for token in tokens:
        print()
