try:
	from gi.repository import Gtk, Gdk, Wnck
	from gi.repository import PanelApplet
except: # Can't use ImportError, as gi.repository isn't quite that nice...
	import gtk as Gtk
	import gdk as GdK

import sys

def update_name(window, label, state):
	try:
		text = ''
		if (window == None):
			text = ''
		elif (window.has_name()):
			text = window.get_name()
		else:
			text = "No Name"

		if (not state.is_visible):
			state.text = text
		else:
			label.set_label(text)
	except Exception as e:
		label.set_label('Name: ' + str(e))

class State:
	__slots__ = ['prev_id', 'prev_xid', 'is_visible', 'text', 'click']

def window_changed(screen, prev_window, label, state):
	try:
		window = screen.get_active_window()

		if (prev_window != None and state.prev_id != None):
			prev_window.disconnect(state.prev_id)

		if (window != None):
			state.prev_id = window.connect("name-changed", update_name, label, state)
			state.prev_xid = window.get_xid()

		update_name(window, label, state)
	#	label.set_text(str(state.counter))
	#	state.counter += 1
		window = None
		screen = None
	except Exception as e:
		label.set_label('Changed: ' + str(e))

def window_closed(screen, window, label, state):
	try:
		if (window.get_xid() == state.prev_xid):
			label.set_label('')	
			state.prev_xid = None
		window = None
		screen = None
	except Exception as e:
		label.set_label('Closed: ' + str(e))

def workspace_changed(screen, prev_workspace, label, state):
	try:
		window = screen.get_active_window()
		if (window != None):
			workspace = window.get_workspace()
			cur_space = screen.get_active_workspace()
			if (workspace == None or cur_space == None or workspace.get_number() != cur_space.get_number()):
				label.set_label('')
				state.text = ''
			workspace = None
			cur_space = None
		else:
			label.set_label('')
			state.text = ''
		screen = None
		window = None
		prev_workspace = None
	except Exception as e:
		label.set_label('Workspace: ' + str(e))

def toggle_visibility(button, event, label, state):
	try:
		state.click = (state.click + 1) % 3

		if (state.click != 2 and not state.is_visible):
			state.is_visible = True
			label.set_label(state.text)

		if (state.click == 0):
			label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('light gray'))
		elif (state.click == 1):
			label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.Color.from_floats(0.5, 0.5, 0.5))
		else:
			state.is_visible = False
			state.text = label.get_label()
			label.set_label('')
	except Exception as e:
		label.set_label('Toggle: ' + str(e))


def applet_factory(applet, iid, data = None):
	# Create our label
	label = Gtk.Button('DEFAULT')

	try:
		# Get the screen
		screen = Wnck.Screen.get_default()
		screen.force_update()
		window = screen.get_active_window()

		# State object
		state = State()
		state.prev_id = None
		state.prev_xid = None
		state.is_visible = True
		state.text = ''
		state.click = 1

		update_name(window, label, state)
		#label.set_alignment(0.5, 0.5)
		#label.set_justify(Gtk.Justification.CENTER)
		label.connect("button-release-event", toggle_visibility, label, state)
		toggle_visibility(label, None, label, state)

		# Connect up some events
		screen.connect("active-window-changed", window_changed, label, state)
		screen.connect("window-closed", window_closed, label, state)
		screen.connect("active-workspace-changed", workspace_changed, label, state)

		screen = None
		window = None
	except Exception as e:
		label.set_label('Error occurred: ' + str(e))

	applet.add(label)
	applet.set_flags(PanelApplet.AppletFlags.EXPAND_MAJOR)
	applet.connect('destroy', Wnck.shutdown)
	applet.show_all()
	return True
