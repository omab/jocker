import shutil
import logging

import dirsync


def compress(dirname):
    """
    Compress the directory into a .tar.gz file.
    """
    return dirname


def decompress(filename):
    """
    Decompress the .tar.gz into a directory.
    """
    return filename


def copy_tree(src, dest):
    """Copy the tree structure from src to dest"""
    try:
        shutil.copytree(src, dest)
    except (shutil.Error, FileExistsError):
        logger = logging.getLogger('dirsync')
        status_backup = logger.disabled
        logger.disabled = True
        dirsync.sync(src, dest, 'sync', verbose=False)
        logger.disabled = status_backup


def copy_file(src, dest):
    """Copy the file src to dest"""
    shutil.copy2(src, dest)
