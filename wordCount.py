#Bryan Figueroa
#Assignment 1
import sys
import re
import os
import string 

if len(sys.argv) is not 3:
    print("Correct usage: wordCount.py <input text file> <output file>")
    exit()

inputFname = sys.argv[1]
outputFname = sys.argv[2]
listOfWords = list()

if not os.path.exists(inputFname):
    print ("text file input %s doesn't exist! Exiting" % inputFname)
    exit()


with open(inputFname,"r") as fileReader:
	lines = fileReader.readlines()
	for line in lines:
		for punc in string.punctuation:
			line = line.replace(punc,' ')
		words = line.split()
		for word in words:
			listOfWords.append(word.lower())


listOfWords.sort()

currentWord = listOfWords.pop(0)
counter = 1
writeFile = open(outputFname,"w")

for nextWord in listOfWords:
	if currentWord == nextWord:
		counter = counter + 1
	else:
		writeFile.write(currentWord+" "+str(counter)+"\n")
		currentWord = nextWord
		counter = 1

writeFile.write(currentWord+" "+str(counter)+"\n")
writeFile.close()

