
from typing import Type, Literal, TYPE_CHECKING
from enum import Enum, IntEnum, StrEnum
import os
import json

from google_auth_oauthlib.flow import InstalledAppFlow # type: ignore
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.admin_v1beta import AnalyticsAdminServiceClient

if TYPE_CHECKING:
    from arkalos.services.google_stubs.drive.v3 import DriveResource   
    from arkalos.services.google_stubs.sheets.v4 import SheetsResource
    from arkalos.services.google_stubs.searchconsole.v1 import SearchConsoleResource
    from arkalos.services.google_stubs.forms.v1 import FormsResource

from arkalos.core.path import base_path
from arkalos.core.config import config



class GoogleAuthType(IntEnum):
    OAUTH = 1
    SERVICE_ACC = 2

class GoogleScopeType(StrEnum):
    # List of Scopes:
    # https://developers.google.com/identity/protocols/oauth2/scopes

    # Google Drive API
    DRIVE_READ = 'https://www.googleapis.com/auth/drive.readonly'
    # Google Sheets API
    SHEETS_READ = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    # Google Search Console API
    SEARCH_CONSOLE_READ = 'https://www.googleapis.com/auth/webmasters.readonly'
    # Google Analytics Data API and Google Analytics Admin API
    ANALYTICS_READ = 'https://www.googleapis.com/auth/analytics.readonly'
    # Google Forms API
    FORMS_READ = 'https://www.googleapis.com/auth/forms.body.readonly'
    FORMS_RESPONSES_READ = 'https://www.googleapis.com/auth/forms.responses.readonly'

class GoogleServiceBuilderType(Enum):
    DRIVE = ('drive', 'v3', None)
    SHEETS = ('sheets', 'v4', None)
    SEARCH_CONSOLE = ('searchconsole', 'v1', None)
    ANALYTICS = ('analytics', None, BetaAnalyticsDataClient)
    ANALYTICS_ADMIN = ('analytics_admin', None, AnalyticsAdminServiceClient)
    FORMS = ('forms', 'v1', None)

    @property
    def name(self):
        return self.value[0]
    
    @property
    def version(self):
        return self.value[1]
    
    @property
    def cls(self):
        return self.value[2]



class GoogleService:

    AUTH: Type[GoogleAuthType] = GoogleAuthType
    SCOPE: Type[GoogleScopeType] = GoogleScopeType
    ACCESS_TOKEN_PATH: str = 'data/tokens/google_access_token.json'

    auth_type: GoogleAuthType
    key_path: str
    scopes: list[GoogleScopeType]
    credentials: Credentials
    services: dict[str, object]



    def __init__(self, 
        scopes: list[GoogleScopeType]|None = None, 
        auth_type: GoogleAuthType = GoogleAuthType.OAUTH, 
        key_path: str|None = None
    ):
        """Provide auth type (oauth or service account) or provide a custom key path"""
        if (key_path is None):
            if (auth_type == GoogleAuthType.OAUTH):
                key_path = base_path(config('data_sources.google.oauth_key_path'))
            else:
                key_path = base_path(config('data_sources.google.service_account_key_path'))
        
        if (scopes is None):
            scopes = [
                GoogleScopeType.DRIVE_READ,
                GoogleScopeType.SHEETS_READ,
                GoogleScopeType.FORMS_READ,
                GoogleScopeType.FORMS_RESPONSES_READ,
                GoogleScopeType.SEARCH_CONSOLE_READ,
                GoogleScopeType.ANALYTICS_READ
            ]

        self.auth_type = auth_type
        self.scopes = scopes
        self.key_path = key_path
        self.services = {}
        # set self.credentials
        self.authenticate(scopes, auth_type, key_path)



    @staticmethod
    def detectKeyType(json_file_path: str) -> GoogleAuthType|Literal[False]:
        """Reads a JSON file and detects if it's a Google OAuth key or Service Account key."""
        try:
            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Check if the key is a service account
            if data.get("type") == "service_account":
                return GoogleAuthType.SERVICE_ACC

            # Check for OAuth key (OAuth credentials usually have installed/web keys)
            if "installed" in data or "web" in data:
                return GoogleAuthType.OAUTH

            raise Exception('Unknown Google Key Type')
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            return False



    def authenticate(self, scopes: list, auth_type: int, key_path: str) -> None:
        creds = None
        access_token_path = base_path(self.ACCESS_TOKEN_PATH)

        if auth_type == GoogleAuthType.OAUTH:
            # The file access_token.json stores the user's access and refresh tokens, and is created
            # automatically when the authorization flow completes for the first time.
            if os.path.exists(access_token_path):
                creds = Credentials.from_authorized_user_file(access_token_path, scopes)
            # If there are no (valid) credentials available, let the user log in.
            # Copy the link from the terminal and open it in your browser, approve the scopes and continue,
            # Then access token will be stored and script will continue.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(key_path, scopes)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(access_token_path, "w") as token:
                    token.write(creds.to_json())
        else:
            # Service Account
            creds = service_account.Credentials.from_service_account_file(key_path, scopes=scopes)

        self.credentials = creds



    def _buildServiceInstance(self, type: GoogleServiceBuilderType):
        if (type.name not in self.services):
            if (type.cls is None):
                self.services[type.name] = build(type.name, type.version, credentials=self.credentials)
            else:
                self.services[type.name] = type.cls(credentials=self.credentials)
        return self.services[type.name]

    def drive(self) -> 'DriveResource':
        return self._buildServiceInstance(GoogleServiceBuilderType.DRIVE)
        
    def sheets(self) -> 'SheetsResource':
        return self._buildServiceInstance(GoogleServiceBuilderType.SHEETS)
    
    def forms(self) -> 'FormsResource':
        return self._buildServiceInstance(GoogleServiceBuilderType.FORMS)
        
    def searchConsole(self) -> 'SearchConsoleResource':
        return self._buildServiceInstance(GoogleServiceBuilderType.SEARCH_CONSOLE)
        
    def analytics(self) -> BetaAnalyticsDataClient:
        return self._buildServiceInstance(GoogleServiceBuilderType.ANALYTICS)
    
    def analyticsAdmin(self) -> AnalyticsAdminServiceClient:
        return self._buildServiceInstance(GoogleServiceBuilderType.ANALYTICS_ADMIN)
