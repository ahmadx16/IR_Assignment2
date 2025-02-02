import sys
from bs4 import BeautifulSoup
from nltk import PorterStemmer
import collections
import os
import math
# read stopwords 

scoreName='Dirichlet'

if len(sys.argv)>=3:
    if sys.argv[1]=='--score':
        scoreName=sys.argv[2]


fStoplist = open("stoplist.txt","r")

stopWordList = str(fStoplist.read()).split()
dictStopword= { stopWordList[i] : i for i in range(0, len(stopWordList) ) }


# Query processing
tIndexFile = open('topics.xml','r')

soup = BeautifulSoup(tIndexFile.read(),'html.parser')
    
queries = soup.findAll('query')

fnewstoplis = []
for query in  queries:
    lisq = str(query.get_text()).split()
    #print(len(lisq))
    newstoplis = []
    for i in range(len(lisq)):
        if lisq[i] not in dictStopword:
            portword = PorterStemmer().stem(lisq[i])
            portword = portword.replace('\'','')
            newstoplis.append(portword)
    fnewstoplis.append(newstoplis)



topIds = []
topics = soup.findAll('topic')  

topIds = [topics[i].get('number') for i in range(len(topics)) ]

querydict = {topIds[i] :fnewstoplis[i] for i in range(len(topIds))}


#  Real relevent 
realRelfile = open('relevance judgements.qrel','r')

realRel = realRelfile.readlines()

qid = 0
releventDocarr={}

for line in realRel:
    linearr = line.split()
    
    
    if int(linearr[0])!=qid:
        qid = int(linearr[0])
        
        if linearr[3]!="0" and linearr[3]!="-2":
            releventDocarr[qid] =[linearr[2]]
        else:
            releventDocarr[qid] =[]

    else:
        if linearr[3]!="0" and linearr[3]!="-2":
            releventDocarr[qid].append(linearr[2])

listdocRel = list(releventDocarr.values())





# file reading 
tIndexFile = open('term_index.txt','r')

lines = tIndexFile.readlines()


path = "../Assignment/corpus/"
files = os.listdir(path)
allDocs =[0 for i in range(len(files)+1)]



termDic={}
flag=0
for line in lines:
    sline = line.split()
    desline = collections.deque(sline)
    did = desline.popleft()
    tot_occ = desline.popleft()
    tot_docs = desline.popleft()

    termDic[did] = [tot_occ,tot_docs]
    lastDocid=0
    termDocsDic={}
    for i in range(len(desline)):
        rowWordspli = desline[i].split(',')
        #print(rowWordspli)
        if rowWordspli[0]!='0':
            lastDocid = lastDocid+int(rowWordspli[0])       # decoding the delta encoding
            termDocsDic[lastDocid] = [int(rowWordspli[1])]
            allDocs[lastDocid]+=1               # count sort type sum
        elif rowWordspli[0]=='0':
            termDocsDic[lastDocid].append(int(rowWordspli[1])+int(termDocsDic[lastDocid][len(termDocsDic[lastDocid])-1]))
            allDocs[lastDocid]+=1
             
    
    termDic[did].append(termDocsDic)    

    #print(termDic)



IDF=[int(vtrow[1])/(len(allDocs)-1) for vtrow in termDic.values() ]


TotalCorpusWords = sum([int(vtrow[0]) for vtrow in termDic.values()])
BackGroundProbability = [int(vtrow[0])/TotalCorpusWords for vtrow in termDic.values()]
AvgDocLen = TotalCorpusWords/(len(allDocs)-1)







tidFile = open('termid.txt','r')
tids = tidFile.readlines()
termId ={}
for tid in tids:
    ttid = tid.split()
    termId[ttid[0]] = ttid[1]
tidFile.close()

didFile = open('docid.txt','r')
dids = didFile.readlines()
dicdids ={}
for did in dids:
    ddid = did.split()
    dicdids[ddid[0]] = ddid[1]
didFile.close()

inv_dicdids = {v: k for k, v in dicdids.items()}



#print(dicdids[str(1)])

