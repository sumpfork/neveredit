class Progressor:
    def __init__(self):
        self.progressDisplay = None
        
    def setProgressDisplay(self,p):
        self.progressDisplay = p

    def setProgress(self,p):
        if self.progressDisplay:
            self.progressDisplay.setProgress(p)

    def setStatus(self,s):
        if self.progressDisplay:
            self.progressDisplay.setStatus(s)
