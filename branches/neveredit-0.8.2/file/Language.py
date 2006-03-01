
# Those are the languages codes as specified by Bioware (source : bioware content documentation)
# Not sure if they should all be included as some of them require specific charsets anyway...
BIOlangCodes = {'english':0,
                'french':1,
                'german':2,
                'italian':3,
                'spanish':4,
                'polish':5,
                'korean':128,
                'chinese traditional':129,
                'chinese simplified':130,
                'japanese':131}

# Needed because anydictionary.key() will give the keys in *random* order
BIOorderedLangs = ['english','french','german','italian','spanish','polish','korean',
                'chinese traditional','chinese simplified','japanese']
# Using another dict with key/values reversed instead of coded function
InverseBIOCodes = {0:'english',
                1:'french',
                2:'german',
                3:'italian',
                4:'spanish',
                5:'polish',
                128:'korean',
                129:'chinese traditional',
                130:'chinese simplified',
                131:'japanese'
                }

# It's convenient to be able to use a "connexe" list of indexes, for example for use with
# controls (like wx.Choice). It allows to translate BIOorderedLangs indexes to BioLangCodes
def convertFromBIOCode(n):
        if n<6:
                return n
        else:
                return n-122

def convertToBIOCode(n):
        if n<6:
                return n
        else:
                return n+122

def fromBIOCodeToString(n):
        return InverseBIOCodes[n]

def fromInternalCodeToString(n):
        return InverseBIOCode[convertToBIOCode(n)]
