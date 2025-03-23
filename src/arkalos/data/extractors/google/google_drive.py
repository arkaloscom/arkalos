
# Useful Resources:
# https://developers.google.com/drive/api/reference/rest/v3/files
# https://developers.google.com/drive/api/guides/ref-export-formats

import os
import io
import csv
from functools import partial
from typing import TYPE_CHECKING

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from arkalos.core.path import drive_path
from arkalos.utils.mime_types import MimeType
from arkalos.utils.dict_utils import filter_by_col, add_count_col
from arkalos.utils.file_utils import escape_filename
from arkalos.services.google_service import GoogleService

if TYPE_CHECKING:
    from arkalos.services.google_stubs.drive.v3 import DriveResource
    from arkalos.services.google_stubs.sheets.v4 import SheetsResource
    from arkalos.services.google_stubs.forms.v1 import FormsResource



class GoogleDriveQuery:

    query: list[str]

    def __init__(self):
        self.query = []

    def name(self, name: str | list[str]) -> 'GoogleDriveQuery':
        if isinstance(name, list):
            name_queries = ' or '.join([f"name contains '{n}'" for n in name])
            self.query.append(f'({name_queries})')
        else:
            self.query.append(f"name contains '{name}'")
        return self

    def folder(self, folder: str) -> 'GoogleDriveQuery':
        self.query.append(f"'{folder}' in parents")
        return self

    def type(self, mime_type: str | list[str]) -> 'GoogleDriveQuery':
        if isinstance(mime_type, list):
            mime_queries = ' or '.join([f"mimeType = '{mt}'" for mt in mime_type])
            self.query.append(f'({mime_queries})')
        else:
            self.query.append(f"mimeType = '{mime_type}'")
        return self

    def build(self) -> str:
        return ' and '.join(self.query)



class GoogleFormParser:

    TYPE_SECTION = 'SECTION'
    TYPE_TEXT = 'TEXT'
    TYPE_QUESTION = 'QUESTION'

    QTYPE_TEXT_LONG = 'TEXT_LONG'
    QTYPE_TEXT = 'TEXT'
    QTYPE_CHOICE_RADIO = 'RADIO'
    QTYPE_CHOICE_CHECKBOX = 'CHECKBOX'
    QTYPE_CHOICE_DROPDOWN = 'DROPDOWN'
    QTYPE_SCALE = 'SCALE'

    @staticmethod
    def getItemType(item):
        if 'pageBreakItem' in item:
            return GoogleFormParser.TYPE_SECTION
        elif 'textItem' in item:
            return GoogleFormParser.TYPE_TEXT
        elif 'questionItem' in item:
            return GoogleFormParser.TYPE_QUESTION
        raise Exception('Unsupported form item type')

    @staticmethod
    def getQuestionType(item):
        if 'textQuestion' in item['questionItem']['question']:
            if 'paragraph' in item['questionItem']['question']['textQuestion']:
                return GoogleFormParser.QTYPE_TEXT_LONG
            return GoogleFormParser.QTYPE_TEXT
        elif 'choiceQuestion' in item['questionItem']['question']:
            type = item['questionItem']['question']['choiceQuestion']['type']
            if type == 'RADIO':
                return GoogleFormParser.QTYPE_CHOICE_RADIO
            elif type == 'CHECKBOX':
                return GoogleFormParser.QTYPE_CHOICE_CHECKBOX
            elif type == 'DROP_DOWN':
                return GoogleFormParser.QTYPE_CHOICE_DROPDOWN
        elif 'scaleQuestion' in item['questionItem']['question']:
            return GoogleFormParser.QTYPE_SCALE 
        # print(item)
        raise Exception('Unsupported form item question type')

    @staticmethod
    def parse(form_data):
        form = form_data
        form_meta = {
            'id': form['formId'],
            'file_name': form['info']['documentTitle'],
            'title': form['info']['title'],
            'description': form['info']['description'],
            'collecting_emails': 'emailCollectionType' in form['settings'],
            'responder_url': form['responderUri'],
            'form_url': 'https://docs.google.com/forms/d/' + form['formId'],
            'linked_sheet_url': 'https://docs.google.com/spreadsheets/d/' + form['linkedSheetId'] if 'linkedSheetId' in form else None,
            'linked_sheet_id': form['linkedSheetId'] if 'linkedSheetId' in form else None,
            'items': []
        }

        for item in form['items']:
            type = GoogleFormParser.getItemType(item)
            qtype = None
            question_id = None
            required = None
            options = None
            options_other = None
            scale = None
            if type == GoogleFormParser.TYPE_QUESTION:
                if 'required' in item['questionItem']['question']:
                    required = True
                else:
                    required = False
                question_id = item['questionItem']['question']['questionId']
                qtype = GoogleFormParser.getQuestionType(item)
                if qtype in [
                    GoogleFormParser.QTYPE_CHOICE_CHECKBOX, 
                    GoogleFormParser.QTYPE_CHOICE_DROPDOWN, 
                    GoogleFormParser.QTYPE_CHOICE_RADIO
                ]:
                    options_other = False
                    options = []
                    opts = item['questionItem']['question']['choiceQuestion']['options']
                    for opt in opts:
                        if 'value' in opt:
                            options.append(opt['value'])
                        elif 'isOther' in opt:
                            options_other = opt['isOther']
                elif qtype == GoogleFormParser.QTYPE_SCALE:
                    scale = item['questionItem']['question']['scaleQuestion']

            item_meta = {
                'id': item['itemId'],
                'title': item['title'],
                'type': type,
                'question_type': qtype,
                'question_id': question_id,
                'required': required,
                'options': options,
                'options_other': options_other,
                'scale': scale,
            }
            form_meta['items'].append(item_meta)

        return form_meta
    
    @staticmethod
    def parseResponses(form_responses, questions_meta) -> list[dict]:
        if 'responses' not in form_responses:
            return []

        responses = form_responses
        questions = questions_meta

        question_map = {}
        for question in questions:
            question_map[question['question_id']] = (question['title'], question['question_type'])

        items = []

        for response in responses['responses']:
            item = {
                '_id': response['responseId'],
                '_timestamp': response['createTime'],
                '_email': response['respondentEmail'] or None,
            }
            for question_id in question_map:
                question_title = question_map[question_id][0]
                item[question_title] = None
            for question_id in response['answers']:
                if question_id in question_map: # ignore old deleted questions that were answered
                    question_title = question_map[question_id][0]
                    question_type = question_map[question_id][1]
                    answers = response['answers'][question_id]['textAnswers']['answers']
                    if question_type == 'CHECKBOX':
                        answs = []
                        for answ in answers:
                            answs.append(answ['value'])
                        item[question_title] = answs
                    else:
                        item[question_title] = answers[0]['value']

            items.append(item)

        return items



class GoogleDrive:

    service: GoogleService
    drive: 'DriveResource'
    sheets: 'SheetsResource'
    forms: 'FormsResource'



    def __init__(self, service: GoogleService):
        self.service = service
        self.drive = self.service.drive()
        self.sheets = self.service.sheets()
        self.forms = self.service.forms()



    def _executeFilesListQuery(self, query: GoogleDriveQuery, fields: str|None = None) -> list:
        '''Helper method to execute a files list query with pagination.'''
        all_files: list = []
        page_token: str|None = None
        if fields is None:
            fields = 'files(id, name, mimeType, size, createdTime, modifiedTime, owners, parents, webViewLink, webContentLink)'
        
        while True:
            results = self.drive.files().list(
                q=query.build(),
                fields=f'nextPageToken, {fields}',
                pageToken=page_token).execute()
                
            all_files.extend(results.get('files', []))
            page_token = results.get('nextPageToken')
            
            if not page_token:
                break
                
        return all_files
    


    def getFolderPath(self, folder_id: str, is_file: bool = False) -> str:
        '''Get the full path of a folder by ID.'''
        if folder_id == 'root':
            return ''
            
        path_parts: list = []
        current_id: str|None = folder_id
        
        while current_id and current_id != 'root':
            file = self.drive.files().get(
                fileId=current_id, 
                fields='name,parents').execute()
                
            path_parts.insert(0, file.get('name'))
            
            if 'parents' in file and file['parents']:
                current_id = file['parents'][0]
            else:
                current_id = None

        if is_file:
            path_parts = path_parts[:-1]
                
        return '/' + '/'.join(path_parts)



    def _buildItemMetaDict(self, file, folder_path, folder_id = None):
        if folder_id is None:
            folder_id = file.get('parents')[0]
        size = file.get('size')
        owner = None
        for owner_obj in file.get('owners', []):
            owner = owner_obj.get('displayName')

        fname= escape_filename(file.get('name'))
        item = {
            'id': file.get('id'),
            'name': fname,
            'folder': f'{folder_path}',
            'path': f'{folder_path}/{fname}',
            'type': 'folder' if file.get('mimeType') == MimeType.FOLDER_GOOGLE else 'file',
            'mime_type': file.get('mimeType'),
            'extension': MimeType.getExtFromMimeType(file.get('mimeType')),
            'size': int(size) if size is not None else None,
            'created_time': file.get('createdTime'),
            'modified_time': file.get('modifiedTime'),
            'owner': owner,
            'parent_id': folder_id if folder_id is not None else file.get('parents')[0],
            'folder_url': 'https://drive.google.com/drive/folders/' + folder_id,
            'file_url': file.get('webViewLink'),
            'download_url': file.get('webContentLink')
        }
        return item


    def getFileMetadata(self, file_id: str):
        file = self.drive.files().get(
            fileId=file_id, 
            fields='id, name, mimeType, size, createdTime, modifiedTime, owners, parents, webViewLink, webContentLink'
        ).execute()
        folder_path: str = self.getFolderPath(file_id, True)
        item = self._buildItemMetaDict(file, folder_path)
        return item


    def listFiles(self, 
        folder_id: str, 
        name_pattern: str|None = None,
        file_types: list|None = None,
        recursive_depth: int = 0,
        do_print: bool = False
    ):
        '''
        List files and folders in a Google Drive folder with structured metadata.
        
        Args:
            folder_id (str): The ID of the folder to search in

            name_pattern (str): Optional regex pattern to filter results by name.
            
            file_types (list): Optional list of MIME types to filter results
            
            recursive_depth (int): 0 for no recursion, -1 for unlimited recursion, 
                positive int for specific depth (e.g., 1 for one level)
            
        Returns:
            list: List of dictionaries with structured file/folder metadata
        '''
        items: list = []
        file_types = file_types or []
        folder_path: str = self.getFolderPath(folder_id)

        query = GoogleDriveQuery().folder(folder_id)
        if recursive_depth != 0:
            # Always include google folder if reading the directory recursively 
            file_types.append(MimeType.FOLDER_GOOGLE)
        if file_types:
            query.type(file_types)
        # if name_pattern:
        #     query.name(name_pattern)
        # WARNING: Google doesn't have money to hire designers. It searches only 
        # for words that start with name_pattern, you can't search inside of words!
        # Filter results manually instead after fetching all the data

        if do_print:
            print('Reading: ' + folder_path)
            
        # Execute query
        files = self._executeFilesListQuery(query)
        
        # Process results
        for file in files:
            item = self._buildItemMetaDict(file, folder_path, folder_id)
            items.append(item)
            
            # Handle recursion based on recursive_depth value
            if file.get('mimeType') == MimeType.FOLDER_GOOGLE:
                list_files = partial(self.listFiles, 
                    file.get('id'), 
                    name_pattern=name_pattern,
                    file_types=file_types,
                    recursive_depth=-1,
                    do_print=do_print
                )
                if recursive_depth == -1:  # Unlimited recursion
                    subfolder_items = list_files()
                    items.extend(subfolder_items)
                elif recursive_depth > 0:  # Specific depth limit
                    subfolder_items = list_files(recursive_depth=recursive_depth-1)
                    items.extend(subfolder_items)

        if name_pattern:
            items = filter_by_col(items, 'name', name_pattern)

        items = add_count_col(items, 'folder')
                
        return items
    

    
    def listSpreadsheets(self, 
        folder_id: str, 
        name_pattern: str|None = None,
        recursive_depth: int = 0,
        with_meta: bool = False,
        do_print: bool = False
    ):
        '''
        List all spreadsheets in a folder.
        
        Args:
            folder_id (str): Folder ID to search in
            recursive (bool): Whether to search recursively
            include_schemas (bool): Whether to include column schemas for each sheet
            
        Returns:
            list: List of spreadsheet dictionaries with metadata and sheet schemas
        '''
        
        items = self.listFiles(
            folder_id, 
            name_pattern, 
            [MimeType.SHEET_GOOGLE], 
            recursive_depth, 
            do_print
        )

        items = filter_by_col(items, 'type', 'file')

        if with_meta:
            for item in items:
                meta = self.getSpreadsheetMetadata(item['id'])
                tabs = []
                for tab in meta:
                    tabs.append(tab['tab_name'] + ': ' + str(tab['row_count']))
                item['tabs'] = tabs

        return items



    def _isGoogleWorkspaceFile(self, mime_type):
        """Check if file is a Google Workspace file that needs to be exported"""
        google_workspace_types = {
            MimeType.DOC_GOOGLE,
            MimeType.SHEET_GOOGLE,
            MimeType.SLIDE_GOOGLE,
            MimeType.FORM_GOOGLE
        }
        return mime_type in google_workspace_types


    def _getDefaultExportExt(self, google_mime_type):
        """Get default export extension for Google Workspace files"""
        defaults = {
            MimeType.DOC_GOOGLE: 'pdf',
            MimeType.SHEET_GOOGLE: 'xlsx',
            MimeType.SLIDE_GOOGLE: 'pptx',
            MimeType.FORM_GOOGLE: 'csv'
        }
        return defaults.get(google_mime_type, 'pdf')



    def downloadFile(self, 
        file_id: str, 
        file_path: str|None = None, 
        as_mime_type: MimeType|None = None,
        do_print: bool = False
    ) -> str:
        """
        Download a file from Google Drive by its file ID and save it to the specified path.
        Handles both binary files and Google Workspace files automatically.
        
        Args:
            file_id (str): The Google Drive file ID
            file_path (str, optional): The relative path where to save the file.
                                    If not provided, uses the original filename.
        
        Returns:
            str: The absolute path where the file was saved
        """
        
        meta = self.getFileMetadata(file_id)
        mime_type = meta['mime_type']
        export_as_mime_type = mime_type
        if file_path is None:
            file_path = meta['path']
        is_workspace_file = self._isGoogleWorkspaceFile(mime_type)
        extension = MimeType.getExtFromMimeType(mime_type)
        
        if is_workspace_file:
            extension = self._getDefaultExportExt(mime_type)
            export_as_mime_type = MimeType.getMimeTypeFromExt(extension)

        if as_mime_type is not None and mime_type != MimeType.FORM_GOOGLE:
            extension = MimeType.getExtFromMimeType(as_mime_type)
            export_as_mime_type = as_mime_type
        
        file_path = file_path + '.' + extension
        
        absolute_path = drive_path(file_path)
        
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        if mime_type == MimeType.FORM_GOOGLE:
            if do_print:
                print(f'Exporting Google Form responses "{meta['name']}" as csv...')
            self._downloadFormResponses(file_id, meta, absolute_path)
        else:
            if is_workspace_file:
                # Google Workspace file, can't be downloaded, use export as
                # export_mime = self._getExportMimeType(extension, mime_type)
                request = self.drive.files().export_media(fileId=file_id, mimeType=export_as_mime_type)
                if do_print:
                    print(f'Exporting Google {mime_type.split('.')[-1]} file "{meta['name']}" as {extension}...')
            else:
                # Regular binary file, download it
                request = self.drive.files().get_media(fileId=file_id)
                if do_print:
                    print(f'Downloading binary file "{meta['name']}" of type {mime_type}...')
            
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                # print(f"Download progress: {int(status.progress() * 100)}%")
            
            with open(absolute_path, 'wb') as f:
                f.write(file_handle.getvalue())
        
        if do_print:
            print(f"File saved to: {absolute_path}")
        return absolute_path
    

    def _downloadFormResponses(self, form_id, file_meta, absolute_path):
        '''Download form responses as a CSV file with question titles as headers.'''
        responses = self.getFormResponses(form_id)
        if not responses:
            return False

        headers = []
        if responses:
            headers = responses[0].keys()

        # Write to CSV
        with open(absolute_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(responses)

        return True


    def getFormMetadata(self, form_id):
        form_data = self.forms.forms().get(formId=form_id).execute()
        return GoogleFormParser.parse(form_data)


    def getFormQuestions(self, form_id):
        form_meta = self.getFormMetadata(form_id)
        questions = filter_by_col(form_meta['items'], 'type', GoogleFormParser.TYPE_QUESTION)
        return questions
    

    def getFormResponses(self, form_id):
        responses = self.forms.forms().responses().list(formId=form_id).execute()
        questions = self.getFormQuestions(form_id)
        return GoogleFormParser.parseResponses(responses, questions)


    def getSpreadsheetMetadata(self, spreadsheet_id):
        response = self.sheets.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields='sheets(properties)'
        ).execute()

        sheets = response.get('sheets', [])
        items = []
        for sheet in sheets:
            props = sheet['properties']
            item = {
                'tab_id': props['sheetId'],
                'tab_name': props['title'],
                'order': props['index'],
                'row_count': props['gridProperties']['rowCount'],
                'col_count': props['gridProperties']['columnCount']
            }
            items.append(item)

        return items
