# create floating list of views
import overlay
import ui,clipboard,dialogs, time
from objc_util import *
from FilePicker import TreeNode, TreeDialogController
import getobjcprops
from ast import literal_eval
import re


class ViewBrowserNode(TreeNode):
	def __init__(self, rootview, level=0):
		TreeNode.__init__(self)
		self.rootview = rootview
		self.level = level
		self.title,self.subtitle= self.get_node_descr()
		self.leaf = len(rootview.subviews())==0
		self.icon_name = 'FileOther' if self.leaf else 'Folder'
		#todo: icon represents class
	def get_node_descr(self):
		f=self.rootview.frame()
		return str(self.rootview._get_objc_classname()),'{}'.format((		f.origin.x,f.origin.y, f.size.width, f.size.height))
	def expand_children(self):
		s=self.rootview.subviews()
		#print(s)
		self.children = [ViewBrowserNode(sv,  self.level+1) for sv in s]
		self.expanded = True
@on_main_thread		
def prep():
	UIDebuggingInformationOverlay = ObjCClass('UIDebuggingInformationOverlay')
	UIDebuggingInformationOverlay.prepareDebuggingOverlay()
	return UIDebuggingInformationOverlay.overlay()



def showinfo(sender):
	row=picker.row_for_view(sender)
	entry = picker.flat_entries[row]
	b=entry.rootview
	try:
		text=b.ab_text()
	except AttributeError:
		text=''
	targets=[t for t in list(b.allTargets())]
	event=b.allControlEvents()
	actions=[]
	for t in targets:
		a=b.actionsForTarget_forControlEvent_(t,event)
		if a:
			for sel in a:
				actions.append('{} {}'.format(str(targets[0]._get_objc_classname()),sel))
	print(b.__repr__())
	print('text: ',text)
	for a in actions:
		print(actions)
	if b.gestureRecognizers():
		for g in b.gestureRecognizers():
			print(repr(g))
def show_objc_properties(sender):
	row=picker.row_for_view(sender)
	entry = picker.flat_entries[row]
	b=entry.rootview
	datasource=getobjcprops.ObjCPropertyDataSource(b)
	c = dialogs._ListDialogController(title=b.__repr__(), items=[], multiple=False, done_button_title='Done')
	c.view.data_source=datasource
	c.view.delegate=datasource
	datasource.action=properties_row_selected
	n.push_view(c.view)
def properties_row_selected( ds):
		selected_item = ds.items[ds.selected_row]
		print(selected_item)
		addr=re.match('<[^:]*: (0x[0-9a-fA-F]*)',selected_item[1])
		if addr:
			addr=addr.group(1)
			addr=literal_eval(addr)
			obj=ObjCInstance(addr)
			print(obj)
			datasource=getobjcprops.ObjCPropertyDataSource(obj)
			c = dialogs._ListDialogController(title=selected_item[0], items=[], multiple=False, done_button_title='Done')
			c.view.data_source=datasource
			c.view.delegate=datasource
			datasource.action=properties_row_selected
			n.push_view(c.view)

def tableview_cell_for_row(tv, section, row):
		self=picker
		entry = self.flat_entries[row]

		cell= old_cell_for_row(tv,section,row)
		if entry.rootview.isHidden():
			for s in cell.content_view.subviews:
				if issubclass(type(s),ui.Label):
					s.text_color='#bbb'
		info=ui.Button(frame=(cell.content_view.width-220,0,32,32),
		image=ui.Image.named('iob:ios7_information_outline_32'))
		info.flex='l'
		info.tint_color='blue'
		info.action = show_objc_properties
		cell.content_view.add_subview(info)
		try:
			ObjCInstanceMethod(entry.rootview,'allTargets')		
			info=ui.Button(frame=(cell.content_view.width-250,0,32,32),
				image=ui.Image.named('iob:link_32'))
			info.flex='l'
			info.action = showinfo
			cell.content_view.add_subview(info)
		except AttributeError:
			pass
		return(cell)
def tableview_accessory_button_tapped(sender):
	print('tapped')
@on_main_thread
def tableview_did_select(tv, section,row):
		#print(row)
		self=picker
		entry = self.flat_entries[row]
		
		sv=entry.rootview._focusItemsOverlayCreateIfNecessary_(True)
		if sv:
			sv.backgroundColor=UIColor.redColor()
			sv.alpha=0.2
			sv.hidden=False
		clipboard.set('ObjCInstance({})'.format(entry.rootview.ptr))

@on_main_thread
def tableview_did_deselect( tv, sectin,row):
		self=picker
		entry = self.flat_entries[row]
		entry.rootview._removeFocusItemOverlayViews()

		
if __name__=='__main__':
	v=ui.View(name='View Browser',frame=(0,0,320,576))
	n=ui.NavigationView(v,frame=v.bounds,name=v.name)
	root_node=ViewBrowserNode(overlay.AppWindows.root())	
	picker = TreeDialogController(root_node, async_mode=False)
	old_cell_for_row=picker.tableview_cell_for_row
	picker.tableview_did_deselect=tableview_did_deselect
	picker.tableview_did_select=tableview_did_select
	picker.tableview_cell_for_row=tableview_cell_for_row
	v.add_subview(picker.view)
	o=overlay.Overlay(content=n,parent=overlay.AppWindows.root())
	#o.recognizer_should_simultaneously_recognize=recognizer_should_simultaneously_recognize
	o.content_view.touch_enabled=True
	#o.content_view.bring_to_front()
	#picker.view.height=picker.view.height-20
	#v.height-=40
	#o.content_view.height-=20
	o.y-=20
	v.bg_color='red'
	o.x=30
	o.y=50
	picker.view.flex='wh'
	picker.view.height=v.height
	o.content_view.bg_color='blue'
	o.content_view.content_mode=0
	o.content_view.height-=20
	o.bg_color='white'
