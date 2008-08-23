import logging
logger = logging.getLogger('neveredit.game')

from ConfigParser import NoSectionError

from neveredit.file.GFFFile import GFFStruct
from neveredit.game.NeverData import LocatedNeverData
from neveredit.util import neverglobals

class Tile(LocatedNeverData):
    CORNERS=['TopLeft',
             'TopRight',
             'BottomRight',
             'BottomLeft']

    SIDES=['Top',
           'Right',
           'Bottom',
           'Left']
    
    propList = {
        'Tile_AnimLoop1':'Boolean',
        'Tile_AnimLoop2':'Boolean',
        'Tile_AnimLoop3':'Boolean',
        'Tile_Height':'Integer,0-5',
        'Tile_ID':'Integer',
        'Tile_MainLight1':'Integer',#actually 2da index
        'Tile_MainLight2':'Integer',#actually 2da index
        'Tile_Orientation':'Integer,0-3',
        'Tile_SrcLight1':'Integer,0-15',
        'Tile_SrcLight2':'Integer,0-15'
        }

    def __init__(self,tileset,gffEntry=None,tid=None):
        LocatedNeverData.__init__(self)
        if not gffEntry:
            if tid == None:
                raise RuntimeError("need one of gffEntry or tid")
            #tinfo = tileset.getTileInfo(tid)
            gffEntry = GFFStruct(1)
            #not quite sure yet where defaults for the next values come from
            #they don't seem to be specified in the .set file
            gffEntry.add('Tile_AnimLoop1',0,'INT')
            gffEntry.add('Tile_AnimLoop2',0,'INT')
            gffEntry.add('Tile_AnimLoop3',0,'INT')
            gffEntry.add('Tile_Height',0,'INT')
            gffEntry.add('Tile_ID',tid,'INT')
            gffEntry.add('Tile_MainLight1',0,'BYTE')
            gffEntry.add('Tile_MainLight2',0,'BYTE')
            gffEntry.add('Tile_Orientation',0,'INT')
            gffEntry.add('Tile_SrcLight1',0,'INT')
            gffEntry.add('Tile_SrcLight2',0,'INT')
            
        self.addPropList('main',self.propList,gffEntry)
        self.properties = dict(tileset.items('TILE' + str(self['Tile_ID'])))
        self.doors = []
        for i in range(int(self['Doors'])):
            try:
                doorsection = 'TILE' + `self['Tile_ID']` +\
                              'DOOR' + `i`
                self.doors.append(dict(tileset.items(doorsection)))
            except NoSectionError:
                logger.info('no door section found: ' + doorsection)
        self.tileset = tileset
        self.modelName = self['model'] + '.mdl'
        self.model = None
        self.TwoDTile = None

    def getId(self):
        return self['Tile_ID']
    
    def getName(self):
        return `self.getId()` + '/' + self.modelName

    def getPortrait(self):
        return self.get2DTile()

    def get2DImageName(self):
        return self['Imagemap2D'].lower() + '.tga'
    
    def get2DTile(self):
        """
        Get the 2D tile picture for this tile.
        @return: the 2D tile (a PIL Image object)
        """
        if not self.TwoDTile:
            self.TwoDTile = neverglobals.getResourceManager()\
                            .getResourceByName(self.get2DImageName())
        return self.TwoDTile

    def getModel(self,copy=False):
        if not self.model:
            self.model = neverglobals.getResourceManager()\
                         .getResourceByName(self.modelName,copy)
        return self.model

    def __getitem__(self,key):
        if self.hasProperty(key):
            return self.getPropertyValue(key)
        else:
            return self.properties[key.lower()]

    def getDoor(self,n):
        return self.doors[n]

    def isInGroup(self):
        return self.tileset.isTileInGroup(self)
    
    def getCornerType(self,corner):
        """Return the type of corner terrain of this tile for the given corner.
        @param corner: a string specifying which corner terrain type to return,
                     possible values are L{CORNERS}
        @return: a string representation of that terrain"""
        orientation = self['Tile_Orientation']
        cornerSpecs = dict(zip(Tile.CORNERS,
                               Tile.CORNERS[orientation:]
                               + Tile.CORNERS[:orientation]))
        return self[cornerSpecs[corner]]

    def getSideType(self,side):
        """Return the type of crosser (side elements like roads, rivers, fences) for
        this tile for the given side.
        @param side: a string specifying which side crosser to return, possible values
                     are L{SIDES}
        @return: a string representation of that crosser (empty string if no crosser)"""
        orientation = self['Tile_Orientation']
        sideSpecs = dict(zip(Tile.SIDES,
                             Tile.SIDES[orientation:]
                             + Tile.SIDES[:orientation]))
        return self[sideSpecs[side]]

    def getType(self,direction):
        """Return the type of corner or side, depending on the direction given.
        See L{getSideType} and L{getCornerType}.
        @param direction: The side or corner from L{SIDES} or L{CORNERS}
        @return: a string representation of the type of terrain at that side or corner.
        """
        if direction in Tile.CORNERS:
            return self.getCornerType(direction)
        elif direction in Tile.SIDES:
            return self.getSideType(direction)
        else:
            raise ValueError("unknown direction: " + direction)
        
    def canPlaceRelativeTo(self,tile,direction):
        """
        Check whether this tile can be placed relative to another tile.
        @param tile: the tile to try placement relative to
        @param direction: the direction of relative placement chosen from
                          L{Tile.CORNERS} + L{Tile.SIDES}. This is the direction
                          FROM the already placed tile given as an argument TO
                          the tile this method is called on, i.e. if there's
                          a tile to the left of the spot being considered, the
                          direction should be 'Right'.
        """
        if direction in Tile.CORNERS:
            placedCornerType = tile.getCornerType(direction)
            myDirection = Tile.CORNERS[(Tile.CORNERS.index(direction) + 2) % 4]
            myCornerType = self.getCornerType(myDirection)
            #if placedCornerType == myCornerType:
            #    print 'checking corner:',direction
            #    print 'myDirection:',myDirection
            #    print 'placed:',placedCornerType
            #    print 'myCornerType:',myCornerType
            #    print '----------'
            return placedCornerType == myCornerType
        elif direction in Tile.SIDES:
            placedSideType = tile.getSideType(direction)
            myDirection = Tile.SIDES[(Tile.SIDES.index(direction) + 2) % 4]
            mySideType = self.getSideType(myDirection)
            #if placedSideType == mySideType:
            #    print 'checking side:',direction            
            #    print 'placed:',placedSideType
            #    print 'myDirection:',myDirection
            #    print 'mySideType:',mySideType
            #    print '----------'
            return placedSideType == mySideType
        else:
            raise ValueError(direction + ' not a valid tile direction')

    def rotate(self,angle):
        """Rotate this tile clockwise.
        @param angle: angle in degrees to rotate by, must be multiple of 90.
        """
        if angle % 90 != 0:
            logger.error("can only rotate tiles by angles divisible by 90 degrees")
            return
        else:
            self['Tile_Orientation'] += angle/90
            self['Tile_Orientation'] %= 4
            
    def getBearing(self):
        o = self['Tile_Orientation']
        if o == 0:
            return 0.0
        elif o == 1:
            return 90.0
        elif o == 2:
            return 180.0
        elif o == 3:
            return 270.0
        else:
            logger.warn('warning, unknown tile orientation: ' + `o`)
            return 0.0

    def getTileHeight(self):
	return self['Tile_Height']
	