from kivy.config import Config

Config.set('graphics', 'width', '375')
Config.set('graphics', 'height', '667')
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from functools import partial
from kivy.app import App
from logistics.gui.callbacks import Callbacks
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from logistics.data.myevernote import EvernoteSession
from logistics.gui.layout import add_widgets, item_col, del_col, move_col
from logistics.data.read import Results
from logistics.gui.layout import ComboEdit


class MainApp(App, Callbacks, Results):
    def __init__(self):
        Callbacks.__init__(self)
        App.__init__(self)
        self.session = EvernoteSession()
        self.places = []
        self.conditions = {}
        self.results = None
        self.root = BoxLayout(orientation='vertical', spacing=10)
        self.place_spinner = ComboEdit(hint_text='Specify place')
        self.conditions_btn = Button(text='Conditions', id='conditions')
        self.search_btn = Button(text='Search!')
        self.add_item_btn = Button(text='Add Item', on_press=self.add_item_btn_callback, disabled=False)
        self.header_grid = GridLayout(cols=2, size_hint=(1, 0.05))
        self.results_panel = None
        self.results_scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.55))
        self.results_grid = GridLayout(cols=1)
        self.save_btn = Button(text='Save', on_press=self.save_callback, disabled=True)
        self.reset_btn = Button(text='Reset', on_press=self.reset_callback, disabled=True)
        Window.softinput_mode = 'below_target'

    def spinner_box_fill(self):
        spinner_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        self.places = self.session.retrieve_placenames()
        self.place_spinner.bind(focus=self.place_select_callback)

        # add place selection spinner to search box
        self.place_spinner.options = [Button(text=place, size_hint_y=None) for place in self.places]
        self.conditions = self.session.retrieve_tags()

        self.conditions_btn.bind(
            on_press=self.conditions_popup_callback)

        add_widgets(spinner_box, (self.place_spinner, self.conditions_btn))
        # Add to root
        self.root.add_widget(spinner_box)

    def action_grid_fill(self):
        # add search button to search box
        action_grid = GridLayout(cols=2, size_hint=(1, 0.1))
        self.search_btn.bind(on_press=self.search_callback)
        # add buttons to search box
        add_widgets(action_grid, (self.search_btn, self.add_item_btn))
        # Add to root
        self.root.add_widget(action_grid)

    def refresh_grid_fill(self):
        refresh_grid = GridLayout(cols=2, size_hint=(1, 0.1))
        add_widgets(refresh_grid, (self.save_btn, self.reset_btn))
        # Add to root
        self.root.add_widget(refresh_grid)

    def _build(self):

        self.spinner_box_fill()
        self.action_grid_fill()
        self.root.add_widget(self.results_grid)
        self.refresh_grid_fill()

    def build(self):

        self.spinner_box_fill()
        self.action_grid_fill()
        self.root.add_widget(self.results_grid)
        self.refresh_grid_fill()

    def results_panel_fill(self):
        # remove previous results from results grid
        self.results_grid.clear_widgets()
        self.results_panel = TabbedPanel(do_default_tab=False)

        # loop through categories in current results
        for category in self.results.categories.keys():

            category_tab = TabbedPanelHeader(text=category)

            # add grid to a scrollview widget
            items_scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height * 0.55))

            # create grid that is scrollable
            items_grid = GridLayout(cols=3, size_hint=(1, None), size=(Window.width, Window.height * 0.55))
            items_grid.bind(minimum_height=items_grid.setter('height'))

            new_items_field = TextInput(hint_text="'Seperate multiple items with commas'")
            add_item_btn = Button(text='Add\nitems', size_hint=(del_col, None),
                                  on_press=partial(self.add_new_cat_item_callback, input=new_items_field,
                                                   category=category))
            add_widgets(items_grid, (new_items_field, add_item_btn))

            # disable add new item button on search box when add item btn in results box is added
            # self.add_item_btn.disabled = True

            # loop through items in category

            items = self.results.categories[category].items.items()
            for (item_name, item_obj) in items:
                # create item label, edit button, and del button
                delete_btn = ToggleButton(text="X", size_hint=(del_col, None),
                                          on_press=partial(self.delete_item_callback,
                                                           item=item_name,
                                                           category=category))

                edit_btn = Button(text=item_name, size_hint=(item_col, None),
                                  on_press=partial(self.edit_item_callback, category=category, item=item_name))

                edit_btn.text_size=edit_btn.size

                # edit_btn.text_size = edit_btn.size
                add_widgets(items_grid, (edit_btn, delete_btn))
            # create a textbox for adding new items'

            items_scrollview.add_widget(items_grid)

            category_tab.content = items_scrollview
            self.results_panel.add_widget(category_tab)

        # add panel to results grid
        self.results_grid.add_widget(self.results_panel)

try:
    if __name__ == '__main__':
        MainApp().run()

except:
