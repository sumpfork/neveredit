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
                    <size>500,30</size>\012                  </\
object>\012                  \012                  <flag>wxLEFT|wx\
RIGHT|wxGROW</flag>\012                  \012                  <bo\
rder>5</border>\012                </object>\012              </ob\
ject>\012              <tooltip>General Neveredit Preferences</\
tooltip>\012            </object>\012          </object>\012         \
 <object class=\"notebookpage\">\012            <label>Key Mappin\
gs</label>\012            <object class=\"wxPanel\" name=\"UserCon\
trolsPanel\">\012              <object class=\"wxGridSizer\">\012    \
            <rows>2</rows>\012                <cols>4</cols>\012  \
              <object class=\"sizeritem\">\012                  <\
object class=\"wxStaticText\" name=\"upText\">\012                 \
   \012                    <label>Up Key</label>  \012            \
      </object>\012                  \012                  <flag>w\
xALIGN_CENTRE</flag>\012                  \012                </ob\
ject>\012                <object class=\"sizeritem\">\012           \
       <object class=\"wxTextCtrl\" name=\"mwUpKey\">\012          \
        </object>\012                  \012                  <flag\
>wxLEFT|wxRIGHT|wxALIGN_CENTRE</flag>\012                  \012   \
             </object>\012                <object class=\"sizeri\
tem\">\012                  <object class=\"wxStaticText\" name=\"d\
ownText\">\012                    \012                    <label>Do\
wn Key</label>  \012                  </object>\012               \
   \012                  <flag>wxALIGN_CENTRE</flag>\012          \
        \012                </object>\012                <object c\
lass=\"sizeritem\">\012                  <object class=\"wxTextCtr\
l\" name=\"mwDownKey\">\012                  </object>\012           \
       \012                  <flag>wxLEFT|wxRIGHT|wxALIGN_CENTR\
E</flag>\012                  \012                </object>\012      \
          <object class=\"sizeritem\">\012                  <obje\
ct class=\"wxStaticText\" name=\"leftText\">\012                   \
 \012                    <label>Left Key</label>\012              \
    </object>\012                  \012                  <flag>wxA\
LIGN_CENTRE</flag>\012                  \012                </obje\
ct>\012                <object class=\"sizeritem\">\012             \
     <object class=\"wxTextCtrl\" name=\"mwLeftKey\">\012          \
        </object>\012                  \012                  <flag\
>wxLEFT|wxRIGHT|wxALIGN_CENTRE</flag>\012                  \012   \
             </object>\012                <object class=\"sizeri\
tem\">\012                  <object class=\"wxStaticText\" name=\"r\
ightText\">\012                    \012                    <label>R\
ight Key</label>\012                  </object>\012               \
   \012                  <flag>wxALIGN_CENTRE</flag>\012          \
        \012                </object>\012                <object c\
lass=\"sizeritem\">\012                  <object class=\"wxTextCtr\
l\" name=\"mwRightKey\">\012                  </object>\012          \
        \012                  <flag>wxLEFT|wxRIGHT|wxALIGN_CENT\
RE</flag>\012                  \012                </object>\012     \
         </object>\012              <tooltip>Define Keys to Con\
trol App Navigation</tooltip>\012            </object>\012        \
  </object>\012          <object class=\"notebookpage\">\012        \
    <label>Script Editor</label>\012            <object class=\"\
wxPanel\" name=\"ScriptEditorPanel\">\012              <object cla\
ss=\"wxBoxSizer\">\012                <orient>wxVERTICAL</orient>\
\012                <object class=\"sizeritem\">\012                \
  <object class=\"wxCheckBox\" name=\"ScriptAntiAlias\">\012       \
             \012                    <label>Use Font Antialiasi\
ng</label>\012                  </object>\012                  \012  \
                <flag>wxALL|wxGROW</flag>\012                  \
\012                  <border>10</border>\012                </obj\
ect>\012                <object class=\"sizeritem\">\012            \
      <object class=\"wxCheckBox\" name=\"ScriptAutoCompile\">\012 \
                   \012                    <label>Automatically\
 Compile Script when Editor Closed</label>\012                 \
 </object>\012                  \012                  <flag>wxALL|\
wxGROW</flag>\012                  \012                  <border>1\
0</border>\012                </object>\012              </object>\
\012              <tooltip>Script Editor Specific Preferences</\
tooltip>\012            </object>\012          </object>\012         \
 <object class=\"notebookpage\">\012            <label>Language</\
label>\012            <object class=\"wxPanel\" name=\"TextPanel\">\
\012              <object class=\"wxBoxSizer\">\012                <\
orient>wxVERTICAL</orient>\012                <object class=\"si\
zeritem\">\012                  <object class=\"wxBoxSizer\">\012    \
                <orient>wxHORIZONTAL</orient>\012              \
      <object class=\"sizeritem\">\012                      <obje\
ct class=\"wxChoice\" name=\"DefaultLocStringLang\">\012           \
             \012                        <content>\012            \
              <item>english</item>\012                         \
 <item>french</item>\012                          <item>german<\
/item>\012                          <item>italian</item>\012      \
                    <item>spanish</item>\012                   \
       <item>polish</item>\012                          <item>k\
orean</item>\012                          <item>chinese traditi\
onal</item>\012                          <item>chinese simplifi\
ed</item>\012                          <item>japanese</item>\012  \
                      </content>\012                        \012  \
                      <selection>0</selection>\012             \
         </object>\012                      \012                  \
    <flag>wxALL|wxGROW</flag>\012                      \012       \
               <border>10</border>\012                    </obj\
ect>\012                    <object class=\"sizeritem\">\012        \
              <object class=\"wxStaticText\" name=\"defaultLang\
Label\">\012                        \012                        <la\
bel>Default language for translatable strings</label>\012      \
                </object>\012                      \012           \
           <flag>wxALL|wxGROW</flag>\012                      \012\
                      <border>10</border>\012                  \
  </object>\012                  </object>\012                </ob\
ject>\012              </object>\012              <tooltip>Game la\
nguage preferences</tooltip>\012            </object>\012         \
 </object>\012        </object>\012        \012        <flag>wxBOTTOM\
|wxALL|wxEXPAND|wxGROW</flag>\012        \012        <border>5</bo\
rder>\012        \012        <cellpos>1,1</cellpos>\012      </object\
>\012      <object class=\"sizeritem\">\012        <object class=\"wx\
BoxSizer\">\012          <orient>wxHORIZONTAL</orient>\012         \
 <object class=\"sizeritem\">\012            <object class=\"wxBut\
ton\" name=\"ID_CANCEL\">\012              \012              <label>C\
ancel</label>\012            </object>\012            \012           \
 <flag>wxALIGN_CENTRE_VERTICAL|wxALIGN_CENTRE_HORIZONTAL</fl\
ag>\012          </object>\012          <object class=\"sizeritem\">\
\012            <object class=\"wxButton\" name=\"ID_OK\">\012        \
      \012              <label>Ok</label>\012              \012      \
        <default>1</default>\012            </object>\012         \
   \012            <flag>wxALIGN_CENTRE_VERTICAL|wxALIGN_CENTRE\
_HORIZONTAL</flag>\012          </object>\012        </object>\012   \
     \012        <flag>wxALL|wxALIGN_RIGHT|wxALIGN_BOTTOM</flag\
>\012        \012        <border>5</border>\012        \012        <cell\
pos>2,1</cellpos>\012      </object>\012      <growablecols>1</gro\
wablecols>\012      <growablerows>1</growablerows>\012    </object\
>\012  </object>\012</resource>"
### end
