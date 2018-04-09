#Tristan Basil
#Assignment: Project 5 - cS460G Machine Learning, Dr. Harrison

#https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary --> for getting max key of a dictionary

import sys
import copy
import math

#this class is only designed to work for the data in this project.
class BayesNet:
    debug = False
    inputs = list()
    classLabelList = list()
    classLabels = ['hamlet', 'juliet', 'macbeth', 'romeo']
    wordDict = dict()
    totalWordsCounts = dict()
    wordFrequencyDict = dict()
    NUM_CLASSES = 4
    totalWords = 0
    totalCorrect = 0
    testWords = 0

    #initialization takes 4 filenames (one for each class)
    def __init__(self, hamletFile, julietFile, macbethFile, romeoFile, debug):
        self.debug = debug
        fileList = list()
        file1 = None
        file2 = None
        file3 = None
        file4 = None
        try:
            fileList.append(open(hamletFile, "r"))
            fileList.append(open(julietFile, "r"))
            fileList.append(open(macbethFile, "r"))
            fileList.append(open(romeoFile, "r"))
        except:
            print('file not found')
            exit(-1)

        #for each line in each file, parse the inputs.
        for i in range(self.NUM_CLASSES):
            lineIndex = 0
            file = fileList[i]
            self.wordDict[self.classLabels[i]] = dict()
            self.wordFrequencyDict[self.classLabels[i]] = dict()
            self.totalWordsCounts[self.classLabels[i]] = 0
            for line in file:
                parsedLine = line.rstrip().split(' ')
                for tokenIndex in range(len(parsedLine)-1):
                    token = (parsedLine[tokenIndex], parsedLine[tokenIndex+1])
                    #initialize the dictionary entry if it doesn't exist
                    if token not in self.wordDict[self.classLabels[i]]:
                        self.wordDict[self.classLabels[i]][token] = 0
                        self.wordFrequencyDict[self.classLabels[i]][token] = 0
                    self.wordDict[self.classLabels[i]][token] += 1
                    self.wordFrequencyDict[self.classLabels[i]][token] += 1
                    self.totalWordsCounts[self.classLabels[i]] += 1
                    self.totalWords+=1

        #go back and set the probabilities.
        for i in range(self.NUM_CLASSES):
            currentDict = self.wordDict[self.classLabels[i]]
            for token in currentDict:
                currentDict[token] = float(currentDict[token]) / self.totalWordsCounts[self.classLabels[i]]

    #test against a given file and class
    def test(self, filename, classLabel):
        file = None
        try:
            file = open(filename, "r")
        except:
            print('file not found')
            exit(-1)
        successes = 0
        total = 0
        for line in file:
            parsedLine = line.rstrip().split(' ')
            prediction = ''
            maxProbability = -1000000000000
            for i in range(self.NUM_CLASSES):
                probability = 0.0
                for tokenIndex in range(len(parsedLine)-1):
                    #make the bigram
                    token = (parsedLine[tokenIndex], parsedLine[tokenIndex+1])
                    if token in self.wordDict[self.classLabels[i]]:
                        probability += math.log(self.wordDict[self.classLabels[i]][token], 2)
                    #use a pseudocount if the word exists in a different dictionary.
                    elif self.inOtherDict(token, i):
                        probability += math.log(( 1.0 / (self.totalWordsCounts[self.classLabels[i]] + len(parsedLine)) ), 2)
                    #otherwise, ignore it.
                
                #add in the base probability.
                probability += math.log((float(self.totalWordsCounts[self.classLabels[i]])/self.totalWords), 2)
                if probability > maxProbability:
                    maxProbability = probability
                    prediction = self.classLabels[i]

            if prediction == classLabel:
                successes += 1
                self.totalCorrect+=1
            total+=1
            self.testWords+=1

        print 'Accuracy for', classLabel, successes, 'out of', total, (float(successes)/total)

    def inOtherDict(self, token, currentIndex):
        for i in range(self.NUM_CLASSES):
            if i != currentIndex and token in self.wordDict[self.classLabels[i]]:
                return True

    def predictiveKeyboard(self, classLabel, startingWord):
        bestOptions = list()
        sortedDict = None
        #if they don't provide a starting word, give them the 5 best words in general.
        if startingWord == None:
            #consolidate these probabilities - right now they're all split along bigrams.
            dictCopy = dict()
            for key in self.wordDict[classLabel]:
                if key[0] not in dictCopy:
                    dictCopy[key[0]] = 0
                dictCopy[key[0]]+=self.wordFrequencyDict[classLabel][key]

            while len(bestOptions) < 5:
                bestKey = max(dictCopy, key=dictCopy.get)
                if bestKey not in bestOptions:
                    bestOptions.append(bestKey)
                del dictCopy[bestKey]

        #otherwise, find the next possible words and build out a list of the best 5.
        else:
            #get a dict of possible words, and keep a tally of the total number of instances to calculate the probability of each.
            possibleWords = dict()
            totalPossibilityCount = 0
            for key in self.wordDict[classLabel]:
                if key[0] == startingWord:
                    if key not in possibleWords:
                        possibleWords[key] = 0.0
                    possibleWords[key]+=self.wordFrequencyDict[classLabel][key]
                    totalPossibilityCount+=self.wordFrequencyDict[classLabel][key]

            #lastly, take the top 5 best possibilities.
            dictCopy = copy.deepcopy(possibleWords)
            bestOptions = list()
            while len(bestOptions) < 5 and len(dictCopy) > 0:
                bestKey = max(dictCopy, key=dictCopy.get)
                #we'll give an end of line option at the end.
                if bestKey[1] != '<eol>':
                    bestOptions.append(bestKey[1])
                del dictCopy[bestKey]

            #if we don't have 5 possibilities, fill in the rest with the best possibilities from the base dictionary.
            basePossibilities = self.predictiveKeyboard(classLabel, None)
            index = 0
            while len(bestOptions) < 5:
                if basePossibilities[index] not in bestOptions:
                    bestOptions.append(basePossibilities[index])
                index+=1
            #give the end of line option.
            bestOptions.append('<eol>')

        return bestOptions

    
