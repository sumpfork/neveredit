# -*- coding: ISO-8859-1 -*-
"""Resource paint_icon_png (from file paint_icon.png)"""
# written by resourcepackage: (1, 0, 0)
source = 'paint_icon.png'
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
data = "�PNG\015\012\032\012\000\000\000\015IHDR\000\000\000\032\000\000\000\030\010\002\000\000\000k�z�\000\000\000\003sBIT\010\010\010��O�\000\000\0057IDAT8�u�\
M���\025��y>���5w>�Mb�\031cZhcB\015��\024*�,���v%��Ft�n���]K�p��V\020�� �\
��F\004\023Z!�Z��d&�d2373w�~���9.�ɍ-��\036\036�?����?�����t\000\000\021\001��\001��\005h\
d\"`\024J0\021\004DI\020\004\011\026��\003J\004�>dff\036\016�j}}�V�!\"\021!2�\000\020\000�<BD\000�\034\020520\002�C�� X\
\004�\001\0043\003�\020��www\0253�z=\000\000\000\004��\000�9\010\0211!���\000D�=�/����v��P0\012U�\021\021\"j��\020\
��ED\000/A\0218!t�\000\002(�5��\030��۱\012{\011\014V��f���@�^FJID\000�*aD\004\000�L�\001�Ě�\030�\
\034����͹\006\024aK�=�\017@�u{k�>$��6\001@J��w���qp�8k\015�b'��z\002����GK\017.�\
���҅`��z��^o�;\027aqg���\000���r�����VҒ�B�7��7f`���\023�N��\032�(�l\
[I>��k�\035g<'������\020B\020BxO��ˣ�K9�{7p�\030g�V��G��^�����$�,�\031�\021�\
��8k}�&�\024\"\012D��\033c�<�~+X\017�\017�%W���Һ[��Y��w/\026�e��`b\006�q����\033!�J�\
\022��b�+�y�z�\033c��ι�y�\002\031\037����\015�w�t\033��U�z��(�A��W�q�����Z�v���\
�[���xcٖ�zp\014@|���򪁫\037f��v�6��+++W�^v�U\036�D\021Q0��:I�Z�&c�v��\
�Gv\\�`�\015dY`��?]M/��\032�6�[:5,ͅ/�J�Y)���jV\001��:��<�g�3��I��,�\020\
����\033�k�/��l��7����_ԛ�>��\003���{dQJYqM��*�$I�4��m\\�jmusp��h\
yutck�\030[�f�БË'n~u���+O���у�n�F�\003I�L��\024ؗ�ZgY���}��\037mm5�\
�n�{������֚ȗ��t:��[�=��ڱ�₸��$K��B\000�d�w�(ʲ��l�;w�9GDZ\
�4M�4M�$։\011�ݝ�z��W�x��/]><�����<�{%$\010\020H\004\012��#A)��i��\\\\\\\034�F̜\
�y�ei��q��d��^��\026o^���_�L>J��\037\036�����9�,\035�`\024j��$Ifgg�8��\012!�$\
�Zk��R*��A\022g\000p�ɧ~��W�ya�Ƹ\031����:��Ĉ\022Q\000��z/���(��v���t:�v�\
�j����(�(M�(�\025s��\026�-\035?��߽|��\017��~���\033\001R\012\002���\020b:��(����*s\"�\
�Q�$E#m-�=����h<���~�����t�\022\025PP�h�F�7\003��BD栣��5[-\036������\
���#ƴ �T\025\034PFw��T�yDĀB2\003@�fMW���ӏ����?��;/>�\005\022#\"��/��W\032\
�AV�.�k��/\017\034:�㜙��\036�\010P\"\"\002����~�?U��4��p���\020D$����<ω���4\015!�\
e�K��ka��[o���\000\000\000\000IEND�B`�"
### end
