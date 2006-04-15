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
data = "‰PNG\015\012\032\012\000\000\000\015IHDR\000\000\000\032\000\000\000\030\010\002\000\000\000kàz’\000\000\000\003sBIT\010\010\010ÛáOà\000\000\0057IDAT8u•\
Mˆå\025ÇÏy>Þïû5w>îMb’\031cZhcB\015¢©\024*…,¬‚Øv%ŠíFtÙnºè¢Ô]K»påÂV\020©¨ Á\
âF\004\023Z!–Zª“d&“d2373wæ~½Ï×9.ÞÉ-ôì\036\036Þ?¿óœÿû?¸¶¶Öét\000\000\021\001ˆ€\001€™\005h\
d\"`\024J0\021\004DI\020\004\011\026’É\003J\004ª>dff\036\016‡j}}½V«!\"\021!2€\000\020\000À<BD\000Á\034\020520\002³C”È X\
\004á\001\0043\003€\020‚™www\0253÷z=\000\000\000\004Íà\000€9\010\0211!ŠÀŒ\000Dä=±/½ó“áØvççP0\012UÑ\021\021\"j­•\020\
¢¢ED\000/A\0218!tà\000\002(5“Ò\030çÁÛ±\012{\011\014V®ùf£‘æ‘@¬^FJID\000 *aD\004\000’LÞ\001áÄšÒ\030ç\
\034™áÞöÍ¹\006\024aKù=ç¬\017@®u{kó€>$ãý6\001@JÉÌwéÆãqpÞ8k\015Åb'öãŒz\002·ßþËGK\017.þ\
àä½ãÒ…`½‡z„½^o®;\027aqg†û¥\000€ˆÊrüùç—îÿVÒ’ÃBî’7Ž7f`ýÂñ\023§N¶¬\032ø(žl\
[I>“£kƒ\035g<'¬”ªèöý\020B\020BxOËËË£K9¯{7pÎ\030gÇVîî•G»åŸ^þàø·Ï$…,ƒ\031˜\021¸\
¾›8k}…&î\024\"\012DôÞ\033cò<¿~+X\017¥\017¥%W²±£Òº[ý€Yãíw/\026Òeñæ`b\006Ãq®ìíÛ\033!„J±\
\022…ÊbÕ+æyízß\033cœñÎ¹Òyë\002\031\037ËòÆÚ\015óŸwŽt\033§çUêz“É(ÆA¿¿WqŠÆÌûœZëv»½µ\
Ë[ýáÄxcÙ–Îzp\014@|êÌüòª«\037fÝïvï‰6¶Ç+++W¯^vÎU\036®D\021Q0³Ö:I’Z­&c½v«ô\
–Gv\\ú`­\015dY`£ˆ?]M/ýë\0326ï[:5,Í…/ûJèªY)¥”²jV\001€Ö:Š¢<Ïgê3›ƒI·é,û\020\
¸œ„ë\033î‹kƒ/¯ìlØò7¯ÂùÓ_Ô›>ý£\003ó«÷ß{dQJYqM‡«*ù$IÒ4™m\\ýjmuspåÖh\
yutck‡\030[f÷Ð‘Ã‹'n~uùó+OþìèÑƒÇnî®FÙ\003I’L¹ª\024Ø—ÓZgY¶°Ð}ï½ó\037mm5›\
Ín·{öÄ÷êõºÖšÈ—¥ït:üÛ[=üÏÚ±Îâ‚¸Ú$KµÖB\000dÅwé¢(Ê²¬Ùlž;wÎ9GDZ\
ë4MÓ4M’$Ö‰\011“Ý¾zú©WÞxë×/]><³´½ö¦<ø{%$\010\020H\004\012‘÷#A)•¦i³Ù\\\\\\\034FÌœ\
çy–eišÆq¬µd¢­^¿–\026o^üôã¿_ùL>Jƒí\037\036ø÷Á¥“9Ç,\035²`\024jêÀ$Ifggã8¶Ö\012!’$\
ÑZk­•R*’ÁA\022g\000pöÉ§~ù‡WžyaýÆ¸\031¿öþã¿:–ÎÄˆ\022Q\000±˜z/Š¢¢(Úív·Ûít:ív»\
ÕjÕëõ¢(’(Mã(¯\025sí™û\026-\035?ôÛß½|–Æ\017´”~ý¯Ö\033\001R\012\002¢ò¡\020b:¢(Š¢¨è*s\"¢\
ÔQ’$E#m-Ì=û‹ç¾ßh<¡“‡~ò„ùì¢ÙØtÈ\022\025PPÓhžFÍ7\003§ºBDæ £¤–5[-\036÷‡ýôç\
¾ðÉ#Æ´ ÇT\025\034PFwÓùT¾yDÄ€B2\003@œfMWšù¹Óœ¹àý?Òø;/>˜\005\022#\"°ø/ºÿW\032\
AV«.Ïk­–/\017\034:ûãœ™‹¢\036ë\010P\"\"\002©ÙÙÙ~¿?U¼³4öãpº÷„\020D$„¨þÓ<Ï‰ˆ™Ó4\015!”\
eéœK’äka±â[oÙÏö\000\000\000\000IEND®B`‚"
### end
