import logging
logger = logging.getLogger('neveredit.ui')

import wx

from neveredit.util import neverglobals
import neveredit.file.SoundSetFile as SoundSetFile

import os.path
import sys
import threading
from cStringIO import StringIO



# "Global" (module-wise) event : we only want one sound playing thread at a time
# and we have many SoundControl on a PropWindow
Event_Die = threading.Event()


class SoundControl(wx.BoxSizer):
    ''' Control that allows to select a sound via a wxChoice, and to
test the selected sound on a button hit.
There a 4 kinds of selectable sounds in NWN:
    - Ambient music, the ResRef points to a .bmu file in the 'music'
        directory in the NWN install location. The reference 2da file is
        ambientmusic.2da -- problem with BMU file format (Micka)
    - Ambient sounds, the ResRef points to a .wav file in the 'ambient'
        directory in the NWN install location. the reference 2da file is
        ambientsound.2da -- done (Micka)
    - Sound objects, either in a .uts gff file or as 'Sound' struct in
        an GIT file -- not planning to support on short term (Micka)
    - Sound Sets, used for NPC voices, in a specific (non GFF) file format
        (the SSF file format), referenced to via soundset.2da. One problem is
        that though the resources are classified as 'wav', the Bioware provided
        ones are in fact BMU.

NOTE : pygame.mixer.Sound doesn't support mp3 files, and pygame.mixer.music does but doesn't
allow loading from a file object (it only loads from a file name). So I had to use
pygame.movie.Movie (!) to play mp3 files.

TODO : -cycle through the many sounds in a soundset on each consecutive play
       -set playback duration in preferences - maybe one pref for each
       

BUG : I experience some segfaults with mp3 playing...

    '''


    def __init__(self, prop, propWindow,choices,twodaName):
        wx.BoxSizer.__init__(self,wx.HORIZONTAL)
        self.play_button = wx.Button(propWindow,-1,_('play'))
        self.sound_list = wx.Choice(propWindow,-1,choices=choices)
        self.twodaName = twodaName
        self.twoda = neverglobals.getResourceManager().getResourceByName(twodaName)
        self.parent = propWindow
        self.Add(self.sound_list)
        self.Add(self.play_button)
        wx.EVT_CHOICE(propWindow,self.sound_list.GetId(),self.soundChanged)
        wx.EVT_BUTTON(propWindow,self.play_button.GetId(),self.playButtonHit)
        self.SoundType = None
        self.SoundObject = None
        self.hasChanged = False
        self.firstTime = True

    def Destroy(self):
        self.sound_list.Destroy()
        self.play_button.Destroy()
        wx.BoxSizer.Destroy(self)

    def soundChanged(self,event):
        self.hasChanged = True
        event.SetId(self.GetId())
        self.parent.controlUsed(event)

    def SetSelection(self,n):
        self.sound_list.SetSelection(n)

    def GetSelection(self):
        return self.sound_list.GetSelection()

    def GetId(self):
        return self.sound_list.GetId()

    def playButtonHit(self, event):
        if self.hasChanged or self.firstTime:
            self.hasChanged = False
            self.firstTime = False
            if self.twodaName=='ambientmusic.2da':
                self.playButtonHit_music()
            elif self.twodaName=='ambientsound.2da':
                self.playButtonHit_ambient()
            elif self.twodaName=='soundset.2da':
                self.playButtonHit_soundset()
        else:
            self.playSound()

    def playButtonHit_music(self):
        # get the resource name of the sound we want to play
        sound_resource = self.twoda.getEntry(self.sound_list.GetSelection(),'Resource')
        sound_resource = sound_resource.lower()
        sound_files = [x.split('.')[0].lower()\
            for x in neverglobals.getResourceManager().getBMUFileNames()]
        try:
            i = sound_files.index(sound_resource)
            bmu_name = neverglobals.getResourceManager().getBMUFileNames()[i]
            print(bmu_name)
        except ValueError:
            # The file does not exist on this nwn install dir
            logger.warning("the requested file %s doesn't exist on this NWN installation",\
                sound_resource+".bmu")
            bmu_name = ''
        if bmu_name:
            # a bit harsh : will only take a part of the file (temporary)
            bmu_file = open(os.path.join(neverglobals.getResourceManager().getAppDir(),\
                'music',bmu_name),'rb')
            data = bmu_file.read()[8:]
            self.SoundObject = StringIO(data)
            self.SoundType = 'BMU'
            self.hasChanged = False
            self.playSound()

    def playButtonHit_soundset(self):
        soundset_name = self.twoda.getEntry(self.sound_list.GetSelection(),'RESREF')
        soundset_name = soundset_name.lower()
        soundset = neverglobals.getResourceManager().getRawResourceByName(\
            soundset_name + '.ssf')
        ssf = SoundSetFile.SoundSetFile()
        ssf.fromFile(StringIO(soundset))
        sound_name = ssf.getEntryData(1)[0]
        # now, let's get the sound file, at least
        sound_resource = neverglobals.getResourceManager().getRawResourceByName(sound_name+'.wav')
        # check if we have a bmu file
        if sound_resource[0:3]=='BMU':
            sound_resource = sound_resource[8:]
            self.SoundType = 'BMU'
        else:
            self.SoundType = 'WAV'
        self.SoundObject = StringIO(sound_resource)
        self.hasChanged = False
        self.playSound()

    def playButtonHit_ambient(self):
        sound_name = self.twoda.getEntry(self.sound_list.GetSelection(),'Resource')
        sound_name = sound_name.lower()
        sndfile_name = ''
        ambient_sounds = [x.split('.')[0].lower() for x in\
            neverglobals.getResourceManager().getAmbSoundFileNames()]
        try:
            sound_idx = ambient_sounds.index(sound_name)
            sndfile_name = neverglobals.getResourceManager().getAmbSoundFileNames()[sound_idx]
        except ValueError:
            logger.warning("the requested file %s doesn't exist on this NWN installation",\
                sndfile_name)
            sndfile_name = ''
            self.SoundObject = None
            self.SoundType = None
            self.hasChanged = False
        if sndfile_name:
            self.SoundObject = open(os.path.join(neverglobals.getResourceManager().getAppDir(),\
                'ambient',sndfile_name),'rb')
            self.SoundType = 'WAV'
            self.hasChanged = False
            self.playSound()

    def playSound(self):
        # two cases, either we have a wav, or we have a mp3
        Event_Die.set()
        Event_Die.clear()
        self.changeButton()
        if self.SoundType == 'WAV':
            self.snd_player = WAV_Thread(self.SoundObject)
            self.snd_player.start()
        elif self.SoundType == 'BMU':
            self.snd_player = MP3_Thread(self.SoundObject)
            self.snd_player.start()
            self.hasChanged = True # force the long way, pygame.movie closes the file!
        else:
            self.stopButtonHit(None)

    def stopButtonHit(self,event):
        Event_Die.set()
        Event_Die.clear()
        self.play_button.SetLabel('play')
        wx.EVT_BUTTON(self.parent,self.play_button.GetId(),self.playButtonHit)
        self.play_button.Refresh()

    def changeButton(self):
        self.play_button.SetLabel('stop')
        wx.EVT_BUTTON(self.parent,self.play_button.GetId(),self.stopButtonHit)
        self.play_button.Refresh()


class MP3_Thread(threading.Thread ):
    def __init__(self,fobject):
        threading.Thread.__init__(self)
        self.sound = fobject

    def run(self):
        import pygame.movie
        self.sound.seek(0)
        snd = pygame.movie.Movie(self.sound)
        snd.set_volume(1.0)
        snd.set_display(None)
        snd.play()
        Event_Die.wait()


class WAV_Thread(threading.Thread ):
    def __init__(self,fobject):
        threading.Thread.__init__(self)
        self.sound = fobject

    def run(self):
        import pygame.mixer
        pygame.mixer.init(22050,-16,True,1024)
        self.sound.seek(0)
        snd = pygame.mixer.Sound(self.sound)
        snd.play(0,6000) # maxtime should be set in Preferences
        Event_Die.wait()
        pygame.mixer.quit()
