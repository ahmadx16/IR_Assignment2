
tidFile = open('termid.txt','r')
tids = tidFile.readlines()
termId ={}
for tid in tids:
    ttid = tid.split()
    termId[ttid[0]] = ttid[1]
print(termId)
