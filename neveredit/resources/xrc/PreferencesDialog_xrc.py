# -*- coding: ISO-8859-1 -*-
"""Resource PreferencesDialog_xrc (from file PreferencesDialog.xrc)"""
# written by resourcepackage: (1, 0, 0)
source = 'PreferencesDialog.xrc'
package = 'neveredit.resources.xrc'
data = "<?xml version=\"1.0\" ?>\012<resource>\012  <object class=\"wxDialog\"\
 name=\"PrefDialog\">\012    <title>Preferences</title>\012    <size\
>550,200</size>\012    <object class=\"wxGridBagSizer\">\012      <o\
bject class=\"sizeritem\">\012        <object class=\"wxNotebook\" \
name=\"PrefNotebook\">\012          <object class=\"notebookpage\">\
\012            <label>General</label>\012            <object clas\
s=\"wxPanel\" name=\"GeneralPanel\">\012              <object class\
=\"wxBoxSizer\">\012                <orient>wxVERTICAL</orient>\012 \
               <object class=\"sizeritem\">\012                  \
<object class=\"unknown\" name=\"AppDir\">\012                    \012\
                    \012                    <size>500,30</size>\
\012                  </object>\012                  \012            \
      \012                  <flag>wxLEFT|wxRIGHT|wxGROW</flag>\012\
                  \012                  \012                  <bor\
der>5</border>\012                </object>\012              </obj\
ect>\012              <tooltip>General Neveredit Preferences</t\
ooltip>\012            </object>\012          </object>\012          \
<object class=\"notebookpage\">\012            <label>Script Edit\
or</label>\012            <object class=\"wxPanel\" name=\"ScriptE\
ditorPanel\">\012              <object class=\"wxBoxSizer\">\012     \
           <orient>wxVERTICAL</orient>\012                <obje\
ct class=\"sizeritem\">\012                  <object class=\"wxChe\
ckBox\" name=\"ScriptAntiAlias\">\012                    \012        \
            \012                    <label>Use Font Antialiasin\
g</label>\012                  </object>\012                  \012   \
               \012                  <flag>wxALL|wxGROW</flag>\012\
                  \012                  \012                  <bor\
der>10</border>\012                </object>\012                <o\
bject class=\"sizeritem\">\012                  <object class=\"wx\
CheckBox\" name=\"ScriptAutoCompile\">\012                    \012   \
                 \012                    <label>Automatically C\
ompile Script when Editor Closed</label>\012                  <\
/object>\012                  \012                  \012             \
     <flag>wxALL|wxGROW</flag>\012                  \012          \
        \012                  <border>10</border>\012             \
   </object>\012              </object>\012              <tooltip>\
Script Editor Specific Preferences</tooltip>\012            </o\
bject>\012          </object>\012          <object class=\"notebook\
page\">\012            <label>Text</label>\012            <object c\
lass=\"wxPanel\" name=\"TextPanel\">\012              <object class\
=\"wxBoxSizer\">\012                <orient>wxVERTICAL</orient>\012 \
               <object class=\"sizeritem\">\012                  \
<object class=\"wxBoxSizer\">\012                    <orient>wxHO\
RIZONTAL</orient>\012                    <object class=\"sizerit\
em\">\012\011\011\011    <object class=\"wxChoice\" name=\"DefaultLocStringL\
ang\">\012                        \012                        <cont\
ent>\012                          <item>english</item>\012        \
                  <item>french</item>\012                      \
    <item>german</item>\012                          <item>ital\
ian</item>\012                          <item>spanish</item>\012  \
                        <item>polish</item>\012                \
          <item>korean</item>\012                          <ite\
m>chinese traditional</item>\012                          <item\
>chinese simplified</item>\012                          <item>j\
apanese</item>\012                        </content>\012          \
              \012                        <selection>0</selecti\
on>\012                      </object>\012                      \012 \
                     <flag>wxALL|wxGROW</flag>\012             \
         \012                      <border>10</border>\012        \
            </object>\012                    <object class=\"siz\
eritem\">\012                      <object class=\"wxStaticText\" \
name=\"defaultLangLabel\">\012                        \012          \
              <label>Default language for translatable strin\
gs</label>\012                      </object>\012                 \
     \012                      <flag>wxALL|wxGROW</flag>\012      \
                \012                      <border>10</border>\012 \
                   </object>\012                  </object>\012   \
             </object>\012              </object>\012             \
 <tooltip>Text specific preferences</tooltip>\012            </\
object>\012          </object>\012        </object>\012        \012     \
   \012        <flag>wxBOTTOM|wxALL|wxEXPAND|wxGROW</flag>\012    \
    \012        \012        <border>5</border>\012        \012        \012 \
       <cellpos>1,1</cellpos>\012      </object>\012      <object \
class=\"sizeritem\">\012        <object class=\"wxBoxSizer\">\012     \
     <orient>wxHORIZONTAL</orient>\012          <object class=\"\
sizeritem\">\012            <object class=\"wxButton\" name=\"ID_CA\
NCEL\">\012              \012              \012              <label>Ca\
ncel</label>\012            </object>\012            \012            \
\012            <flag>wxALIGN_CENTRE_VERTICAL|wxALIGN_CENTRE_HO\
RIZONTAL</flag>\012          </object>\012          <object class=\
\"sizeritem\">\012            <object class=\"wxButton\" name=\"ID_O\
K\">\012              \012              \012              <label>Ok</l\
abel>\012              \012              \012              <default>1\
</default>\012            </object>\012            \012            \012 \
           <flag>wxALIGN_CENTRE_VERTICAL|wxALIGN_CENTRE_HORI\
ZONTAL</flag>\012          </object>\012        </object>\012        \
\012        \012        <flag>wxALL|wxALIGN_RIGHT|wxALIGN_BOTTOM</\
flag>\012        \012        \012        <border>5</border>\012        \012\
        \012        <cellpos>2,1</cellpos>\012      </object>\012    \
  <growablecols>1</growablecols>\012      <growablerows>1</grow\
ablerows>\012    </object>\012  </object>\012</resource>"
### end
