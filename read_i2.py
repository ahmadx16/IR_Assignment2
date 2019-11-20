# Without HASH Table
import re
from bs4 import BeautifulSoup
import os, sys
from nltk import PorterStemmer
from collections import defaultdict
path = "../Assignment1/corpus/" 

files = os.listdir(path)
count=0

termId=0
docId=0
uniqueWords=dict()
term_index=[]

print('Opening Documents...\n')

fDoc = open("docid.txt", "w")
fTerm=open("termid.txt","w")
fStoplist = open("stoplist.txt","r")

stopWordList = str(fStoplist.read()).split()
dictStopword= { stopWordList[i] : i for i in range(0, len(stopWordList) ) }
#print(dictStopword)

print('Processing...\n')

for file in files:
    count+=1
    
    if count%100==0:
        print('Documents Processed: ')
        print(count)
        print('\n')
    f = open(r'../Assignment1/corpus/'+file,'r',encoding="utf8",errors='ignore')
    docId+=1
    fDoc.write(str(docId)+"\t"+file+"\n")
    soup = BeautifulSoup(f.read(),"html.parser")
    body = soup.find('body')
    
    if body is None:
        continue
        
        
    for script in body(["script", "style"]):
        script.extract()                        # rip it out

    text = body.get_text()
    
    words= text.lower()   
    words=re.split(r' |,|\n|-|\.|\'|\t|\;|:|\(|\)|\@|\xa0',words) 
    #print(words)
    sword=' '.join(words)
    words = re.findall(r'[A-Za-z0-9]+',sword)
    
    
   
    uw=len(uniqueWords)

    
    wordPosition=0
    for word in words:
        if len(word.strip()) == 1:
            continue
        if word not in dictStopword:
            word= PorterStemmer().stem(word) 

            if word not in uniqueWords:
                uniqueWords[word]=uw
                term_index.append([docId,uw])   # 
                uw+=1
        wordPosition+=1


        #print(term_index)
    if count ==3495:
        fDoc.close()
        #fTerm.close() 
        break
    
print('Processing Completed Successfully\n')
    # print all the Unique words  TERM ID
print('Writing TermIds...\n')   
for key,value in uniqueWords.items():
    fTerm.write(key+'\t'+str(value)+'\n')
print('TermIds written successfully\n')
    
#fDoc.close()
fTerm.close() 


print('Writting Term Indexes...\n')
print(term_index)


t_index.close()



 
        
    
