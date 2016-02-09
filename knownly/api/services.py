import logging

from django.contrib.auth import get_user_model
from dropbox import Dropbox
from dropbox.files import ListFolderError

from knownly.api.exceptions import DirectoryDoesNotExistError

logger = logging.getLogger(__name__)

User = get_user_model()


class DropboxDirectoryListingService(object):

    def __init__(self, dropbox_user, dropbox=None):
        if dropbox:
            self.dropbox = dropbox
        else:
            self.dropbox = Dropbox(dropbox_user.dropbox_token)

    def get_directory_listing(self, path):

        try:
            result = self.dropbox.files_list_folder('/' + path)
            files = result.entries

            while result.has_more:
                result = self.dropbox.files_list_folder_continue(result.cursor)
                files.append(result.entries)
        except ListFolderError as lfe:
            if lfe.error.is_path():
                if not lfe.error.get_path().error.is_not_found():
                    logger.debug(lfe.error.user_message_text)
                raise DirectoryDoesNotExistError()
            else:
                raise lfe

        for f in files:
            f.path_lower = f.path_lower.lstrip('/')

        return files
