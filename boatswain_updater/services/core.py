#  This file is part of Boatswain.
#
#      Boatswain<https://github.com/theboatswain> is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Boatswain is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Boatswain.  If not, see <https://www.gnu.org/licenses/>.
#
#

import logging
import os
import shutil
import tempfile
import zipfile

from boatswain_updater.exceptions.installation import InstallationFailedException, ReleaseFolderStructureIncorrect
from boatswain_updater.models.app_to_update import AppToUpdate
from boatswain_updater.utils import sys_utils, pyqt_utils, permission_utils, resources_utils

logger = logging.getLogger(__name__)
exclude_dirs = ['__MACOSX']


def getUpdateDir(extract_to):
    for directory in os.listdir(extract_to):
        if os.path.isdir(os.path.join(extract_to, directory)) and directory not in exclude_dirs:
            return directory


def installUpdate(update_file: str, progress_callback=None):
    """
    Install the update from the given update file as Zip
    Step 1: Extracting the file
    Step 2: Verify updating structure
    Step 3:
        If the destination has write permission, then directly extract data to that folder
        Else, request for privilege permission to execute the installer scripts
            located in the boatswain_updater/installer's folder
    At this moment, if no error occurred, then restart the application so then the new update will take effective
    """

    logger.info('Starting update')
    logger.info('Extracting update...')
    extract_to = tempfile.mkdtemp(suffix='', prefix='boatswain_x_zip_', dir=None)
    zip_file = zipfile.ZipFile(update_file, 'r')
    for file in zip_file.infolist():
        zip_file.extract(file, extract_to)
        os.chmod(os.path.join(extract_to, file.filename), 0o755)  # make executable
    zip_file.close()
    original_app = AppToUpdate()

    update_app_path = os.path.join(extract_to, getUpdateDir(extract_to))

    logger.info('Update data path: ' + update_app_path)
    if not verifyUpdateStructure(update_app_path, original_app):
        logger.error('Update app: %s and original app: %s are not the same structure'
                     % (update_app_path, original_app.folder))
        raise ReleaseFolderStructureIncorrect()

    if original_app.hasPermission():
        cleanupPreviousVersion()
        copyFolderNoRoot(update_app_path, original_app)
    else:
        copyFolderWithRoot(update_app_path, original_app)


def cleanupPreviousVersion():
    """
    When we are doing the processing of update, then all of the files of the old version will be added .bak extension
    This function will clean those file.
    """
    original_app = AppToUpdate()
    if permission_utils.isDirWritable(original_app.folder):
        files = sys_utils.getListOfFiles(original_app.folder)
        for f in files:
            if f.endswith(".bak"):
                os.unlink(os.path.join(original_app.folder, f))


def verifyUpdateStructure(update_app_path: str, original_app: AppToUpdate):
    """
    This function will ensure the structure of the update folder path have the same structure
    with the original folder path
    @return: boolean
    """
    relative_exe_location = original_app.getRelativeExecutable()
    return os.path.isfile(os.path.join(update_app_path, relative_exe_location))


def copyFolderNoRoot(update_app_path: str, original_app: AppToUpdate):
    """
    If we have permission to write in the destination, no need to do anything too complex
    Move the extracted files into the destination folder
    The original files will be added .bak extension for backing up
    """
    logger.info("Starting to move files from %s -> %s" % (update_app_path, original_app.folder))
    try:
        for f in sys_utils.getListOfFiles(update_app_path):
            if os.path.isfile(os.path.join(original_app.folder, f)):
                os.rename(os.path.join(original_app.folder, f), os.path.join(original_app.folder, f) + ".bak")
            shutil.move(os.path.join(update_app_path, f), os.path.join(original_app.folder, f))
    except OSError as e:
        logger.error("Exception occurred, rolling back to the earlier backed up version.\n Exception: %s", e)
        raise InstallationFailedException()


def copyFolderWithRoot(update_app_path: str, original_app: AppToUpdate):
    """
    In case we don't have permission, we will start an external script and ask for an executing permission
    """
    if sys_utils.isMac() or sys_utils.isLinux():
        fd, installer = tempfile.mkstemp(suffix='.sh')
        pyqt_utils.defrostAndSaveInto(resources_utils.getResource('installers/posix/installer.sh'), installer)
    else:
        fd, installer = tempfile.mkstemp(suffix='.bat')
        pyqt_utils.defrostAndSaveInto(resources_utils.getResource('installers/windows/installer.bat'), installer)

    os.close(fd)
    os.chmod(installer, 0o755)  # make executable
    command = [installer, update_app_path, original_app.folder]

    logger.info("Calling command %s" % ' '.join(command))
    try:
        res_code = permission_utils.runAsAdmin(command)
        if res_code == 0:
            return
        else:
            logger.error("Exception occurred, exit code: %d" % res_code)
    except OSError as e:
        logger.error("Exception occurred, rolling back to the earlier backed up version.\n Exception: %s", e)
    finally:
        os.unlink(installer)
    raise InstallationFailedException()
