import os

from evernote.edam.type.ttypes import Note
from evernote.edam.type.ttypes import NoteAttributes

real_mode = os.environ.get("ONLINE", "True")

if real_mode == "True":
    real_mode = True
else:
    real_mode = False
notes = [
    Note(contentHash='\xe8K\x8a\x89\x81\xb7\xe0\xba\x84L\x10wQ\xe5\x89e', updated=1519359983000, created=1519359983000,
         deleted=None, contentLength=103, title='test', notebookGuid='61d28712-302c-416a-8362-a8a1a5a31cdb',
         content='<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note><en-todo/>test<br/></en-note>',
         tagNames=None, updateSequenceNum=1311, tagGuids=['43bd1db1-9c67-42f2-ae9f-7932f8f89d5d'], active=True,
         attributes=NoteAttributes(lastEditorId=None, placeName='new', sourceURL=None, classifications=None,
                                   creatorId=None, author=None, reminderTime=None, altitude=None, reminderOrder=None,
                                   shareDate=None, reminderDoneTime=None, longitude=None, lastEditedBy=None,
                                   source=None,
                                   applicationData=None, sourceApplication='LogisticsApp', latitude=None,
                                   contentClass=None, subjectDate=None), guid='da4b312a-7486-4dab-833f-914c7653050e',
         resources=None),
    Note(contentHash='ynA\xf6s\xad\\\xc96q\x8f\x12\x9d\xc9\x93\x9a', updated=1519361101000, created=1519361101000,
         deleted=None, contentLength=102, title='new', notebookGuid='61d28712-302c-416a-8362-a8a1a5a31cdb',
         content='<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note><en-todo/>new<br/></en-note>',
         tagNames=None, updateSequenceNum=1317, tagGuids=['4db91364-493f-44d3-8e5d-6850dabe5fdf'], active=True,
         attributes=NoteAttributes(lastEditorId=None, placeName='new', sourceURL=None, classifications=None,
                                   creatorId=None, author=None, reminderTime=None, altitude=None, reminderOrder=None,
                                   shareDate=None, reminderDoneTime=None, longitude=None, lastEditedBy=None,
                                   source=None,
                                   applicationData=None, sourceApplication='LogisticsApp', latitude=None,
                                   contentClass=None, subjectDate=None), guid='22685b9a-d6fd-4430-b7bc-9f24b4dbbafe',
         resources=None)]

# offline data
place_notes = {'conditions': [],
               'categories': {
                   'buy': {'guid': "354e3b76-c78a-4f0f-bc1e-2f9115f09176",
                           'add_pointer': 'no add btn assigned yet',
                           'items':
                               {
                                   'item 1': {
                                       'location': '354e3b76-c78a-4f0f-bc1e-2f9115f09176',
                                       'delete': None},
                                   'item 2': {
                                       'location': '354e3b76-c78a-4f0f-bc1e-2f9115f09176',
                                       'delete': None}
                               }
                           },
                   'return': {'guid': '454e3b76-c78a-4f0f-bc1e-2f9115f09177',
                              'add_pointer': 'no add btn assigned yet',
                              'items':
                                  {
                                      'item 1': {
                                          'location': '354e3b76-c78a-4f0f-bc1e-2f9115f09176',
                                          'delete': None},
                                      'item 2': {
                                          'location': '354e3b76-c78a-4f0f-bc1e-2f9115f09176',
                                          'delete': None}
                                  }
                              },
               },
               'place': 'walmart'}

note_obj = Note()
note_obj.guid = 'offline_test_guid'

conditions = {'guid_tag': 'random_tag'}
places = ['walmart', 'Custom']
