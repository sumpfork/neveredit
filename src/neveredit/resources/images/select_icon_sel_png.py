# -*- coding: ISO-8859-1 -*-
"""Resource select_icon_sel_png (from file select_icon_sel.png)"""
# written by resourcepackage: (1, 0, 0)
source = 'select_icon_sel.png'
package = 'neveredit.resources.images'

### wxPython specific functions
originalExtension = '.png'
from wxPython.wx import wxImageFromStream, wxBitmapFromImage, wxEmptyIcon
import cStringIO
def getData( ):
	"""Return the data from the resource as a simple string"""
	return data
def getImage( ):
	"""Return the data from the resource as a wxImage"""
	stream = cStringIO.StringIO(data)
	return wxImageFromStream(stream)
def getBitmap( ):
	"""Return the data from the resource as a wxBitmap"""
	return wxBitmapFromImage(getImage())
def getIcon( ):
	"""Return the data from the resource as a wxIcon"""
	icon = wxEmptyIcon()
	icon.CopyFromBitmap(getBitmap())
	return icon
data = "�PNG\015\012\032\012\000\000\000\015IHDR\000\000\000\032\000\000\000\030\010\002\000\000\000k�z�\000\000\000\003sBIT\010\010\010��O�\000\000\004�IDAT8�u�\
Ϗ\\G\021ǿU��޼�Yό=���\004��`@���2������\021p@�_ ��\003 GA�\012$�\\�f$�\001\020\
H!�Mb���؎��̼y�u��\034�zX�o���Է����������G\011���U\011D�`R\026�����\
����|>�M��f3\000�\020\031U\005�T� P\"�ΙIS��\"� \000\002=4_\020�߿o�l%��v�\000\000\"b\001�\004J)\
�M����a�du��\027\031��D�&\000��C��\023%V\"�\020�*\011<�\032T�U�_Vv�b=jï�{�W/g��\
��8\"\002`\001t��\005\000EBZ�b�_��Ū�r�\022���喯��&a�ž<x=��!քC\\������\016�|�\
ˢt���y�.f��C\031�đ�$\024���Jv��y͟b�N�\032Ǫ�E��˽��\037�n��_��n����V\
\037\027���\037\036�Jē�>y�Bl\033�\011�[�\0071�A��\036&�\010M\0140E\021����Q���0��ʇ\024}�U�Տ\037\
�yw�4�i\021�$Ml�ԯ�X�mEITU5i��\031�eUm}�es���|�,��FM>�A�2�ʍw�~�n\
\035�\030��\006�\006a�x%�����񈩍H*H1��\022���4���\026m��\024[�2�K�$ׯ����8�𯫶\
\011>�:�6�f��0�\0245��I\005\022\014��H\011`ڍ;�\027�E\010^CH1�M�I����\017���\037Y~t�G�\
R����x|��ۦ&\011+,�D��;l/f�|ku�����F'�hhR�b%�l>���w����o�\025�=\
y�O�\025fn��Wϵ�%��a��B�\005@\012cL��>W�t����p���6ƺ5\012\030�R���{�[����o�\
�>�;;�1\032\037�U\023��%�\002\001\020f@\011Jp.?\023N>l�������~��;�y/�Hjէb0:9;q��\
7���!�c���~�8�\010��0\002\"eK���#g\014��/}���ޣ�m�tӝ:����OB\010Ml����u\
��t�����\005�TD�nL�D0L`������7���\010�\025�����\020�իW�HD.]�4��'��d2\
q�u]��dU�\000DDU-;74�Ͷσj\"þ\016\002�r��ٳg�ݻ��UU�y�e\031\021u�\024\007�\001@\022A��\
��1�\036ߚn���L���xL�Ο??\032�.^�(\"7n�\030\016�EQ8�܏J\003`Y\016{�(z�Q��cf�m�\
H�x�k��)��,��\033\033\033�9c����z4�P�$�DJ�0p.w��ֲ�\025y6\030\016'��x<\036\016��/_\006�\
��������hI��\013�e�\010\023�*3g�\031c�\"�h�Y.��r\010!Xk�熱��\020e�\010Ș�\0020��f\006\000\
`�\021\021���\013\027�s)������J-)F�ѿ�֋��CQU��EQ�u����p0\0308玂�h>��~�_\024�\
�����y��!\004\"ʲ,�2f�v�:����g�;G%\0076��\000\000\000\000IEND�B`�"
### end
