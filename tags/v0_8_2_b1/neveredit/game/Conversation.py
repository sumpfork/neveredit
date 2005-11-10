import string

from neveredit.game import NeverData

class SimpleSyncStruct:
    def __init__(self,strEntry):
        self.active = strEntry['Active']
        self.index = strEntry['Index']
    def __str__(self):
        return string.join([
                'Script for choice: ',
                `self.active`,
                'Reply index: ',
                `self.index`
                ])
    def __repr__(self):
        return self.__str__()

class SyncStruct(SimpleSyncStruct):
    def __init__(self,strEntry):
        SimpleSyncStruct.__init__(self,strEntry)
        self.isChild = strEntry['IsChild']
        self.linkComment = None
        if self.isChild:
            self.linkComment = strEntry['LinkComment']

class Dialog:
    # AnimLoop not dealt with as deemed obsolete
    def __init__(self,dlgEntry):
        self.animation = dlgEntry['Animation']
        self.comment = dlgEntry['Comment']
        self.delay = dlgEntry['Delay']
        self.quest = dlgEntry['Quest']
        self.questEntry = None
        if self.quest != '':
            self.questEntry = dlgEntry['QuestEntry']
        self.script = dlgEntry['Script']
        self.sound = dlgEntry['Sound']
        self.text = dlgEntry['Text']
    def __str__(self):
        qstr = ''
        if self.quest != '':
            qstr = string.join(['Quest: ', self.quest, 'QuestEntry: ', `self.questEntry`])
        return string.join([
                 'Animation: ',
                 `self.animation`,
                 'Comment: ',
                 `self.comment`,
                 qstr,
                 'Script: ',
                 `self.script`,
                 'Sound: ',
                 `self.sound`,
                 'Text: ',
                 `self.text`
                 ])
    def __repr__(self):
        return self.__str__()

class NPCDialog(Dialog):
    def __init__(self,dlgEntry):
        Dialog.__init__(self,dlgEntry)
        self.repliesList = [SyncStruct(s) for s in dlgEntry['RepliesList']]
        self.Speaker = dlgEntry['Speaker']
    def __str__(self):
        return string.join([
                Dialog.__str__(self),
                `self.repliesList`,
                `self.Speaker`
                ])
    def __repr__(self):
        return self.__str__()

class PCDialog(Dialog):
    def __init__(self,dlgEntry):
        Dialog.__init__(self,dlgEntry)
        self.repliesList = [SyncStruct(s) for s in dlgEntry['EntriesList']]

    def __str__(self):
        return string.join([
                Dialog.__str__(self),
                `self.repliesList`
                ])

    def __repr__(self):
        return self.__str__()

class ConvNode(NeverData.NeverData):
    nodePropList = {
        'Active' : 'ResRef,NSS'
    }

    conversationNode = None

    def __init__(self,structEntry):
        NeverData.NeverData.__init__(self)
        self.addPropList('main',self.nodePropList,structEntry)
        self.structData = structEntry

class LinkNode(ConvNode):
    linkNodePropList = {
        'LinkComment' : 'CExoString'
    }
    def __init__(self,index,structEntry):
        ConvNode.__init__(self,structEntry)
        self.linkIndex = index
        self.pointed = None
        self.addPropList('link',self.linkNodePropList,structEntry)

class RealConvNode(ConvNode):
    realNodePropList = {
        'Animation' : 'Integer,0-88',
        'Comment' : 'CExoString',
#        Delay is 0xFFFFFFFF, so we don't represent it
#        'Delay' : 'Integer,4294967295-4294967295',
        'Quest' : 'CExoString',
        'QuestEntry' : 'Integer',
        'Script' : 'ResRef,NSS',
        'Sound' : 'ResRef', # I don't know what to put here
        'Text' : 'CExoLocString,4'
        }

    def __init__(self,index,structEntry,gffEntry):
        ConvNode.__init__(self,structEntry)
        self.index = index
        self.addPropList('real',self.realNodePropList,gffEntry)
        self.data = gffEntry
        self.children = [] # This include links
        self.links = []
        self.backlinks = []

