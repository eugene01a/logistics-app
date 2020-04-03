from functools import partial

from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from logistics.data.read import Item, create_new_note
from logistics.data.read import Results
from logistics.gui.layout import add_widgets, line_widgets, stack_widgets

default_condition = 'Conditions'
no_place_selected_text = 'Place'
custom_text = 'Custom'


class Callbacks():
    def __init__(self):
        self.add_item_popup = Popup(title='Add new item')
        self.add_place_popup = Popup(title='Add new place', size_hint = (0.75, 0.75))
        self.condition_select_popup = Popup(title='Select conditions', size_hint = (0.75, 0.75))
        self.edit_item_popup = Popup(title='Edit item', size_hint = (0.75, 0.75))
        self.confirm_popup = Popup(title="Confirm action", size_hint = (0.5, 0.25))
        self.saved_popup = Popup(title="Save successful", size_hint = (0.5, 0.25))

    def search_callback(self, parent):
        place = self.place_spinner.text
        conditions = []
        for condition in self.conditions_btn.text.split(', '):
            if condition in self.conditions.values():
                conditions.append(condition)
        notes = self.session.find_notes(place, conditions=conditions)
        self.results = Results(place, conditions, notes)
        # remove previous results grid if any exist

        self.results_panel_fill()

        # disable searbutton and enable save and reset buttons
        for disable in [self.search_btn, self.conditions_btn, self.place_spinner]:
            disable.disabled = True
        for enable in [self.save_btn, self.reset_btn]:
            enable.disabled = False

    def add_new_cat_item_callback(self, btn, input=None, category=None):
        items = input.text.split(",")
        for item in items:
            item_obj = Item(item, None, False)
            self.results.categories[category].items[item] = item_obj
        self.results_panel_fill()

    def add_item_btn_callback(self, btn, category=None):
        def set_selection_text(btn, default_txt, blank_txt):
            if btn.text == default_txt:
                return blank_txt
            else:
                return btn.text

        def popup_add_btn_callback(btn, category=None):
            items = item_value.text.split(",")
            place = place_value.text
            conditions = conditions_value.text.split(',')
            ''
            if category is None:
                category = str(category_value.text)

            new_note = create_new_note(items, place, category, conditions)
            self.results = Results(place, conditions, [new_note])
            self.results_panel_fill()
            self.add_item_popup.dismiss()
            self.save_btn.disabled = False
            self.reset_btn.disabled = False

        content = GridLayout(cols=1)
        place_grid = GridLayout(cols=2)
        place_value = TextInput(text=self.place_spinner.text)
        place_label = Label(text="Place".format(size_hint_x=0.25))
        add_widgets(place_grid, (place_label, place_value))

        conditions_selection = set_selection_text(self.conditions_btn, 'Conditions',
                                                  'Seperate multiple conditions with commas')
        conditions_grid = GridLayout(cols=2)

        if self.conditions_btn.text == default_condition:
            conditions_value = TextInput(hint_text=conditions_selection)
        else:
            conditions_value = TextInput(text=self.conditions_btn.text)

        conditions_label = Label(text="Conditions".format(size_hint_x=0.25))
        add_widgets(conditions_grid, (conditions_label, conditions_value))

        category_grid = GridLayout(cols=2)
        category_label = Label(text="Category".format(size_hint_x=0.25))
        if category:
            category_value = TextInput(text=category, disabled=True)
        else:
            category_value = TextInput(hint_text="Enter a Category")
        add_widgets(category_grid, (category_label, category_value))

        item_grid = GridLayout(cols=2)
        item_value = TextInput(hint_text="'Seperate multiple items with commas'")
        item_label = Label(text="Item(s)".format(size_hint_x=0.25))
        add_widgets(item_grid, (item_label, item_value))

        add_btn = Button(text="Add", on_press=partial(popup_add_btn_callback, category=category))

        add_widgets(content, (place_grid, conditions_grid, category_grid, item_grid, add_btn))

        self.add_item_popup.content = content
        self.add_item_popup.open()

    def save_callback(self, btn):

        def save_changes(btn):
            # Saves changes made to self.results
            self.confirm_popup.dismiss()
            for _, category in self.results.categories.items():

                note = category.generate_note()
                if note.guid is None:
                    self.session.sync_note(note)
                else:
                    self.session.update_note(note)
            # Once all changes have been saved, open the saved dialog
            create_saved_dialog()
            self.saved_popup.open()

        def create_confirm_popup():
            # creates a popup window that asks user to press yes button to proceed with saving changes.
            yes_btn = Button(text='Yes', on_press=save_changes)
            no_btn = Button(text='No', on_press=lambda btn: self.confirm_popup.dismiss())
            confirm_msg = Label(text="Are you sure?")

            action_btns = line_widgets(yes_btn, no_btn)
            self.confirm_popup.content = stack_widgets(confirm_msg, action_btns)

        def create_saved_dialog():
            def reset(btn):
                self.saved_popup.dismiss()
                self.reset_callback(self.reset_btn)

            saved_msg = Label(text='Changes saved. Reset?')
            yes_btn = Button(text='Yes', on_press=reset)
            no_btn = Button(text='No', on_press=lambda btn: self.saved_popup.dismiss())
            action_btns = line_widgets(yes_btn, no_btn)
            self.saved_popup.content = stack_widgets(saved_msg, action_btns)

        # create and open confirmation popup window
        create_confirm_popup()
        self.confirm_popup.open()

    def reset_callback(self, reset_btn):
        self.place_spinner.values = self.session.retrieve_placenames()
        self.place_spinner.text = ''
        self.conditions_btn.text = default_condition
        self.results_panel.clear_tabs()
        self.results_grid.clear_widgets()
        for btn in (reset_btn, self.search_btn, self.add_item_btn, self.save_btn):
            btn.disabled = True
        for enable in [self.search_btn, self.conditions_btn, self.place_spinner]:
            enable.disabled = False

    def place_select_callback(self, *args):
        spinner = args[0]
        print args

        # if user selects a new place, the add button is enabled.
        def add_place_callback(btn):
            spinner.text = new_place.text
            self.add_place_popup.dismiss()


        if spinner.text == custom_text:
            # Search btn disabled since there wont be any results for new place
            self.add_item_btn.disabled = False
            self.search_btn.disabled = True

            content = GridLayout(cols=1)
            new_place = TextInput()
            add_btn = Button(text="Add", on_press=add_place_callback)
            add_widgets(content, (new_place, add_btn))
            self.add_place_popup.content = content
            self.add_place_popup.open()
        elif spinner.text in self.places:
            # if an existing place is selected, enable to search button so user can search for existing placenotes
            self.search_btn.disabled = False
            self.add_item_btn.disabled = True

    def conditions_popup_callback(self, btn):
        # get currently checked conditions from btn text
        checked_conditions = btn.text.split(',')

        print "Reading checked_conditions from btn text: {}".format(str(checked_conditions))

        # remove default condition from checked conditions, if it exists
        if default_condition in checked_conditions:
            print "removing '{}' from current conditions".format(default_condition)
            checked_conditions.remove(default_condition)

        content = GridLayout(cols=1)

        # copy checked_conditions to keep track of any new conditions not synced to account
        new_conditions = list(checked_conditions)

        def checkbox_callback(chkbx, value):
            if value is True:
                checked_conditions.append(chkbx.id)
            else:
                checked_conditions.remove(chkbx.id)

        # Loop through all conditions
        for guid, condition in self.conditions.items():
            # if condition is in the btn text, create a checked checkbox, otherwise create unchecked checkbox.
            # Set id of checkbox to name of condition to be able to identify the value in callback
            condition_row = GridLayout(cols=2)

            if condition in checked_conditions:
                is_active = True
                # remove condition from new_conditions if it is checked and already synced to account
                new_conditions.remove(condition)
            else:
                is_active = False

            condition_checkbox = CheckBox(size_hint_x=0.1, active=is_active, id=condition)

            # remove or add the condition from checked_conditions when its status changes


            condition_checkbox.bind(active=checkbox_callback)

            # add the checkbox and condition label to the content of the popup
            add_widgets(condition_row, (condition_checkbox, Label(text=condition)))
            add_widgets(content, (condition_row,))

        # add a textfield for any conditions not yet synced to the account
        new_conditions_textbox = TextInput(focus=False,
                                           hint_text='Seperate multiple conditions with commas')

        # If new conditions exist, add them in the text field seperated by commas
        if new_conditions != []:
            new_conditions_textbox.text = ','.join(new_conditions)

        def save_callback(btn):
            print "Save button pressed"
            # add conditions in textbox to checked_conditions if it doesnt exist already
            if new_conditions_textbox.text:
                textbox_conditions = new_conditions_textbox.text.split(',')
                for textbox_condition in textbox_conditions:
                    if textbox_condition not in checked_conditions:
                        checked_conditions.append(textbox_condition)
            else:
                for condition in new_conditions:
                    checked_conditions.remove(condition)

            # if checked conditions exist set them to btn text, otherwise set btn text to default condition
            if checked_conditions:
                print "Detected checked conditions: {}".format(str(checked_conditions))
                self.conditions_btn.text = ','.join(checked_conditions)

            else:
                self.conditions_btn.text = default_condition

            self.condition_select_popup.dismiss()

        save_btn = Button(text="Save", on_press=save_callback)

        add_widgets(content, (new_conditions_textbox, save_btn))

        self.condition_select_popup.content = content
        self.condition_select_popup.open()

    def delete_item_callback(self, btn, item, category):
        if btn.state == 'down':
            self.results.categories[category].items[item].delete = True
        else:
            self.results.categories[category].items[item].delete = False

    def edit_item_callback(self, item_label, category, item):
        def save_callback(btn, field=None):
            self.results.categories[category].items[item].value = value_field.text
            item_label.text = value_field.text
            self.edit_item_popup.dismiss()

        popup_content = GridLayout(cols=1)
        value_field = TextInput(text=item_label.text)

        save_btn = Button(text="Save", on_press=partial(save_callback, field=value_field))
        add_widgets(popup_content, (self.place_spinner, save_btn))
        self.edit_item_popup.content = popup_content
        self.edit_item_popup.open()