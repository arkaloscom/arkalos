
from enum import StrEnum

class MimeType(StrEnum):

    # Folder types
    FOLDER_GOOGLE = 'application/vnd.google-apps.folder'
    FOLDER_MS_ONEDRIVE = 'application/onedrive'
    FOLDER_APPL_ICLOUD = 'application/icloud'

    # Text types
    TXT_TEXT = 'text/plain'
    TXT_HTML = 'text/html'
    TXT_CSS = 'text/css'
    TXT_JAVASCRIPT = 'text/javascript'
    TXT_CSV = 'text/csv'
    TXT_JSON = 'application/json'
    TXT_XML = 'application/xml'

    # Image types
    IMG_JPEG = 'image/jpeg'
    IMG_PNG = 'image/png'
    IMG_GIF = 'image/gif'
    IMG_SVG = 'image/svg+xml'

    # Audio types
    AUD_MP3 = 'audio/mpeg'
    AUD_WAV = 'audio/wav'
    AUD_OGG = 'audio/ogg'

    # Video types
    VID_MP4 = 'video/mp4'
    VID_OGG = 'video/ogg'
    VID_WEBM = 'video/webm'

    # Docs
    DOC_PDF = 'application/pdf'
    DOC_GOOGLE = 'application/vnd.google-apps.document'
    DOC_MS_WORD = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    DOC_MS_WORD_OLD = 'application/msword'
    DOC_LIBRE_WRITER = 'application/vnd.oasis.opendocument.text'
    DOC_APPL_PAGES = 'application/x-iwork-pages-sffpages'

    # Forms
    FORM_GOOGLE = 'application/vnd.google-apps.form'

    # Spreadsheets
    SHEET_GOOGLE = 'application/vnd.google-apps.spreadsheet'
    SHEET_MS_EXCEL = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    SHEET_MS_EXCEL_OLD = 'application/vnd.ms-excel'
    SHEET_LIBRE_CALC = 'application/vnd.oasis.opendocument.spreadsheet'
    SHEET_APPL_NUMBERS = 'application/x-iwork-numbers-sffnumbers'

    # Slides
    SLIDE_GOOGLE = 'application/vnd.google-apps.presentation'
    SLIDE_MS_POWERPOINT = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    SLIDE_MS_POWERPOINT_OLD = 'application/vnd.ms-powerpoint'
    SLIDE_LIBRE_IMPRESS = 'application/vnd.oasis.opendocument.presentation'
    SLIDE_APPL_KEYNOTE = 'application/x-iwork-keynote-sffkey'

    # Compression and archives
    COMPR_ZIP = 'application/zip'
    COMPR_GZIP = 'application/gzip'
    
    # Other data storage, analysis and ML formats
    DATA_PARQUET = 'application/vnd.apache.parquet'
    DATA_HDF5 = 'application/x-hdf5'
    DATA_PICKLE = 'application/python-pickle'
    DATA_FEATHER = 'application/feather'
    DATA_ONNX = 'application/onnx'

    # Other
    OCTET_STREAM = 'application/octet-stream'


    @classmethod
    def getExtFromMimeType(cls, mime_type):
        """Get file extension for a mime type"""
        extensions = {
            cls.FOLDER_GOOGLE: '',
            cls.FOLDER_MS_ONEDRIVE: '',
            cls.FOLDER_APPL_ICLOUD: '',
            # Text types
            cls.TXT_TEXT: 'txt',
            cls.TXT_HTML: 'html',
            cls.TXT_CSS: 'css',
            cls.TXT_JAVASCRIPT: 'js',
            cls.TXT_CSV: 'csv',
            cls.TXT_JSON: 'json',
            cls.TXT_XML: 'xml',
            # Image types
            cls.IMG_JPEG: 'jpg',
            cls.IMG_PNG: 'png',
            cls.IMG_GIF: 'gif',
            cls.IMG_SVG: 'svg',
            # Audio types
            cls.AUD_MP3: 'mp3',
            cls.AUD_WAV: 'wav',
            cls.AUD_OGG: 'ogg',
            # Video types
            cls.VID_MP4: 'mp4',
            cls.VID_OGG: 'ogv',
            cls.VID_WEBM: 'webm',
            # Docs
            cls.DOC_PDF: 'pdf',
            cls.DOC_GOOGLE: 'pdf',
            cls.DOC_MS_WORD: 'docx',
            cls.DOC_MS_WORD_OLD: 'doc',
            cls.DOC_LIBRE_WRITER: 'odt',
            cls.DOC_APPL_PAGES: 'pages',
            # Forms
            cls.FORM_GOOGLE: 'csv',
            # Spreadsheets
            cls.SHEET_GOOGLE: 'xlsx',
            cls.SHEET_MS_EXCEL: 'xlsx',
            cls.SHEET_MS_EXCEL_OLD: 'xls',
            cls.SHEET_LIBRE_CALC: 'ods',
            cls.SHEET_APPL_NUMBERS: 'numbers',
            # Slides
            cls.SLIDE_GOOGLE: 'pptx',
            cls.SLIDE_MS_POWERPOINT: 'pptx',
            cls.SLIDE_MS_POWERPOINT_OLD: 'ppt',
            cls.SLIDE_LIBRE_IMPRESS: 'odp',
            cls.SLIDE_APPL_KEYNOTE: 'key',
            # Compression and archives
            cls.COMPR_ZIP: 'zip',
            cls.COMPR_GZIP: 'gz',
            # Other data storage
            cls.DATA_PARQUET: 'parquet',
            cls.DATA_HDF5: 'h5',
            cls.DATA_PICKLE: 'pkl',
            cls.DATA_FEATHER: 'feather',
            cls.DATA_ONNX: 'onnx',
            # Other
            cls.OCTET_STREAM: 'bin'
        }
        return extensions.get(mime_type, 'bin')
    
    @classmethod
    def getMimeTypeFromExt(cls, extension):
        """Get MIME type from file extension"""
        extension = extension.lower().lstrip('.')
        ext_to_mime = {
            # Text types
            'txt': cls.TXT_TEXT,
            'html': cls.TXT_HTML, 'htm': cls.TXT_HTML,
            'css': cls.TXT_CSS,
            'js': cls.TXT_JAVASCRIPT,
            'csv': cls.TXT_CSV,
            'json': cls.TXT_JSON,
            'xml': cls.TXT_XML,
            # Image types
            'jpg': cls.IMG_JPEG, 'jpeg': cls.IMG_JPEG,
            'png': cls.IMG_PNG,
            'gif': cls.IMG_GIF,
            'svg': cls.IMG_SVG,
            # Audio types
            'mp3': cls.AUD_MP3,
            'wav': cls.AUD_WAV,
            'ogg': cls.AUD_OGG,
            # Video types
            'mp4': cls.VID_MP4,
            'ogv': cls.VID_OGG,
            'webm': cls.VID_WEBM,
            # Docs
            'pdf': cls.DOC_PDF,
            'docx': cls.DOC_MS_WORD,
            'doc': cls.DOC_MS_WORD_OLD,
            'odt': cls.DOC_LIBRE_WRITER,
            'pages': cls.DOC_APPL_PAGES,
            # Spreadsheets
            'xlsx': cls.SHEET_MS_EXCEL,
            'xls': cls.SHEET_MS_EXCEL_OLD,
            'ods': cls.SHEET_LIBRE_CALC,
            'numbers': cls.SHEET_APPL_NUMBERS,
            # Slides
            'pptx': cls.SLIDE_MS_POWERPOINT,
            'ppt': cls.SLIDE_MS_POWERPOINT_OLD,
            'odp': cls.SLIDE_LIBRE_IMPRESS,
            'key': cls.SLIDE_APPL_KEYNOTE,
            # Compression and archives
            'zip': cls.COMPR_ZIP,
            'gz': cls.COMPR_GZIP,
            # Other data storage
            'parquet': cls.DATA_PARQUET,
            'h5': cls.DATA_HDF5,
            'pkl': cls.DATA_PICKLE, 'pickle': cls.DATA_PICKLE,
            'feather': cls.DATA_FEATHER,
            'onnx': cls.DATA_ONNX,
            # Default
            'bin': cls.OCTET_STREAM
        }
        return ext_to_mime.get(extension, cls.OCTET_STREAM)