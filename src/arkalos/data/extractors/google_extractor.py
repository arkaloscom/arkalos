
from typing import Type

from arkalos.services.google_service import GoogleService, GoogleAuthType, GoogleScopeType

from arkalos.data.extractors.google.google_analytics import GoogleAnalytics
from arkalos.data.extractors.google.google_drive import GoogleDrive



class GoogleExtractor:

    AUTH: Type[GoogleAuthType] = GoogleAuthType
    SCOPE: Type[GoogleScopeType] = GoogleScopeType

    service: GoogleService
    drive: GoogleDrive 
    analytics: GoogleAnalytics

    def __init__(self, 
        scopes: list[GoogleScopeType]|None = None, 
        auth_type: GoogleAuthType = GoogleAuthType.OAUTH, 
        key_path: str|None = None
    ):
        self.service = GoogleService(scopes, auth_type, key_path)
        self.drive = GoogleDrive(self.service)
        self.analytics = GoogleAnalytics(self.service)
