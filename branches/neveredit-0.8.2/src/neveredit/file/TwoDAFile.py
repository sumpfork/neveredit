"""Class for reading 2DA files"""

class TwoDAFile:
    __doc__ = globals()['__doc__']
    def __init__(self):
        pass
    
    def fromFile(self,f):
        f.seek(0)
        line = ''
        while not line:
            line = f.readline().strip()
        (self.type,self.version) = line.split()
        line = ''
        while not line:
            line = f.readline().strip()
        self.columnLabels = ['RowNumber'] + line.split()
        line = f.readline().strip()
        while not line:
            line = f.readline().strip()
        self.rows = []
        while line:
            self.rows.append(line.split())
            line = f.readline().strip()
        f.close()

    def getRowCount(self):
        return len(self.rows)

    def getRows(self):
        return self.rows

    def getRowIndex(self,entry,colName):
        colIndex = self.columnLabels.index(colName)
        for i,row in enumerate(self.rows):
            if row[colIndex] == entry:
                return i
        print 'warning: no entry',entry,'column',colName
        return None
    
    def getRow(self,index):
        '''get row by index in 2da file
        @param index: index of row to return
        @return: list of string entries in that row
        '''
        return self.rows[index]

    def getEntry(self,index,colName):
        '''get entry by row index and column name
        @param index: index of row
        @param colName: name of the column in the 2da file to look at
        @return: entry requested as string
        '''
#        print 'returning',index,self.columnLabels.index(colName),'amongst',len(self.rows),len(self.columnLabels)
        return self.rows[index][self.columnLabels.index(colName)]
    
    def __str__(self):
        s = self.type + ' ' + self.version + '\n'
        s += str(self.columnLabels) + '\n'
        s += str(self.rows)
        return s

    def __repr__(self):
        return self.__str__()

if __name__ == '__main__':
    import sys
    f = TwoDAFile()
    f.fromFile(open(sys.argv[1]))
    print f
