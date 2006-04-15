import logging
logger = logging.getLogger("neveredit.ui")

import wx

class Notebook (wx.Notebook):
    def __init__(self,parent):
        wx.Notebook.__init__(self,parent,-1,(420,420))
        self.pageMap = {}

    def AddPage(self, page, title, tag):
        self.pageMap[tag] = [self.GetPageCount(), True]
        wx.Notebook.AddPage(self, page, title)

    def getSelectedTag(self):
        select = self.GetSelection()
        for tag,info in self.pageMap.iteritems():
            if info[0] == select:
                return tag
        return None
        
    def getPageByTag(self, tag):
        if tag in self.pageMap:
            return self.GetPage(self.pageMap[tag][0])
        else:
            return None

    def removePageByTag(self, tag, doDelete=False):
        if tag not in self.pageMap:
            #logger.warning('trying to delete page not in notebookMap: ' + `tag`
            #               + ' notebookMap: ' + `self.pageMap`)
            return
        else:
            pageNum = self.pageMap[tag][0]
            for name,page in self.pageMap.iteritems():
                if page[0] > pageNum:
                    self.pageMap[name][0] -= 1
            #print 'removing page',pageNum,tag
            if doDelete:
                self.DeletePage(pageNum)
            else:
                self.RemovePage(pageNum)
            del self.pageMap[tag]
            
    def deletePageByTag(self, tag):
        self.removePageByTag(tag, True)

    def getPageInfo(self, pageNum):
        for key,info in self.pageMap.iteritems():
            if info[0] == pageNum:
                return info
        return None

    def getPageInfoByTag(self, tag):
        return self.pageMap.get(tag,None)

    def selectPageByTag(self, tag):
        info = self.getPageInfoByTag(tag)
        if info:
            self.SetSelection(info[0])
            
    def doesCurrentPageNeedSync(self):
        info = self.getPageInfo(self.GetSelection())
        if not info or not info[1]:
            return False
        else:
            return True

    def setSyncAllPages(self, sync):
        for tag, info in self.pageMap.iteritems():
            info[1] = sync
            
    def setCurrentPageSync(self, sync):
        info = self.getPageInfo(self.GetSelection())
        if not info:
            return
        else:
            info[1] = sync

    def setPageSyncByTag(self, tag, sync):
        info = self.getPageInfoByTag(tag)
        if not info:
            return
        else:
            info[1] = sync
    
