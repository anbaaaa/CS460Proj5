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
            self.totalWordsCounts[self.classLabels[i]] = 0
            for line in file:
                parsedLine = line.rstrip().split(' ')
                #parsedLine.pop()
                for token in parsedLine:
                    if token not in self.wordDict[self.classLabels[i]]:
                        self.wordDict[self.classLabels[i]][token] = 0
                    self.wordDict[self.classLabels[i]][token] += 1
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
            #parsedLine.pop()
            prediction = ''
            maxProbability = -1000000000000
            for i in range(self.NUM_CLASSES):
                probability = 0.0
                for token in parsedLine:
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

main()