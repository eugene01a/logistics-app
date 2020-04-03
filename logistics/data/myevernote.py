import evernote.edam.notestore.ttypes as NoteStore
from evernote.api.client import EvernoteClient
from evernote.edam.limits.constants import EDAM_USER_NOTES_MAX
from time import sleep

from logistics.data import config
from logistics.data import offline
from logistics.data.read import *


class EvernoteSession():
    def __init__(self):
        if offline.real_mode is False:
            pass
        else:
            auth = config.load('auth')
            authToken = auth['evernote']['access_token']
            client = EvernoteClient(token=authToken)
            noteStore = client.get_note_store()
            self.authToken = authToken
            self.client = client
            self.noteStore = noteStore

    def sync_note(self, note):
        return self.noteStore.createNote(self.authToken, note)

    def create_note(self, items, place, category, tags=[]):
        conditions = tags
        newNote = create_new_note(items, place, category, conditions)
        return self.noteStore.createNote(self.authToken, newNote)

    def add_note_items(self, items, note_id):


        '''
        :param items: list of items
        :param category: category that contains the item
        :return: metadata of updated note
        '''

        checklist = ''

        # loop through each new item in list
        for item in items:
            # add item to note content as a checklist item
            checklist += '<div>' + enml_tags['unchecked_box'] + (item) + '</div>'

        # update content of note and sync
        noteData.content = write_note_body(checklist)
        return self.noteStore.updateNote(self.authToken, noteData)

    def find_note_ids(self, place, category='', conditions=[]):
        '''
        :return List of guids of matching notes
        '''

        # Create a search filter for notes with same place, conditions, and category
        note_filter = NoteStore.NoteFilter()
        if type(place) in [unicode, str] and type(category) in [unicode, str] and type(conditions) == list:
            placename = 'placeName:"{}"'.format(place)
            title = 'inTitle:{}'.format(category)
            tags = ''
            if len(conditions) > 0:
                tags = ' tag:"{}"'.format(conditions[0])
                if len(conditions) > 1:
                    for condition in conditions[1:]:
                        tags += ' tag:"{}"'.format(condition)
            else:
                # No conditions specified
                pass
        else:
            raise TypeError, "place and category must be string, and conditions must be list of strings"

        note_filter.words = placename + ' ' + title + tags

        resultspec = NoteStore.NotesMetadataResultSpec()
        resultspec.includeTitle = True
        resultspec.includeContent = True
        notes_metadata_list = self.noteStore.findNotesMetadata(self.authToken, note_filter, 0, EDAM_USER_NOTES_MAX,
                                                               resultspec)
        matching_note_guids = [note.guid for note in notes_metadata_list.notes]

        return matching_note_guids

    # main function
    def add_items(self, items, place, category, conditions=[]):
        '''
        Summary:
        adds a item to a note for the matching place and conditions. If no matching note is found, a new note is created.

        :param item: list of strings
        :param place: str, placeName attribute of the appropriate note
        :param category: str, the title of the new note, if necessary. (ex. Grocery, Return, To Do)
        :param conditions: list of tags describing additional conditions (ex. daytime, weekday, orange-county)
        :return: the note that the item was added to

        find a matching note
        if note exists
            add item to note
        else
            create a new note
        return note item was added to
        '''
        if offline.real_mode is False:
            return offline.note_obj

        # Check for existing notes with same place, category, and conditions
        matching_guids = self.find_note_ids(place, category, conditions=conditions)

        if len(matching_guids) > 0:
            # add items to first matching note in list
            item_note_metadata = self.add_note_items(items, matching_guids[0])
            return item_note_metadata
        else:
            # create new note with item
            item_note = self.create_note(items, place, category, tags=conditions)
            return item_note

    # main function
    def find_notes(self, place, conditions=[]):
        '''
        Summary:
        Gets all notes with the matching place and conditions

        :param place: str, placeName attribute of the appropriate note
        :param conditions: list of tags describing additional conditions (ex. daytime, weekday, orange-county)
        :return: list of un-formatted (from enml to dict) notes

        '''

        # find matching notes
        matching_notes = []
        if offline.real_mode is False:
            return offline.notes
        else:
            note_ids = self.find_note_ids(place, conditions=conditions)
            # get matching notes
            for note_id in note_ids:
                sleep(0.5)
                note = self.noteStore.getNote(self.authToken, note_id, True, False, False, False)
                matching_notes.append(note)
            return matching_notes

    def remove_items(self, items, note_guid=None):
        note_filter = NoteStore.NoteFilter()
        resultspec = NoteStore.NotesMetadataResultSpec()
        results = self.noteStore.findNotesMetadata(self.authToken, note_filter, 0, EDAM_USER_NOTES_MAX, resultspec)
        # find all notes with item, and remove the item
        if note_guid:
            sleep(0.5)
            note = self.noteStore.getNote(self.authToken, note_guid, True, False, False, False)
            updated_note = ttypes.Note()
            updated_content = note.content
            for item in items:
                updated_content = re.sub(enml_regex['todo_tag'] + re.escape(item), '', updated_content)
        updated_note.content = updated_content
        updated_note.title = note.title
        updated_note.guid = note.guid
        self.update_note(updated_note)

    def move_items(self, items, current_guid,
                   new_place=None,
                   new_category=None,
                   new_conditions=None):
        '''

        :param item:
        :param current_guid:
        :param new_item:
        :param new_place:
        :param new_category:
        :param new_conditions:
        :return:
        '''
        note = self.noteStore.getNote(self.authToken, current_guid, True, False, False, False)
        current_tags = self.noteStore.getNoteTagNames(self.authToken, current_guid)

        # remove items from current note
        updated_note = ttypes.Note()
        updated_note.title = note.title
        updated_note.guid = note.guid
        updated_note.content = note.content
        for item in items:
            updated_note.content = re.sub(enml_regex['todo_tag'] + item, '', updated_note.content)

        self.updateNote(updated_note)

        # add item with new criteria
        self.add_items(items,
                       new_place if new_place else note.attributes.placeName,
                       new_category if new_category else note.title,
                       conditions=new_conditions if new_conditions else current_tags)

    def retrieve_titles(self):
        note_filter = NoteStore.NoteFilter()
        note_filter.words = 'intitle:*'
        resultspec = NoteStore.NotesMetadataResultSpec()
        resultspec.includeTitle = "True"
        results = self.noteStore.findNotesMetadata(self.authToken, note_filter, 0, EDAM_USER_NOTES_MAX, resultspec)
        titles = []
        for note in results.notes:
            titles.append(note.title)
            print note.title
        unique_places = list(set(titles))
        return unique_places

    def retrieve_placenames(self):
        if offline.real_mode is False:
            return offline.places
        else:
            note_filter = NoteStore.NoteFilter()
            note_filter.words = 'placename:*'
            resultspec = NoteStore.NotesMetadataResultSpec()
            resultspec.includeAttributes = "True"
            results = self.noteStore.findNotesMetadata(self.authToken, note_filter, 0, EDAM_USER_NOTES_MAX, resultspec)
            placenames = []
            for note in results.notes:
                placenames.append(note.attributes.placeName)
            unique_places = list(set(placenames))
            return unique_places

    def retrieve_tags(self):
        # gets list of all tags that do not have the tag "Removed" as its parent tag
        if offline.real_mode is False:
            return offline.conditions
        else:
            tags = self.noteStore.listTags(self.authToken)
            active_tags = list(tags)
            for tag in tags:
                if tag.name == 'Remove':
                    removed_guid = tag.guid
                    for tag in tags:
                        if tag.parentGuid == removed_guid:
                            active_tags.remove(tag)
                            break
                    break
            return create_tag_guid_lookup(active_tags)

    def update_note(self, updated_note):
        checklist = read_note_checklist(updated_note)
        if len(checklist) == 0:
            print "removing note {}".format(updated_note.guid)
            return self.noteStore.deleteNote(self.authToken, updated_note.guid)
        else:
            return self.noteStore.updateNote(self.authToken, updated_note)
