from objc_util import *
import ctypes,re


class_copyPropertyList = c.class_copyPropertyList
class_copyPropertyList.restype = ctypes.POINTER(c_void_p)
class_copyPropertyList.argtypes = [c_void_p, ctypes.POINTER(ctypes.c_uint)]
property_getName = c.property_getName


def structure_repr(s):
	if isinstance(s, ctypes.Structure):
		fieldvals = []
		flds=s._fields_
		for f in flds:
			a=getattr(s,f[0])
			fieldvals.append(structure_repr(a))
		return '({})'.format(','.join(fieldvals))
	else:
		return str(s)
		
		
def getProps(obj):
   cls=ObjCClass(obj._get_objc_classname())
   propCt=ctypes.c_uint(0)
   pA  = class_copyPropertyList(cls, byref(propCt))
   names=[]
   for i in range(propCt.value):
      nameptr=property_getName(pA[i])
      attribs=c.property_getAttributes(pA[i])
      name=(c.sel_getName(nameptr)).decode('ascii')
      sel_name=re.search(b',G([^,"]*)',attribs)
      if sel_name:
        sel_name=sel_name.group(1).decode('ascii')
        if obj.respondsToSelector_(sel(sel_name)):
           name=sel_name
      m=ObjCInstanceMethod(obj, name)
      if not m.sel_name==name:
         print(name,sel_name,m.sel_name,pA[i])
      #fix encoding: blocks cast as pure pointers
      m.encoding=re.match(b'^T([^,"\?]*)',attribs).group(1)+b'0@0:0'
      value='???'
      rc=None
      try:     
         if obj.respondsToSelector(m.sel_name):
            value_obj=m()
            value=structure_repr(value_obj)
      except:
         pass
      names.append((name,str(value),rc))
   return names
import ui
class ObjCPropertyDataSource(ui.ListDataSource):
	def __init__(self,obj):
		items=getProps(obj)
		ui.ListDataSource.__init__(self,items)
	def tableview_cell_for_row(self, tv, section, row):
		item = self.items[row]
		cell = ui.TableViewCell('subtitle')
		cell.text_label.number_of_lines = self.number_of_lines
		cell.text_label.text = item[0]
		cell.detail_text_label.text=item[1]+'retaincount:'+str(item[2])
		if self.text_color:
			cell.text_label.text_color = self.text_color
		if self.highlight_color:
			bg_view = View(background_color=self.highlight_color)
			cell.selected_background_view = bg_view
		if self.font:
			cell.text_label.font = self.font
		return cell
#n=getProps(ObjCInstance(UIApplication.sharedApplication()))

if __name__=='__main__':
	v=ui.View()
	V=ObjCInstance(v)
	p=getProps(V)
