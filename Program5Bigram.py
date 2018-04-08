#Tristan Basil
#Assignment: Project 4 - cS460G Machine Learning, Dr. Harrison

#https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.matrix.html -> for using a matrix in general
#https://stackoverflow.com/questions/4455076/how-to-access-the-ith-column-of-a-numpy-multidimensional-array -> for getting a vector from a matrix
#https://stackoverflow.com/questions/6088077/how-to-get-a-random-number-between-a-float-range -> for generating random weights


import numpy as np
import sys
import copy
import random
import math
import heapq

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

        #for each line in each file, parse the inputs and class labels into parallel lists.
        
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
                    #print token
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
                    token = (parsedLine[tokenIndex], parsedLine[tokenIndex+1])
                    if token in self.wordDict[self.classLabels[i]]:
                        probability += math.log(self.wordDict[self.classLabels[i]][token], 2)
                        #print classLabel, probability
                    elif self.inOtherDict(token, i):
                        probability += math.log(( 1.0 / (self.totalWordsCounts[self.classLabels[i]] + len(parsedLine)) ), 2)
                    #otherwise, ignore it.
                 
                probability += math.log((float(self.totalWordsCounts[self.classLabels[i]])/self.totalWords), 2)
                #print probability, self.classLabels[i]
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
            dictCopy = copy.deepcopy(self.wordDict[classLabel])
            while len(bestOptions) < 5:
                #sortedDict = sorted(self.wordDict[classLabel].values(), reverse=True)
                bestKey = max(dictCopy, key=dictCopy.get)
                if bestKey[1] != '<eol>' and bestKey[0] not in bestOptions:
                    bestOptions.append(bestKey[0])
                del dictCopy[bestKey]
        #otherwise, find the next possible words and build out a list of the best 5.
        else:
            #get a dict of possible words, and keep a tally of the total number of instances to calculate the probability of each.
            possibleWords = dict()
            totalPossibilityCount = 0
            for key in self.wordDict[classLabel]:
                if key[0] == startingWord:
                    possibleWords[key] = 0.0
                    totalPossibilityCount+=self.wordFrequencyDict[classLabel][key]

            #now that we have the total number of possibilities, we can figure out the probability of selecting each.
            for key in possibleWords:
                possibleWords[key] = float(self.wordFrequencyDict[classLabel][key])/totalPossibilityCount

            #lastly, take the top 5 best possibilities.
            dictCopy = copy.deepcopy(possibleWords)
            bestOptions = list()
            while len(bestOptions) < 5 and len(dictCopy) > 0:
                bestKey = max(dictCopy, key=dictCopy.get)
                bestOptions.append(bestKey[1])
                del dictCopy[bestKey]

            #if we don't have 5 possibilities, fill in the rest with the best possibilities from the base dictionary.
            basePossibilities = self.predictiveKeyboard(classLabel, None)
            index = 0
            while len(bestOptions) < 5:
                if basePossibilities[index] not in bestOptions:
                    bestOptions.append(basePossibilities[index])
                index+=1
        
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
        currentWord = None
        while currentWord != '<eol>':
            possibilities = bayesNet.predictiveKeyboard(character, currentWord)
            printOptions(possibilities)
            currentWord = possibilities[int(input('Enter the index of the next word: '))]
            monologue.append(currentWord)
        print 'Your final monologue for', character, ':'
        for i in range(len(monologue)):
            print monologue[i],
        print '\n----------\n'




    bayesNet.predictiveKeyboard('hamlet', None)
    bayesNet.predictiveKeyboard('hamlet', 'it')

main()