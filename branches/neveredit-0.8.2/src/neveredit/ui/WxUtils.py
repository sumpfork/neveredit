import wx

def bitmapFromImage(i):
    image = wx.EmptyImage(i.size[0], i.size[1])
    image.SetData(i.convert('RGB').tostring())
    return image.ConvertToBitmap()
    
