import os
import numpy as np

class InvertedIndex:
    def __init__(self, index_name):
        index_dir = os.path.join(index_name)
        self.docs = np.memmap(index_name + ".docs", dtype=np.uint32, mode='r')
    def __iter__(self):
        i = 2
        f = open("invData.txt", "w")
        while i < len(self.docs):
            size = self.docs[i]
            if size >= 4096:
                #bytes = ipc(self.docs[i+1:size+i+1],size,self.docs[i+1],self.docs[size+i])
                bytes = Simple9(self.docs[i+1:size+i+1])
                f.write(str(size)+" "+str(self.docs[1])+" "+str(bytes)+"\n")
                print(str(size)+" "+str(self.docs[1])+" "+str(bytes)+"\n")
            #Three tuple containing range, size of posting list, encoding
            #(self.docs[size+i]-self.docs[i],size,SomeEncoding(self.docs[i+1:size+i+1]))
            #print(self.docs[1])
            i += size+1
        f.close()
        
    def __next__(self):
        return self
    
def GammaEncoding(postingList):
    last = 0 
    countBits =  2*(np.floor(np.log2(postingList[0])).astype(int))+1
    i = 0
    while i < len(postingList):
        print(countBits)
        current = postingList[i]
        delta = current - last
        last = current
        countBits += 2*(np.floor(np.log2(delta)).astype(int))+1
        i +=1
    return np.ceil(countBits/8)

def VarByteEncoding(postingList):
    last = 0 
    countBytes = 0
    i = 0
    while i < len(postingList):
        #print(countBytes)
        current = postingList[i]
        delta = current - last - 1 
        last = current
        while delta >= 128: 
            delta = delta//128
            countBytes += 1
        countBytes += 1
        i +=1
    return countBytes
        
    
def Simple9(postingList):
    i = 0 
    countBytes = 0
    newList = np.copy(postingList)
    for y in range(len(postingList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
    while i < len(postingList):
        #print(countBytes)
        if (len(postingList)-1-i >= 28 and max(postingList[i:i+28]) <= 1):
            i+=28
        elif (len(postingList)-1-i >= 14 and max(postingList[i:i+14]) <= 3):
            i+=14
        elif (len(postingList)-1-i >= 9 and max(postingList[i:i+9]) <= 7):
            i+=9
        elif (len(postingList)-1-i >= 7 and max(postingList[i:i+7]) <= 15):
            i+=7
        elif (len(postingList)-1-i >= 5 and max(postingList[i:i+5]) <= 31):
            i+=5
        elif (len(postingList)-1-i >= 4 and max(postingList[i:i+4]) <= 127):
            i+=4
        elif (len(postingList)-1-i >= 3 and max(postingList[i:i+3]) <= 511):
            i+=3
        elif (len(postingList)-1-i >= 2 and max(postingList[i:i+2]) <= 16383):
            i+=2 
        else: #assuming all numbers are less than 268435456 (2^28)
            i+=1 
        countBytes+=4 
    return countBytes 
                 
    
def blockSizePFD(postingList, bstr,index): 
    #Assume Block Size of 128 Integers)
    offsetCount = 0 #in case the first number in postingList overflows 
    offset = []
    higherBits = []
    for y in range (index,min(index+128,len(postingList))):
        if (postingList[y] > 2**bstr -1):
            shiftNum = postingList[y] >> bstr
            higherBits.append(shiftNum) 
            offset.append(offsetCount)
            offsetCount = 0
        else:
            offsetCount += 1 
    return (Simple9(higherBits)+Simple9(offset)+bstr*16) #divide 128 by 8 for bytes 
    
def OptPFD(postingList): 
    bstrVals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16, 20, 32]
    countBytes = 0 
    i = 0
    newList = np.copy(postingList)
    for y in range(len(postingList)):
        if (y!=0):
            newList[y] = postingList[y]-postingList[y-1]-1
    while i < len(postingList):
        print(countBytes)
        byteSizes = [] 
        for bstr in bstrVals:
            byteSizes.append(blockSizePFD(postingList,bstr,i))
        countBytes += min(byteSizes)
        print(byteSizes)
        i += 128
    return countBytes 
         
#returns number of bits needed to IP encode numbers in array recursively */

#def ipc(postingList,  num,  low,  high):
#    print(len(postingList))
#    if (num == 0):
#        return(0)
#    mid = num//2
#    n = high-low-num-1
#    x = postingList[mid]-low-mid-1
#    c = nBits(n, x)
#    list1 = np.copy(postingList[::mid+1])
#    list2 = np.copy(postingList[mid+1::])
#    return(c+ipc(list1, len(list1), low, postingList[mid]) + ipc(list2, len(list2), postingList[mid], high))

#returns number of bits needed for an integer x known to be at most n */
#def nBits(n, x):
#    i = (n+1)//2;
#    x = 2*(x-i) if (x >= i) else 2*(i-x)-1
#    i = 1
#    j = 0
#    while (i <= n):
#        j+=1
#        i<<=1            
#    if ((j > 0) and (x < i-1-n)):
#        j-=1
#    return(j)
                    
for i, docs in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs)
