import wx

from neveredit.file.CExoLocString import CExoLocString
from neveredit.ui import PropWindow
from neveredit.game.Conversation import PCConvNode

class ConversationNode(wx.TreeItemData):
    def __init__(self,convNode,convTree):
        wx.TreeItemData.__init__(self)
        self.convNode=convNode
        self.treeNode=None
        self.tree = convTree
        self.colour = wx.BLACK
        convNode.conversationNode = self
        # TODO: check whether we should fetch the default language and gender
        self.setText(0,0)

    def getText(self,langID,gender):
        return self.text.getString(langID,gender)

    def setTreeText(self,langID,gender):
        if self.treeNode:
            self.tree.SetItemText(self.treeNode,self.getText(langID,gender))
            self.tree.SetItemTextColour(self.treeNode,self.colour)

class LinkConversationNode(ConversationNode):
    def __init__(self,convNode,convTree):
        ConversationNode.__init__(self,convNode,convTree)
        self.colour = wx.TheColourDatabase.FindColour('DARK GREY')
    
    def setText(self,langID,gender):
        self.text=CExoLocString(self.convNode.pointed.data['Text'])
        self.setTreeText(langID,gender)

class RealConversationNode(ConversationNode):
    def __init__(self,convNode,convTree):
        ConversationNode.__init__(self,convNode,convTree)
        if convNode.__class__ == PCConvNode:
            self.colour = wx.BLUE
        else:
            self.colour = wx.RED

    def setText(self,langID,gender):
        self.text=CExoLocString(self.convNode.data['Text'])
        self.setTreeText(langID,gender)

    def propertyChanged(self,propControl,prop):
        self.tree.conversationWindow.maybeApplyPropControlValues()
        self.setText(propControl.control.langID,propControl.control.gender)
        for l in self.convNode.backlinks:
            l.conversationNode.setText(propControl.control.langID,propControl.control.gender)

class ConversationTree(wx.TreeCtrl):
    def __init__(self,parent,id,conversation):
        wx.TreeCtrl.__init__(self,parent,id,style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        self.conversation = conversation
        self.conversationWindow = parent
        self.createTree()
    
    def createTreeRec(self,parent,children,links):
        for entry in children:
            if entry in links:
                data = LinkConversationNode(entry,self)
                self.addNode(parent,data)
            else:
                data = RealConversationNode(entry,self)
                node = self.addNode(parent,data)
                self.createTreeRec(node,data.convNode.children,data.convNode.links)
    
    def createTree(self):
        self.AddRoot(self.conversation.name)
        for entry in self.conversation.nodes:
            data = RealConversationNode(entry,self)
            node = self.addNode(self.GetRootItem(),data)
            self.createTreeRec(node,data.convNode.children,data.convNode.links)
    
    def addNode(self,parent,data):
        # TODO: fetch the default langID and gender here
        node = self.AppendItem(parent,data.getText(0,0))
        data.treeNode = node
        self.SetPyData(node,data)
        # TODO: fetch the default langID and gender here
        data.setTreeText(0,0)
        return node

class ConversationWindow(wx.SplitterWindow):
    def __init__(self,parent,data):
        wx.SplitterWindow.__init__(self,parent)

        tID = wx.NewId()
        self.tree = ConversationTree(self,tID,data)

        self.selectedTreeItem = None

        wx.EVT_TREE_SEL_CHANGED(self,tID,self.treeSelChanged)

        self.notebook = wx.Notebook(self,-1,(420,420))#,style=wx.CLIP_CHILDREN)
        self.props = PropWindow.PropWindow(self.notebook)
        self.notebook.AddPage(self.props,_("Properties"))

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING,self.OnNotebookPageChanging,self.notebook)

        self.SplitHorizontally(self.tree,self.notebook,180)

        self.fileChangeCallback = None

    def setConversation(self, data):
        oldTree = self.tree

        tID = wx.NewId()
        self.tree = ConversationTree(self,tID, data)
        wx.EVT_TREE_SEL_CHANGED(self,tID,self.treeSelChanged)

        self.ReplaceWindow(oldTree,self.tree)

        oldTree.Destroy()
        
    def addChangeListener(self,callback):
        self.fileChangeCallback = callback

    def setFileChanged(self,changed):
        if self.fileChangeCallback:
            self.fileChangeCallback(changed)

    def maybeApplyPropControlValues(self):
        if self.selectedTreeItem:
            data = self.tree.GetPyData(self.selectedTreeItem)
            if data:
                self.applyPropControlValues()

    def applyPropControlValues(self):
        '''This method reads back in the values of currently
        displayed property controls and updates the actual
        module file to reflect these values.'''
        if self.props.applyPropControlValues(self.tree\
                                             .GetPyData(self.selectedTreeItem).convNode):
            self.setFileChanged(True)

    def treeSelChanged(self,event):
        self.maybeApplyPropControlValues()
        if self.tree.GetPyData(event.GetItem()):
            self.selectedTreeItem = event.GetItem()
            conversationNode = self.tree.GetPyData(self.selectedTreeItem)
            self.props.makePropsForItem(conversationNode.convNode,self) 
            textControl = self.props.getControlByPropName('Text')
            if textControl:
                textControl.addPropertyChangeListener(conversationNode)
                conversationNode.propertyChanged(textControl,None)


    def unselectTreeItem(self):
        self.maybeApplyPropControlValues()
        self.selectedTreeItem = None
        self.tree.Unselect()

    def OnNotebookPageChanging(self,event):
        '''Callback for notebook page changing event'''
        self.maybeApplyPropControlValues()
