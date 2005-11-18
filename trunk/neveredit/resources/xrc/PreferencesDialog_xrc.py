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
<object class=\"unknown\" name=\"AppDir\">\012                    <\
size>500,30</size>\012                  </object>\012             \
     <flag>wxLEFT|wxRIGHT|wxGROW</flag>\012                  <b\
order>5</border>\012                </object>\012              </o\
bject>\012              <tooltip>General Neveredit Preferences<\
/tooltip>\012            </object>\012          </object>\012        \
  <object class=\"notebookpage\">\012            <label>Screen Co\
ntrols</label>\012            <object class=\"wxPanel\" name=\"Use\
rControlsPanel\">\012              <object class=\"wxGridSizer\">\012\
                <rows>2</rows>\012                <cols>4</cols\
>\012                <object class=\"sizeritem\">\012               \
   <object class=\"wxStaticText\" name=\"upText\">\012             \
       <label>Up Key</label>  \012                  </object>\012 \
                 <flag>wxALL|wxGROW</flag>\012                 \
 <border>10</border>\012                </object>\012             \
   <object class=\"sizeritem\">\012                  <object clas\
s=\"wxTextCtrl\" name=\"mwUpKey\">\012                  </object>\012 \
                 <flag>wxALL|wxGROW</flag>\012                 \
 <border>10</border>\012                </object>\012             \
   <object class=\"sizeritem\">\012                  <object clas\
s=\"wxStaticText\" name=\"downText\">\012                    <label\
>Down Key</label>  \012                  </object>\012            \
      <flag>wxALL|wxGROW</flag>\012                  <border>10\
</border>\012                </object>\012                <object \
class=\"sizeritem\">\012                  <object class=\"wxTextCt\
rl\" name=\"mwDownKey\">\012                  </object>\012          \
        <flag>wxALL|wxGROW</flag>\012                  <border>\
10</border>\012                </object>\012                <objec\
t class=\"sizeritem\">\012                  <object class=\"wxStat\
icText\" name=\"leftText\">\012                    <label>Left Key\
</label>\012                  </object>\012                  <flag\
>wxALL|wxGROW</flag>\012                  <border>10</border>\012 \
               </object>\012                <object class=\"size\
ritem\">\012                  <object class=\"wxTextCtrl\" name=\"m\
wLeftKey\">\012                  </object>\012                  <fl\
ag>wxALL|wxGROW</flag>\012                  <border>10</border>\
\012                </object>\012                <object class=\"si\
zeritem\">\012                  <object class=\"wxStaticText\" nam\
e=\"rightText\">\012                    <label>Right Key</label>\012\
                  </object>\012                  <flag>wxALL|wx\
GROW</flag>\012                  <border>10</border>\012          \
      </object>\012                <object class=\"sizeritem\">\012 \
                 <object class=\"wxTextCtrl\" name=\"mwRightKey\
\">\012                  </object>\012                  <flag>wxALL\
|wxGROW</flag>\012                  <border>10</border>\012       \
         </object>\012              </object>\012              <to\
oltip>Define Keys to Control App Navigation</tooltip>\012      \
      </object>\012          </object>\012          <object class=\
\"notebookpage\">\012            <label>Script Editor</label>\012   \
         <object class=\"wxPanel\" name=\"ScriptEditorPanel\">\012 \
             <object class=\"wxBoxSizer\">\012                <or\
ient>wxVERTICAL</orient>\012                <object class=\"size\
ritem\">\012                  <object class=\"wxCheckBox\" name=\"S\
criptAntiAlias\">\012                    <label>Use Font Antiali\
asing</label>\012                  </object>\012                  \
<flag>wxALL|wxGROW</flag>\012                  <border>10</bord\
er>\012                </object>\012                <object class=\
\"sizeritem\">\012                  <object class=\"wxCheckBox\" na\
me=\"ScriptAutoCompile\">\012                    <label>Automatic\
ally Compile Script when Editor Closed</label>\012             \
     </object>\012                  <flag>wxALL|wxGROW</flag>\012 \
                 <border>10</border>\012                </objec\
t>\012              </object>\012              <tooltip>Script Edi\
tor Specific Preferences</tooltip>\012            </object>\012   \
       </object>\012          <object class=\"notebookpage\">\012   \
         <label>Text</label>\012            <object class=\"wxPa\
nel\" name=\"TextPanel\">\012              <object class=\"wxBoxSiz\
er\">\012                <orient>wxVERTICAL</orient>\012           \
     <object class=\"sizeritem\">\012                  <object cl\
ass=\"wxBoxSizer\">\012                    <orient>wxHORIZONTAL</\
orient>\012                    <object class=\"sizeritem\">\012     \
                 <object class=\"wxChoice\" name=\"DefaultLocSt\
ringLang\">\012                        <content>\012               \
           <item>english</item>\012                          <i\
tem>french</item>\012                          <item>german</it\
em>\012                          <item>italian</item>\012         \
                 <item>spanish</item>\012                      \
    <item>polish</item>\012                          <item>kore\
an</item>\012                          <item>chinese traditiona\
l</item>\012                          <item>chinese simplified<\
/item>\012                          <item>japanese</item>\012     \
                   </content>\012                        <selec\
tion>0</selection>\012                      </object>\012         \
             <flag>wxALL|wxGROW</flag>\012                     \
 <border>10</border>\012                    </object>\012         \
           <object class=\"sizeritem\">\012                      \
<object class=\"wxStaticText\" name=\"defaultLangLabel\">\012      \
                  <label>Default language for translatable s\
trings</label>\012                      </object>\012             \
         <flag>wxALL|wxGROW</flag>\012                      <bo\
rder>10</border>\012                    </object>\012             \
     </object>\012                </object>\012              </obj\
ect>\012              <tooltip>Text specific preferences</toolt\
ip>\012            </object>\012          </object>\012        </obje\
ct>\012        <flag>wxBOTTOM|wxALL|wxEXPAND|wxGROW</flag>\012    \
    <border>5</border>\012        <cellpos>1,1</cellpos>\012      \
</object>\012      <object class=\"sizeritem\">\012        <object c\
lass=\"wxBoxSizer\">\012          <orient>wxHORIZONTAL</orient>\012 \
         <object class=\"sizeritem\">\012            <object clas\
s=\"wxButton\" name=\"ID_CANCEL\">\012              <label>Cancel</\
label>\012            </object>\012            <flag>wxALIGN_CENTR\
E_VERTICAL|wxALIGN_CENTRE_HORIZONTAL</flag>\012          </obje\
ct>\012          <object class=\"sizeritem\">\012            <object\
 class=\"wxButton\" name=\"ID_OK\">\012              <label>Ok</lab\
el>\012              <default>1</default>\012            </object>\
\012            <flag>wxALIGN_CENTRE_VERTICAL|wxALIGN_CENTRE_HO\
RIZONTAL</flag>\012          </object>\012        </object>\012      \
  <flag>wxALL|wxALIGN_RIGHT|wxALIGN_BOTTOM</flag>\012        <b\
order>5</border>\012        <cellpos>2,1</cellpos>\012      </obje\
ct>\012      <growablecols>1</growablecols>\012      <growablerows\
>1</growablerows>\012    </object>\012  </object>\012</resource>\012"
### end
