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
data = "‰PNG\015\012\032\012\000\000\000\015IHDR\000\000\000\032\000\000\000\030\010\002\000\000\000kàz’\000\000\000\003sBIT\010\010\010ÛáOà\000\000\005VIDAT8UU\
Kl]W\025]kŸsï{÷=ÿ^\\›Ô\016Žóqš\006\012\001Š\020\010\004B0c’\011\031FÈ”Q*fH\021H\031Uda2 4ª\"˜EU\
G J`!ÔFj«’&\020•*4¶kçãß{~÷ÞsÏÙ›Ás%Ø£=ØŸµö—\017\037><|xÎ\000PE\001ª\001€ÐD‘<\030a$\
\001\001\024BD¥óf\011P3:Š‚D4ÈnÇ¯¯¯“ff€\000\002\023¸¤\032\034œRhbT@iBƒ\012€Èä $ÍŒ\006\001# ûý\
¡'¹õä©Â\000\020\012À \000\000%\035M\022\023\000&Û³á¦=ÚÀ£írïGÅ\017 &\"€Ž€ÓDrñ\000T\024J\021o–Œ*\020K\012¡Yª\
´ÜÄö¦n¬Ùæ®>õ±\034ñ\017{\037|/ûæDÞ¥\011\035h’\014$•ð\000œ9ŠKLJzä1†M}¼ž\036o`ã\021·óØÏÂî\
X=8Z—eµO\022ºõ½;ß˜úZV¸\021\025¡\030á,óf\006a°\025v¶ìÉ*66õ\0219ôqo¬é/¥²\016\003‹\022\022÷b-Ê\
PëbëÐ;û\037¼8~67uÌ•‰$\015fÉ“„¥j÷\027OùÃÞé)³\023ºk±®bÒ¨÷ÞÝ›ÿBK“G“4¢Iˆ1\035\
uÙ_ôýŸ6?n¡pBÂ{‹Á\011ÍÄÌ\024y;å›wŸ”ëw'ãz¨‡eH©jª2¼ùêã¿;¬†V‡Ô„ª®K\015:6\
à*>-«Š‰â¢\023Qa.Ž¤\000ÐTVUõBöü½§;±–\030µiR¨R=hÔìO¯?ùäý½¦LMpÖ°®C\030\014\027´ó÷\
æ½ˆ\000ó\020ó’‘\016š\004€øÌ’.¹“ÿ\032lÅJC\010ZjY¦þ®‚ñÕ×~ó×?>ùèÎ ÔÖ”h‚ÕM8:ì¼\027î¥H\
ÒH’Ž4ˆ\023’^Xdþlqê“Po÷ËX1ÄXÖ©\032Ö4™;üì+¿¾rûÖÎÃ\017\007USÅ*íì„Ý×ß~øNl\032š\
dB:8ç ô\000¼og­¢7ùÌ‘gïomŸžžÔ&±²z_\001dÎ?wúØKË?»qãFó|¹nO›ÒŸœ<öÝñ\027Í\
\014\000½ƒ\031À$Ñ\003È½Ë‹±vÑýRë‹÷Ë·×\023\014®lB]5€ÒymxbéøO^Z¾ñÛ×¾ÿÂw¾þÕoÍÌL~\
~Læè˜\003\015á0Ú@ñY+—±nñåÎÉÕz¸¶>üó?ÿóû¿Ý}ý­\017’R\035bÓívgff–——ïßù¨ßßž\
ššèŒu½d\"\012É)æT<\000/Ìó¼èv¾2uvë­ð»Oï\035ï.œ<5znåñJ\010±iš—_þ90:5î\
7Þ<vìÄ™3gÆ:ãYæD¼\000@f\024OCæœæí¢h\035ššzåÛ¿ÂP-©™\015Cµ²²\022B¸pá\002I\000×®]{ðàÁ\
ÂÂÂÜÜ\\§ÓÉóÜ{\017àà¶Ày¥˜ƒSt‹‰±Cƒ3‹gö÷ûjt°ýr\010µóçÏŸ;wîÖ­[fvûöíÅÅÅ¢\
(Z­V»ÝÎó|\024\013€™\031\032!Ô1÷y–µüìô3G\026>·tòøs§N-ž\\œ››#yñâÅÙÙÙK—.\001¸yóf¯×\
›šš*ŠÂ{/\"Î9\021!)\"¤ó4@Ì1k\033²NÖÊ‹¤\"N«P{øë×¯\017\006ƒªªúýþ\010ÂêêêÒÒRQ\024Y–9ç\
\016f…<¨,„ÎÑ¨’å®åÚcíñ‰ÖøX§“·'&&fgg\03492??ßëõ._¾LòêÕ«\"’e™÷žä\010ÝH\000õ\
É\024\020\021¥YN\011\016¢bêZ…AØ*Úf6\030\014Ddmmm\004!„\020cÌ²ì \003¤ˆ¨j2zgt\024À'I\012ñ\006Bà\015æ\013‘v»\
mfyž§”ö÷÷¯\\¹ÒívGìDäÿhŠôF@\010˜;x\021 \000 ƒ˜ãÈZDz½^Ó4ý~ß{ŸçùÈùÀž\034UÐ\031\
üôôôîîî(•ª’$9Rð™˜YJ©ÝnÖA–eÙ4ÍÿN\011€V«õ_7Bê”\\\010Ód\000\000\000\000IEND®B`‚"
### end