class PCConvNode(RealConvNode):
    def __init__(self,index,structEntry,pcEntries,npcEntries,conversation):
        conversation.registerPCEntry(index,self)
        gffEntry = pcEntries[index]
        RealConvNode.__init__(self,index,structEntry,gffEntry)
        for entry in gffEntry['EntriesList']:
            if entry['IsChild'] == 0:
                self.children.append(NPCConvNode(entry['Index'],entry,pcEntries,npcEntries,conversation))
            else:
                link = LinkNode(entry['Index'],entry)
                self.children.append(link)
                self.links.append(link)

class NPCConvNode(RealConvNode):
    npcNodePropList = {
        'Speaker' : 'CExoString,Creature_Tags'
        }

    def __init__(self,index,structEntry,pcEntries,npcEntries,conversation):
        conversation.registerNPCEntry(index,self)
        gffEntry = npcEntries[index]
        RealConvNode.__init__(self,index,structEntry,gffEntry)
        self.addPropList('npc',self.npcNodePropList,gffEntry)
        for entry in gffEntry['RepliesList']:
            if entry['IsChild'] == 0:
                self.children.append(PCConvNode(entry['Index'],entry,pcEntries,npcEntries,conversation))
            else:
                link = LinkNode(entry['Index'],entry)
                self.children.append(link)
                self.links.append(link)

class Conversation(NeverData.NeverData):
    dlgPropList = {
        'DelayEntry' : 'Integer,0-1000',
        'DelayReply' : 'Integer,0-1000',
        'EndConverAbort' : 'ResRef,NSS',
        'EndConversation' : 'ResRef,NSS',
        'PreventZoomIn' : 'Boolean',
        }

    def __init__(self,name,gffEntry):
        NeverData.NeverData.__init__(self)
        self.addPropList('main',self.dlgPropList,gffEntry.getRoot())

        self.name = name

        self.pcEntries = {}
        self.npcEntries = {}

        pcEntries = gffEntry['ReplyList']
        npcEntries = gffEntry['EntryList']

        self.nodes = [NPCConvNode(entry['Index'],entry,pcEntries,npcEntries,self) for entry in gffEntry['StartingList']]
        
        for index in self.pcEntries.keys():
            for link in self.pcEntries[index].links:
                if link.linkIndex in self.npcEntries:
                    link.pointed = self.npcEntries[link.linkIndex]
                    self.npcEntries[link.linkIndex].backlinks.append(link)
                else:
                    print "Warning: dangling link"
            
        for index in self.npcEntries.keys():
            for link in self.npcEntries[index].links:
                if link.linkIndex in self.pcEntries:
                    link.pointed = self.pcEntries[link.linkIndex]
                    self.pcEntries[link.linkIndex].backlinks.append(link)
                else:
                    print "Warning: dangling link"
        
        self.entryList = [NPCDialog(d) for d in gffEntry['EntryList']]
        self.numWords = gffEntry['NumWords']
        if not 'PreventZoomIn' in gffEntry:
            gffEntry.add('PreventZoomIn', False, 'BYTE')
        self.replyList = [PCDialog(d) for d in gffEntry['ReplyList']]
        self.startingList = [SimpleSyncStruct(s) for s in gffEntry['StartingList']]

    def registerPCEntry(self,index,pcNode):
        if index in self.pcEntries:
            print 'warning, PC entry with index',index,'already exists'
            return
        self.pcEntries[index] = pcNode

    def registerNPCEntry(self,index,npcNode):
        if index in self.npcEntries:
            print 'warning, NPC entry with index',index,'already exists'
            return
        self.npcEntries[index] = npcNode

    def getEntryList(self):
        return self.entryList

    def __str__(self):
        return self.name
    
#    string.join([
#                self.name,
#                'DelayEntry =',
#                `self.delayEntry`,
#                'DelayReply =',
#                `self.delayReply`,
#                'EndConverAbort =',
#                `self.endConverAbort`,
#                'EndConversation =',
#                `self.endConversation`,
#                'EntryList =',
#                `self.entryList`,
#                'NumWords =',
#                `self.numWords`,
#                'PreventZoomIn =',
#                `self.preventZoomIn`,
#                'ReplyList =',
#                `self.replyList`,
#                'StartingList =',
#                `self.startingList`
#                ])

    def __repr__(self):
        return self.__str__()
