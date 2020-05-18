# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# scorer.py
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Jackson Hambridge
# CMSC 416 Spring 2020
# 4/14/2020 
# 
# This program uses the output from sentiment.py and compares it to a key in order
# to score the prediction from sentiment.py and give a confusion matrix.
# 
# One example of how the program can run:
# py scorer.py my-sentiment-answers.txt sentiment-test-key.txt
# This will output a confusion matrix as well as other information.
# 

import sys
import re

# Gather command line arguments
if len(sys.argv) == 1:
    predictionFile="my-sentiment-answers.txt"
    keyFile="sentiment-key.txt"
elif len(sys.argv) == 2:
    predictionFile=sys.argv[1]
    keyFile="sentiment-key.txt"
else:
    predictionFile=sys.argv[1]
    keyFile=sys.argv[2]

# Read the key
with open(keyFile, 'r') as f:
    keyCorpus=f.read().lower()
f.close()

# Process the key to get instance and sense
keyCorpus=str.split(keyCorpus,"\n")
keyDict={}

for line in keyCorpus:

    if "answer" in line:

        instanceID=line
        instanceID=re.sub(".*instance=\"","",instanceID)
        instanceID=re.sub("\".*","",instanceID)

        senseID=line
        senseID=re.sub(".*sentiment=\"","",senseID)
        senseID=re.sub("\".*","",senseID)

        keyDict[instanceID]=senseID

# Read the predictions
with open(predictionFile, encoding="utf8", errors='ignore') as j:
    predictionCorpus=j.read().lower()
j.close()

# Process the predictions to get instance and sense
predictionCorpus=re.sub("\x00","",predictionCorpus)
predictionCorpus=str.split(predictionCorpus,"\n")
predictionDict={}

for line in predictionCorpus:

    if "answer" in line:
        instanceID=line
        instanceID=re.sub(".*instance=\"","",instanceID)
        instanceID=re.sub("\".*","",instanceID)

        sentiment=line
        sentiment=re.sub(".*sentiment=\"","",sentiment)
        sentiment=re.sub("\".*","",sentiment)

        predictionDict[instanceID]=sentiment

# Set variabless
correct=0
incorrect=0
pos=0
neg=0
accuracy=0
actuallyPos=0
actuallyNeg=0

# Compare prediction and key given an instance
for key in keyDict:
    if predictionDict[key] != "N/A":
        if predictionDict[key] == keyDict[key]:
            correct+=1
            if predictionDict[key] == "positive":
                pos+=1
            else:
                neg+=1
        else:
            incorrect+=1
            if keyDict[key] == "positive":
                actuallyPos+=1
            else:
                actuallyNeg+=1

# Calculate accuracy
accuracy=correct/(correct+incorrect) * 100

# Print information
print()
print("Correct Predictions: " + str(correct))
print("Incorrect Predictions: " + str(incorrect))
print("Predicted positive correctly: " + str(pos))
print("Predicted negative correctly: " + str(neg))
print()
print("Accuracy: " + str(accuracy))
print()
# Print and format confusion matrix
print("        \Actual          positive    negative")
print("Predicted\     positive  "+str(pos)+"         "+str(actuallyNeg))
print("               negative  "+str(actuallyPos)+"          "+str(neg))