qkeys = querydict.keys()
#######  Score Function 1 (BM25)
if scoreName=="BM25":
    scorefilebm = open('scorefilebm.txt','w')
    TablePrecision = open("TablePrecision.txt",'w')
    TablePrecision.write("Query Id"+'\t\t\t'+"P@5"+'\t\t\t'+"P@10"+'\t\t\t'+"P@20"+'\t\t\t'+"P@30"+'\t\t\t'+"MAP" + "\n")
    qkeys = querydict.keys()
    for qkey in qkeys:
        q1 = querydict[qkey]

        CorpScore = [0 for i in range(len(allDocs))]

        k1=  1.2
        k2 = 50
        b = 0.75

        relDocs =[]
        for q in q1:
            qid = termId[q]
            qpos = termDic[qid]                 # getting postings
            relDocs.append(qpos[2].keys())

        #len(termDic[termId[q1[i]]][2][docid]) is term freq
        i=0  
        for doci in relDocs:
            for docid in doci:
                K = k1*((1-b) + (b*(allDocs[docid]/AvgDocLen)))     # d=> doc len
                tscore  = math.log10((allDocs[docid] + 0.5)/IDF[int(qid)-1] +0.5) * ((1+k1)*len(termDic[termId[q1[i]]][2][docid])/K + len(termDic[termId[q1[i]]][2][docid])) * ((1+k2)/(k2+1))
                CorpScore[docid]+=tscore
            i+=1

        temparr = []
        for i in range(1,len(allDocs)):
            temparr.append([i,CorpScore[i]])
        
        temparr.sort(reverse=True,key=lambda x: x[1])

         ##  Evaluation

        # p@5
        relcount =0
        precision5=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision5 = relcount*1.0/(i+1)
            if i+1 ==5:
                break
        
        # p@10
        relcount =0
        precision10=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision10 = relcount*1.0/(i+1)
            if i+1 ==10:
                break

        # p@20
        relcount =0
        precision20=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision20 = relcount*1.0/(i+1)
            if i+1 ==20:
                break
        
        # p@30
        relcount =0
        precision30=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision30 = relcount*1.0/(i+1)
            if i+1 ==30:
                break
         # MAP
        relcount =0
        precisionMAP=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precisionMAP += relcount*1.0/(i+1)
        precisionMAP/=(len(allDocs)-1)
        # writing precision table
        TablePrecision.write(str(qkey)+'\t\t\t'+str(precision5)+'\t\t\t'+str(precision10)+'\t\t\t'+str(precision20)+'\t\t\t'+str(precision30)+'\t\t\t'+str(precisionMAP) + "\n")
    

        
        for i in range(0,len(allDocs)-1):
            scorefilebm.write(str(qkey) +' '+dicdids[str(temparr[i][0])] +' '+ str(i+1) +' '+str(temparr[i][1])+' '+ 'run3'+'\n' )

    scorefilebm.close()
    TablePrecision.close()

#######  Score Function 2 (Dirichlet)

## N/N+u  (doc)  + u/(N+u) (corpus)
if scoreName=="Dirichlet":
    scorefiledir = open("scorefiledir.txt",'w') 
    TablePrecision = open("TablePrecision.txt",'w')
    TablePrecision.write("Query Id"+'\t\t\t'+"P@5"+'\t\t\t'+"P@10"+'\t\t\t'+"P@20"+'\t\t\t'+"P@30"+'\t\t\t'+"MAP" + "\n")
    for qkey in qkeys:
        q1 = querydict[qkey]

        CorpScore = [0 for i in range(len(allDocs))]

        relDocs =[]
        lenrelDocs=[]
        BackGroundtp=[]
        for q in q1:
            qid = termId[q]
            BackGroundtp.append(BackGroundProbability[int(qid)])
            qpos = termDic[qid]                  # getting postings
            relDocs.append(qpos[2].keys())
            tmparr=[]
            for k in qpos[2].keys():
                tmparr.append(len(qpos[2][k]))
            lenrelDocs.append(tmparr)


        i=0  
        for doci in relDocs:
            for docid in doci:
                j=0
                tscore  = (lenrelDocs[i][j]/allDocs[docid])*allDocs[docid]/(allDocs[docid]+AvgDocLen) + (BackGroundtp[i]) *AvgDocLen/ (allDocs[docid]+AvgDocLen)
                CorpScore[docid]+=tscore
                j+=1
            i+=1

        
        temparr = []
        for i in range(1,len(allDocs)):
            temparr.append([i,CorpScore[i]])
        
        temparr.sort(reverse=True,key=lambda x: x[1])

        ##  Evaluation

        # p@5
        relcount =0
        precision5=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision5 = relcount*1.0/(i+1)
            if i+1 ==5:
                break
        
        # p@10
        relcount =0
        precision10=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision10 = relcount*1.0/(i+1)
            if i+1 ==10:
                break

        # p@20
        relcount =0
        precision20=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision20 = relcount*1.0/(i+1)
            if i+1 ==20:
                break
        
        # p@30
        relcount =0
        precision30=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precision30 = relcount*1.0/(i+1)
            if i+1 ==30:
                break
         # MAP
        relcount =0
        precisionMAP=0
        for i in range(len(temparr)):
            if dicdids[str(temparr[i][0])] in releventDocarr[int(qkey)]:
                relcount+=1
            precisionMAP += relcount*1.0/(i+1)
        precisionMAP/=(len(allDocs)-1)
        # writing precision table
        TablePrecision.write(str(qkey)+'\t\t\t'+str(precision5)+'\t\t\t'+str(precision10)+'\t\t\t'+str(precision20)+'\t\t\t'+str(precision30)+'\t\t\t'+str(precisionMAP) + "\n")
    
        for i in range(0,len(allDocs)-1):
            scorefiledir.write(str(qkey) +' '+dicdids[str(temparr[i][0])] +' '+ str(i+1)+' ' +str(temparr[i][1])+' '+ 'run3'+'\n' )


    scorefiledir.close()
    TablePrecision.close()





    