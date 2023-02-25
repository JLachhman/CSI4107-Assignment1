#################################################################################
# Student Name: Jayden Lachhman
# Student Number: 8791694
# Course Code: CSI 4107
# Group Number: 60
# Submission Date: 2023-02-14
#################################################################################

import os
import re
import string
import PorterStemmer
import math

# Records each query
queries = dict()

# Records the maximum term frequency per query
queryMaxFrequency = dict()

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
    TYPE-CONTRACT: () -> dict, dict
    DESCRIPTION: This function reads each document from the folder, and using the <DOCNO>, <HEAD>, and  <TEXT> HTML tags, the
    words content is processed by removing punctuation, ignoring stopwords, and stemmed to create a vocabulary which takes the
    form a dictionary where the corpus term frequency, documents and the tokens they contain post-preprocessing and stored.
    The content after the first paragraph following the openeing <TEXT> HTML tag is ignored for parsing efficiency.
    '''
    documentID = ''

    # EXTRACTS ALL PERTINENT TEXT FROM EACH DOCUMENT

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
                            # Skips stopwords
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
    return indexing(corpusDocumentVocabulary, corpusTermFrequency)

####################################################################################################################################################################################################################

def indexing(corpusDocumentVocabulary, corpusTermFrequency):
    '''
    TYPE-CONTRACT: (dict, dict) -> dict
    DESCRIPTION: An inverted index can be constructed using nested dictionaries where the outside dictionary
    key is a token in the vocabulary from the preprocessing function, and the value (representing
    the inside dictionary) is the document frequency which points to a 2D-array storing the documentID,
    and term frequency in that document
    '''
    invertedIndex = dict()
    sortedVocabulary = sorted(corpusTermFrequency.keys())

    # INVERTED INDEX BUILDER

    for token in sortedVocabulary:
        # Each token points to a dictionary
        invertedIndex[token] = dict()
        # Creating an array to store the Document ID and Term Frequency removes the need for a try/except
        docIDAndTF = []
        documentFrequency = 0
        # The corpus dictionary holds key-value pairs corresponding to document IDs and the array of terms
        # contained in each
        for docID, docTerms in corpusDocumentVocabulary.items():
            termFrequency = 0
            # For each document, if each token has at least one instance, document frequency increments by one
            if token in docTerms:
                documentFrequency += 1
                # Iterating through the total tokens of a document and incrementing a count each time a token
                # matches the desired token in the vocabulary
                for tokens in docTerms:
                    if token==tokens:
                        termFrequency += 1
                # Only add the array to the inverted index's outside dictionary value if the desired token 
                # exists in the document
                docIDAndTF.append([docID, termFrequency])
        # Update inverted index
        invertedIndex[token][documentFrequency] = docIDAndTF

    # CALCULATING CORPUS TF-IDF

    # Removes duplicate terms and creates a dictionary storing document ids and their lengths
    documentVector = dict()
    for docIDs, tokens in corpusDocumentVocabulary.items():
        corpusDocumentVocabulary[docIDs] = list(dict.fromkeys(tokens))
        documentVector[docIDs] = len(corpusDocumentVocabulary[docIDs])

    # Reference to the total number of documents
    totalNumberOfDocuments = len(documentVector.keys())
    
    # Calculating idf values for each word and storing them in dictionary
    for word in invertedIndex.keys():
        df = list(invertedIndex[word].keys())[0]
        sortedVocabulary[word] = math.log(totalNumberOfDocuments/df, 2)

    # Calculating td-idf
    for terms, tf in corpusTermFrequency.items():
        idf = sortedVocabulary[terms]
        tfidf = tf * idf
        sortedVocabulary[terms] = tfidf
    
####################################################################################################################################################################################################################

def rankAndRetrieve():
    
    # EXTRACTS ALL PERTINENT TEXT FROM EACH QUERY

    queryID = ''
    path = "queries.txt"
    with open(path, "r") as file:
        lines = file.readlines()
        for line in lines:
            # Checks if each line is non-empty before parsing
            if line.strip() == "":
                continue
            # Checks for <num> HTML tag and removes it but saves the content after
            elif (line.find('<num>') != -1):
                    line = re.sub('<num>', '', line)
                    line = line.strip()
                    queryID = line
            # Checks for <title> HTML tag and removes it but preprocesses the content after
            elif (line.find('<title>') != 1):
                line = re.sub('<title>', '', line)
                line = line.strip()
                # Removes punctuation
                line = line.translate(str.maketrans('', '', string.punctuation))
                titleWords = line.split()
                for word in titleWords:
                    # Skips stopwords
                    if (word in stopwords or not word.isalpha()):
                        continue
                    # Using PorterStemmer library, each stemmed word is added to query vocabulary
                    # if not present, and its term frequency is incremented
                    try:
                        ps = PorterStemmer()
                        stemmed = ps.stem(word)
                        queries[queryID].append(word)
                        # Each term will be a novel encounter at some point, which will throw a KeyError
                        # because the term index in need of accessing does not exist yet. In that case,
                        # it is given an index in the queryID's vocabulary
                    except KeyError:
                        stemmed = ps.stem(word)
                        try:
                            queries[queryID].append(stemmed)
                        except:
                            queries[queryID] = [stemmed]
                        # The query preprocessing ends after the title is read to help with efficiency
                        break

    # CALCULATE QUERY TF-IDF

    # Stores the maximum term frequency for each query in a dictionary
    for queryID, words in queries.items():
        maxCount = 0
        for word in words:
            frequency = words.count(word)
            if frequency > maxCount:
                maxCount = frequency
        queryMaxFrequency[queryID] = maxCount

    # 
    # for words in query:

    #     queryVector = 