def printOptions(possibilities):
    print 'Possibilties:'
    for i in range(len(possibilities)):
        print i, '-', possibilities[i]



def main():
    if (len(sys.argv) != 9):
        print "Takes 8 command line arguments: hamlet, juliet, macbeth, romeo training files, then their respective test files."
        exit(-1)
    hamletTrainFilename = sys.argv[1]
    julietTrainFilename = sys.argv[2]
    macbethTrainFilename = sys.argv[3]
    romeoTrainFilename = sys.argv[4]
    hamletTestFilename = sys.argv[5]
    julietTestFilename = sys.argv[6]
    macbethTestFilename = sys.argv[7]
    romeoTestFilename = sys.argv[8]

    isDebugMode = True
    #initialize the network
    bayesNet = BayesNet(hamletTrainFilename, julietTrainFilename, macbethTrainFilename, romeoTrainFilename, isDebugMode)
    bayesNet.test(hamletTestFilename, 'hamlet')
    bayesNet.test(julietTestFilename, 'juliet')
    bayesNet.test(macbethTestFilename, 'macbeth')
    bayesNet.test(romeoTestFilename, 'romeo')
    print 'Overall accuracy:', bayesNet.totalCorrect, 'out of', bayesNet.testWords, (float(bayesNet.totalCorrect)/bayesNet.testWords)
    for character in bayesNet.classLabels:
        print 'Creating a monologue for', character
        monologue = list()
        for i in range(5):
            line = list()
            currentWord = None
            while currentWord != '<eol>':
                possibilities = bayesNet.predictiveKeyboard(character, currentWord)
                printOptions(possibilities)
                currentWord = possibilities[int(input('Enter the index of the next word: '))]
                line.append(currentWord)
            print 'Line', i, 'for', character, ':',
            for j in range(len(line)):
                print line[j],
            print '\n----------\n'
            monologue.append(line)
        print 'Final monologue for', character, ':'
        for i in range(len(monologue)):
            for j in range(len(monologue[i])):
                print monologue[i][j],
            print ''
        print '\n----------\n'

main()