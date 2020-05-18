# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# sentiment.py
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Jackson Hambridge
# CMSC 416 Spring 2020
# 4/14/2020
#
# This program predicts word sentiment on tweets. It trains
# on a file of tweets and will predict another file of tweets.
# It uses bag of words as a feature.
# 
# Sentences can have different sentiment depending on context.
# This program attempts to predict sentiment.
# 
# One example of how the program can run:
# py sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt > my-sentiment-answers.txt
# It will output the bag of words and discriminative values
#
# The algorithm uses Decision Lists to sort each type of feature and feature
# to assign discriminative values. The most discriminative features will be used
# first to predict the sense.
#

import sys
import re
import copy
import math

# Sentiment Analysis

# Find the most descriminative word in a sentence
def findBestFeature(discriminativeDictionary,sentence):
    maximum=0
    bestWord="Test_failure_ejvkhmrn"

    sentence=sentence.split()

    for word in sentence:
        if word in discriminativeDictionary:
            if discriminativeDictionary[word]["discriminative"]>maximum:
                maximum = discriminativeDictionary[word]["discriminative"]
                bestWord=word
    return bestWord


# Gather command line arguments
if len(sys.argv) == 1:
    trainingFile="sentiment-train.txt"
    testFile="sentiment-test.txt"
    modelFile="my-model.txt"
elif len(sys.argv) == 2:
    trainingFile=sys.argv[1]
    testFile="sentiment-test.txt"
    modelFile="my-model.txt"
elif len(sys.argv) == 3:
    trainingFile=sys.argv[1]
    testFile=sys.argv[2]
    modelFile="my-model.txt"
else:
    trainingFile=sys.argv[1]
    testFile=sys.argv[2]
    modelFile=sys.argv[3]

# Read training file
file=open(trainingFile,'r',encoding = 'utf-8')
trainingCorpus=file.read().lower()
file.close()

trainingCorpus=str.split(trainingCorpus,"</instance>")

bagOfWords={
}

sentimentCount={
    "positive":0,
    "negative":0
}

# Loop through corpus
for elements in trainingCorpus:
    # If the instance id is on this line, split it by \n
    if "<instance id=" in elements:
        elements=str.split(elements,"\n")
        n=0
        while n < len(elements):
            line=elements[n]
            # If the ID is on this line, gather ID
            if "<instance id=" in line:
                instanceID=line
                instanceID=re.sub("<instance id=\"","",instanceID)
                instanceID=re.sub("\">","",instanceID)
            # If sentiment is on this line, gather sentiment
            if "sentiment=" in line:
                sentiment=line
                sentiment=re.sub(".*sentiment=\"","",sentiment)
                sentiment=re.sub("\"/>","",sentiment)
                sentimentCount[sentiment]+=1
            # If head is on this line, calculate bag of words
            if "<context>" in line:
                line=elements[n+1]

                context=str.split(line)
                
                sentenceStart=0
                sentenceEnd=len(context)

                for word in context:
                    if word not in bagOfWords:
                        bagOfWords[word]={sentiment:1}
                    elif sentiment not in bagOfWords[word]:
                        bagOfWords[word][sentiment]=1
                    else:
                        bagOfWords[word][sentiment]+=1

                # Calculate words and add them to dicitonary bagOfWords
            
            n+=1

# Get all feature types and words in the bag of words
discriminativeDictionary=copy.deepcopy(bagOfWords)

# Loop through and calculate the discriminative
for words in bagOfWords:
    if "positive" in bagOfWords[words] and "negative" in bagOfWords[words]:
        discriminativeDictionary[words]["discriminative"]=abs(math.log( ( bagOfWords[words]["positive"] )/( bagOfWords[words]["negative"] ) ))
        if bagOfWords[words]["positive"] > bagOfWords[words]["negative"]:
            discriminativeDictionary[words]["bestSentiment"]="positive"
        elif bagOfWords[words]["positive"] < bagOfWords[words]["negative"]:
            discriminativeDictionary[words]["bestSentiment"]="negative"
    else:
        # If "negative" doesn't exist
        if "positive" in bagOfWords[words]:
            discriminativeDictionary[words]["discriminative"]=10000*bagOfWords[words]["positive"]
            discriminativeDictionary[words]["bestSentiment"]="positive"
            bagOfWords[words]["negative"]=0
        # If "positive" doesn't exist
        else:
            discriminativeDictionary[words]["discriminative"]=10000*bagOfWords[words]["negative"]
            discriminativeDictionary[words]["bestSentiment"]="negative"
            bagOfWords[words]["positive"]=0



# Read the test file
file=open(testFile,'r',encoding = 'utf-8')
testingCorpus=file.read().lower()
file.close()

testingCorpus=str.split(testingCorpus,"</instance>")

sentimentDict={}

# Follow a similar algorithm to calculate instance and sense
for elements in testingCorpus:
    # If the instance id is on this line, split it by \n
    if "<instance id=" in elements:
        elements=str.split(elements,"\n")
        n=0
        while n < len(elements):
            line=elements[n]
            # If the ID is on this line, gather ID
            if "<instance id=" in line:
                instanceID=line
                instanceID=re.sub("<instance id=\"","",instanceID)
                instanceID=re.sub("\">","",instanceID)
            # If sentiment is on this line, gather sentiment
            if "sentiment=" in line:
                sentiment=line
                sentiment=re.sub(".*sentiment=\"","",sentiment)
                sentiment=re.sub("\"/>","",sentiment)
            # If head is on this line, calculate features
            if "<context>" in line:
                line=elements[n+1]
                sentence=line
                context=str.split(line)
                tempDiscriminativeDictionary=copy.deepcopy(discriminativeDictionary)
                
                found=0
                # Loop until a prediction is found
                while found == 0:
                    # Calculate best feature
                    bestWord=findBestFeature(tempDiscriminativeDictionary,sentence)

                    # If there is absolutely no best feature
                    if bestWord == "Test_failure_ejvkhmrn":
                        if sentimentCount["positive"] > sentimentCount["negative"]: #Majority sense
                            bestSentiment="positive"
                        else:
                            bestSentiment="negative"
                        sentimentDict[instanceID]=bestSentiment
                        found=1
                    else:
                        found=1
                        
                        # Add it to our dictionary
                        bestSense=discriminativeDictionary[bestWord]["bestSentiment"]
                        sentimentDict[instanceID]=bestSense

            n+=1

# Output the Decision List
f = open(modelFile, "w")
f.write(str(discriminativeDictionary))
f.close()

# Print senseDict to standard output
for instance in sentimentDict:
    print("<answer instance=\"" + instance + "\" sentiment=\"" + sentimentDict[instance] + "\"/>")
