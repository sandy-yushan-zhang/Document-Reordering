import os
import numpy as np

class InvertedIndex:
    def __init__(self, index_name):
        index_dir = os.path.join(index_name)
        self.docs = np.memmap(index_name + ".docs", dtype=np.uint32,
              mode='r')
        self.freqs = np.memmap(index_name + ".freqs", dtype=np.uint32,
              mode='r')

    def __iter__(self):
        i = 2
        while i < len(self.docs):
            size = self.docs[i]
            yield (self.docs[i+1:size+i+1], self.freqs[i-1:size+i-1])
            i += size+1

    def __next__(self):
        return self

for i, (docs, freqs) in enumerate(InvertedIndex("/home/josh/output/output.url.inv")):
    print(i, docs, freqs)
