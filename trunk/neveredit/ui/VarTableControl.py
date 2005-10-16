import wx
from neveredit.file.GFFFile import GFFStruct

class VarControl(wx.BoxSizer):

    def __init__(self,owner,parent,pname,ptype,pvalue):
        if ptype in [2,4,5]:
            return
        wx.BoxSizer.__init__(self,wx.HORIZONTAL)
        self.owner = owner
        self.dataType = ptype
        self.parent = parent
        valid_types = [_('integer'),_('float'),_('string'),\
                                            _('object'),_('location')]
        self.control_memory = {self.dataType:pvalue}

        self.left_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.name_control = wx.TextCtrl(self.parent,-1)
        self.name_control.SetValue(pname)
        self.type_control = wx.Choice(self.parent,-1,\
                        choices=valid_types,style=wx.LB_SINGLE)
        self.type_control.SetSelection(self.dataType-1)
        
        self.left_sizer.Add(self.name_control,flag=wx.ALL,border=2)
        self.left_sizer.Add(self.type_control,\
                            flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=2)

        wx.EVT_CHOICE(self.parent,self.type_control.GetId(),self.typeSelect)
        wx.EVT_TEXT(self.parent,self.name_control.GetId(),self.valueChanged)

        self.Add(self.left_sizer,wx.ALL,border=2)

        self.setDataControl()

    def setDataControl(self):
        if self.dataType == 1:
            # integer, use wx.SpinCtrl
            self.data_control = wx.SpinCtrl(self.parent,-1)
            self.data_control.SetRange(-2147483648,2147483647)
            # full Int range and not 0-100
            
            if self.dataType in self.control_memory.keys():
                self.data_control.SetValue(self.control_memory[self.dataType])
            else:
                self.data_control.SetValue(0)
            
            wx.EVT_SPINCTRL(self.parent,self.data_control.GetId(),self.valueChanged)
            wx.EVT_TEXT(self.parent,self.data_control.GetId(),self.valueChanged)
        elif self.dataType in [2,3]:
            # string, use a TextCtrl
            self.data_control = wx.TextCtrl(self.parent,-1)
            if self.dataType in self.control_memory.keys():
                self.data_control.SetValue(self.control_memory[self.dataType])
        elif self.dataType in[4,5]:
            # object and location - unsupported
            self.data_control = wx.StaticText(self.parent,-1,'Uneditable Data')
            if self.dataType in self.control_memory.keys():
                self.data_control.SetValue(self.control_memory[self.dataType])
        if self.data_control:
            self.Add(self.data_control,flag=wx.ALL,border=2)
        self.Layout()
        self.parent.propGrid.Layout()

    def GetId(self):
        return self.name_control.GetId()

    def Destroy(self):
        self.name_control.Destroy()
        self.type_control.Destroy()
        if self.data_control:
            self.data_control.Destroy()
        wx.BoxSizer.Destroy(self)

    def typeSelect(self,event):
        # then change the data control type
        dataType=self.type_control.GetSelection()+1
        if dataType != self.dataType:
            # first, store the data value
            if self.dataType in [1,2,3]:
                self.control_memory[self.dataType]=self.\
                                                data_control.GetValue()
            if self.dataType in [4,5]:
                # we didn't edit the data - if it's not there yet,
                # it wasn't there at the begining
                pass

            # remove the previous control
            oldcontrol=self.data_control
            self.Detach(self.data_control)
            oldcontrol.Destroy()
            self.Layout()
            # now set the new control up
            self.dataType = dataType
            self.setDataControl()
            event.SetId(self.owner.GetId())
            self.parent.controlUsed(event)

    def valueChanged(self,event):
        event.SetId(self.owner.GetId())
        self.parent.controlUsed(event)

    def GetData(self):
        ret_name = self.name_control.GetValue()
        ret_type = self.type_control.GetSelection()+1
        if ret_type in [1,3]:
            # TextCtrl and SpinCtrl support GetValue()
            ret_value = self.data_control.GetValue()
        elif ret_type == 2:
            # must check if the value is a float
            strnumber = self.data_control.GetValue()
            try:
                ret_value = float(strnumber)
            except ValueError:
                # it's not a float string
                ret_value = 0.0 # a bit harsh...
        else:
            # we should return those unknown values as they were given...
            if self.dataType in self.control_memory.keys():
                ret_value = self.control_memory[self.dataType]
            else:
                # I don't really know what I should do there
                pass # in the best case, an error will be raised somewhere
        return ret_name,ret_type,ret_value

class VarListControl(wx.BoxSizer):

    def __init__(self,prop,parent):
        wx.BoxSizer.__init__(self,wx.VERTICAL)
        self.commands_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.parent = parent

        # add command controls : add and delete variable
        self.addBtn = wx.Button(parent,-1,_('add var'))
        self.commands_sizer.Add(self.addBtn,flag=wx.ALL)

        self.Add(self.commands_sizer)
        wx.EVT_BUTTON(parent,self.addBtn.GetId(),self.addBtnPressed)

        self.varControls_sizer = wx.BoxSizer(wx.VERTICAL)
        self.Add(self.varControls_sizer)
        self.addVarControls(prop.getValue())

    def addVarControls(self,vlist):
        self.VarControls = []
        for i in range(len(vlist)):
            self.VarControls.append(VarControl(self,self.parent,vlist[i].\
                getEntry('Name')[0],vlist[i].getEntry('Type')[0],\
                vlist[i].getEntry('Value')[0]))
            self.varControls_sizer.Add(self.VarControls[i],flag=wx.ALL)

    def addBtnPressed(self,event):
        # create a control
        # the GetData method will take care of the data struct creation
        control = VarControl(self,self.parent,'',1,0)
        self.VarControls.append(control)
        self.varControls_sizer.Add(control)
        self.Layout()
        self.parent.propGrid.Layout()
        self.parent.SetupScrolling()
        event.SetId(self.GetId())
        self.parent.controlUsed(event)

    def Destroy(self):
        for c in self.VarControls:
            c.Destroy()
        self.addBtn.Destroy()

    def GetData(self):
        var_list = []
        for c in self.VarControls:
            vname,vtype,vdata = c.GetData()
            if vname !='':
                # create the GFFStruct
                s = GFFStruct()
                s.add('Name',vname,'CExoString')
                s.add('Type',vtype,'DWORD')
                s.add('Value',vdata,(lambda x:\
                    ['','INT','FLOAT','CExoString','DWORD','Struct'][x])(vtype))
                var_list.append(s)
        return var_list

    def GetId(self):
        return self.addBtn.GetId()
