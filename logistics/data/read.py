import re

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from evernote.edam.type import ttypes


class Item:
    '''
    container for category items
    '''

    def __init__(self, name, guid, delete):
        self.value = name
        self.guid = guid
        self.delete = delete


class Category:
    '''
    Category instance will contain list of Item instances
    '''

    def __init__(self, note):
        self.guid = note.guid
        self.place = note.attributes.placeName
        self.conditions = note.tagNames
        self.title = note.title
        self.items = {}
        self.populate_items(note)

    def populate_items(self, note):
        '''
        Assigns a list of items from the note to self.items
        :param note:
        '''
        item_names = read_note_checklist(note)
        for item_name in item_names:
            self.add_item(item_name)

    def add_item(self, item_name):
        '''
        Appends a new Item instance to self.items attribute
        :param item_name:
        '''
        new_item = Item(item_name, self.guid, False)
        self.items[item_name] = new_item

    def write_content(self):
        '''
        Returns ENML content string reflecting the current items in the category
        '''
        current_items = []
        for item, item_obj in self.items.items():
            # if item is marked as deleted, dont add it to the note content, otherwise, add
            if item_obj.delete is False:
                current_items.append(item_obj.value)

        checklist = write_note_checklist(current_items)
        content = write_note_body(checklist)
        return content

    def generate_note(self):
        '''
        returns a note object with current values
        '''
        note = ttypes.Note()
        note.title = self.title
        note.guid = self.guid
        attributes = ttypes.NoteAttributes()
        attributes.placeName = self.place
        attributes.sourceApplication = 'LogisticsApp'
        note.attributes = attributes
        note.tagNames = self.conditions
        note.content = self.write_content()
        return note


class Results:
    # Results object will contain list of Category instances, and place and conditions attributes
    def __init__(self, place, conditions, notes):
        '''
        :param place:
        :param conditions:
        :param notes: list of evernote note objects
        '''
        self.place = place
        self.conditions = conditions
        self.notes = notes
        self.categories = {}
        self.populate_categories()

    def populate_categories(self):
        '''
        :param notes: dict of note objects returned from evernote api
        :return:
        '''
        for note in self.notes:
            self.categories[note.title] = Category(note)

    def add_new_category(self, items, place, category, conditions):
        '''
        Adds a new category to results with new items
        :param category_name: string
        :param items:  list of items
        :return:
        '''
        new_note = create_new_note(items, place, category, conditions)

        self.categories[category] = Category(new_note)


enml_regex = {
    'checked_item': '''<en-todo\s+[^>]*checked\s*=\s*['|\"]true['|\"][^>]*\/\s*>{}(?=<[^>]*en|$)''',
    # checked checkbox item (tag and text), MUST SPECIFY ITEM
    'all_checked_items': r'''<en-todo\s+[^>]*checked\s*=\s*['|\"]true['|\"][^>]*\/\s*>.+?(?=<[^>]*en|$)''',
    # All checked checkbox items (tag and text)
    'unchecked_box': r'<en-todo\s+\/\s*>',  # all checkbox tag that is not checked
    'todo_tag': r'<en-todo\s*[^>]*\s*[^>]*\/\s*>'  # all checkbox tags (checked and unchecked)
}


def read_note_checklist(note):
    '''
    :param note_content: content from note object
    :return: list of items in checklist
    '''
    # extract contents of en-note tag
    enml_content = note.content
    note_body = re.search(r'(?<=<en-note>)(.*)(?=<\/en-note>)', enml_content).group(0)

    # trim all div and br tags
    note_body = re.sub(r'<[^<]*div[^>]*>', '', note_body)
    note_body = re.sub(r'<\/*br.*?>', '', note_body)

    # use BeautifulSoup to parse note body as html
    soup = BeautifulSoup(note_body, 'html.parser')
    soup_contents = soup.contents

    # find all checkbox tags and assign appropriate text to each one
    todo_tags = soup.find_all('en-todo')
    original_soup_contents = soup_contents
    for i, content in enumerate(original_soup_contents):
        # if current item is a Tag and the next item is a NavigableString, add the next item to the current item as its text
        if i < len(soup_contents) - 1:
            next_content = soup_contents[i + 1]
            if type(next_content) is NavigableString and content in todo_tags:
                content.insert(0, next_content)

    # create list of items
    items = list()
    for tag in soup_contents:
        if str(tag.name) == 'en-todo':
            if tag.text:
                items.append(tag.text)

    # return the list of items
    return items


def create_tag_guid_lookup(tags):
    '''
    creates a lookup table for looking up tags by their guids
    :param tags: response of NoteStore.listTags, which returns a list of all active tags in an account
    :return: dictionary with tag guids as keys and tag names as values
    '''
    formatted_tags = dict()
    for tag in tags:
        formatted_tags[tag.guid] = tag.name
    return formatted_tags


enml_tags = {
    'header': '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">',
    'start': '<en-note>',
    'end': '</en-note>',
    'checked_box': '<en-todo checked="true"/>',
    'unchecked_box': '<en-todo/>'
}


def write_note_checklist(items):
    '''
    Creates a checklist in ENML from a list of strings
    :param items:
    :return:
        ENML string containing the checklist of items
    '''
    checklist_body = ''
    for item in items:
        checkbox_item = '{}{}<br/>'.format(enml_tags['unchecked_box'], item)
        checklist_body += checkbox_item
    return checklist_body


def write_note_body(body):
    '''
    formats the body of an evernote note
    :param noteBody:
    :return:
    '''

    nBody = enml_tags['header'] + enml_tags['start'] + body + enml_tags['end']
    return nBody


def create_new_note(items, place, category, conditions):
    '''
    Returns note object given items, place, category, conditions
    :param items:
    :param place:
    :param category:
    :param conditions: list
    :return:
    '''

    new_note = ttypes.Note()
    new_note.guid = None
    new_note.title = category
    newAttributes = ttypes.NoteAttributes()
    newAttributes.placeName = place
    newAttributes.sourceApplication = 'LogisticsApp'
    if conditions:
        new_note.tagNames = conditions
    noteBody = write_note_checklist(items)
    new_note.content = write_note_body(noteBody)
    new_note.attributes = newAttributes
    return new_note
