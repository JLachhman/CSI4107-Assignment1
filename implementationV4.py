import os

term_frequency = dict()
vocabulary = dict()

stopwords = []
stopwordsFile = open("stopwords.txt", "r")
for words in stopwordsFile:
    stopwords.append(words)

print(stopwords)

# During the preprocessing stage, the first pass over the documents is
# conducted where each file is tokenized and stemmed, and unimportant
# HTML tags, punctuation and stopwords are removed in one pass

def preprocessing():
    # Pulls all files from collection folder
    for filenames in os.listdir("test_coll"):
        path = 'test_coll\\' + filenames
        # Pulls one file from set of files
        with open(path, "r") as file:
            lines = file.readlines()
            # Parsing line-by-line begins
            for line in lines:
                # Checks if each line is non-empty before parsing
                if line.strip() == "":
                    break
                # Checks for <DOCNO></DOCNO> and removes HTML tags but not content
                elif (line.find('<DOCNO>') != -1):
                    line = line.replace('<DOCNO>', '')
                    line = line.replace('</DOCNO>', '')
                elif (line.find('<HEAD>') != 1):
                    line = line.replace('<HEAD>', '')
                    line = line.replace('</HEAD>', '')