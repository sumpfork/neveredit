# -*- coding: ISO-8859-1 -*-
"""Resource __init___py~ (from file __init__.py~)"""
# written by resourcepackage: (1, 0, 0)
source = '__init__.py~'
package = 'neveredit.resources.images'
data = "\"\"\"Design-time __init__.py for resourcepackage\015\012\015\012This is th\
e scanning version of __init__.py for your\015\012resource modules\
. You replace it with a blank or doc-only\015\012init when ready t\
o release.\015\012\"\"\"\015\012try:\015\012\011__file__\015\012except NameError:\015\012\011pass\015\012\
else:\015\012\011import os\015\012\011if os.path.splitext(os.path.basename( __\
file__ ))[0] == \"__init__\":\015\012\011\011try:\015\012\011\011\011from resourcepackage\
 import package, defaultgenerators\015\012\011\011\011generators = defaultg\
enerators.generators.copy()\015\012\011\011\011\015\012\011\011\011### CUSTOMISATION POINT\
\015\012\011\011\011## import specialised generators here, such as for wxPy\
thon\015\012\011\011\011#from resourcepackage import wxgenerators\015\012\011\011\011#gene\
rators.update( wxgenerators.generators )\015\012\011\011except ImportErr\
or:\015\012\011\011\011pass\015\012\011\011else:\015\012\011\011\011package = package.Package(\015\012\011\011\011\011pa\
ckageName = __name__,\015\012\011\011\011\011directory = os.path.dirname( os.p\
ath.abspath(__file__) ),\015\012\011\011\011\011generators = generators,\015\012\011\011\011)\
\015\012\011\011\011package.scan(\015\012\011\011\011\011### CUSTOMISATION POINT\015\012\011\011\011\011## forc\
e true -> always re-loads from external files, otherwise\015\012\011\011\
\011\011## only reloads if the file is newer than the generated .p\
y file.\015\012\011\011\011\011# force = 1, \015\012\011\011\011)\015\012\011\011\015\012"
### end
