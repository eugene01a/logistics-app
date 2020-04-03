from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty
from kivy.uix.gridlayout import GridLayout

def stack_widgets(*widgets):
    grid=GridLayout(cols=1)
    add_widgets(grid, tuple(widgets))

    return grid

def line_widgets(*widgets):
    grid = GridLayout(cols = len(widgets))
    add_widgets(grid, tuple(widgets))
    return grid

def add_widgets(parent, children):
    try:
        for child in children:
            parent.add_widget(child)
    except:
        print parent.id
        for child in children:
            print child.id


class ComboEdit(TextInput):
    options = ListProperty(('',))

    def __init__(self, **kw):
        ddn = self.drop_down = DropDown()
        ddn.bind(on_select=self.on_select)
        super(ComboEdit, self).__init__(**kw)

    def on_options(self, instance, value):
        ddn = self.drop_down
        ddn.clear_widgets()
        for widg in value:
            widg.bind(on_release=lambda btn: ddn.select(btn.text))
            ddn.add_widget(widg)

    def on_select(self, *args):
        self.text = args[1]

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.drop_down.open(self)
        return super(ComboEdit, self).on_touch_up(touch)


item_col = 0.75
del_col = 0.125
move_col = 0.125