# -*- coding: ISO-8859-1 -*-
"""Resource select_icon_png (from file select_icon.png)"""
# written by resourcepackage: (1, 0, 0)
source = 'select_icon.png'
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
data = "�PNG\015\012\032\012\000\000\000\015IHDR\000\000\000\032\000\000\000\030\010\002\000\000\000k�z�\000\000\000\003sBIT\010\010\010��O�\000\000\005VIDAT8�UU\
Kl]W\025]k�s�{�=�^\\��\016��q�\006\012\001�\020\010\004B0c�\011\031FȔQ*fH\021H\031Ud�a2�4�\"���EU\
G�J`!�Fj��&\020�*4�k���{~��s�ٛ�s%أ=؟���\017\037><|x�\000PE\001�\001��D�<\030a$\
\001\001\024BD��f\011P3:��D4�nǯ������ff�\000\002\023��\032\034�RhbT@iB�\012��� $͌\006\001# ��\
�'����\000\020\012� \000\000%\035M\022\023\000&۳�=����r�G�\017 &\"����Dr�\000T\024J\021o��*\020K\012�Y�\
�����n���>��\034��\017{\037|/��Dޥ\011\035h�\014$��\000�9�KLJz�1�M}��\036o`�\021������\
X=8Z�e�O\022����;ߘ�ZV�\021\025�\030�,�f\006a��\025v���*66�\0219�qo��/��\016\003�\022\022�b-�\
P�b��;�\037�8~67u̕�$\015fɓ���j�\027O����)�\023�k��bҨ��ݛ�BK�G�4�I�1\035\
u�_���6?n�pB�{��\011���\024y;�w���w'�z��eH�j�2�����;��V�Ԅ��K\015:6\
�*>-����\023Qa.��\000�TVU�B����;��\030�iR�R=h��O�?�����LMpְ�C\030\014\027���\
潈\000�\020�\016�\004��̒.���\032l�JC\010ZjY�������~��?>��� �֔h��M8:�\027�H\
�H��4�\023�^Xd�lq�Po��X1�X֩\032�4�;��+��r����\017\007US�*��ݏ��~�Nl\032�\
dB:8��\000�og��7�̑�g�om����&��z_\001d�?w��K�?�q�F�|�nO�ҟ�<���\027�\
\014\000��\031�$�\003Ƚˋ�v��R��˷��\023\014�lB]5��ymxb��O^Z���׾��w���o��L~\
~�L��\003\015�0�@�Y+��n�����z��>��?�����}��\017��R\035b��vgff��������ߞ\
������u�d\"\012�)�T<\000/���v�2uv��O�\035�.��<5zn��J\010�i��_�90:5�\
7�<v�ę3g�:�Y�D�\000@f\024OC���h\035��z�ۿ�P-��\015C���\022B�p�\002I\000׮]{���\
�����\\�����{\017���y���St���C�3�g���jt��r\010���ϟ;w�֭[fv�����Ţ\
(Z�V����|\024\013��\031\032!�1�y�����3G\026>�t��s�N-�\\���#y������K�.\001�y�f��\
���*��{/\"�9\021!)\"��4@�1k\033�N�ʋ�\"N�P{��ׯ\017\006������\010������RQ\024Y�9�\
\016f�<�,��Ѩ����c����X���'&&fgg�\03492??���._�L��ի\"�e����\010�H\000�\
�\024\020\021�YN\011\016�b�Z�A�*�f6\030\014Ddmmm\004!�\020c̲�\003���j2zgt\024�'I\012�\006B�\015�\013�v�\
mfy�������\\���vG�D��h���F@\010�;x\021�\000�����ZDz�^�4�~�{�������\034U�\031\
�������(���$9R�YJ��n�A�e�4��N\011�V��_7B�\\\010�d\000\000\000\000IEND�B`�"
### end
