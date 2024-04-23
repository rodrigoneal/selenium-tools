from pathlib import Path
from time import time
from typing import Any, Callable, Dict, Optional, Tuple

from selenium_tools.page_objects.page_objects import Element


class UnintilizedFileDownload(Exception):
    """
    This exception occurs when the function does not find any new files in the folder during the timeout.
    """
    pass


class UnfinishedFileDownload(Exception):
    """
    This exception occurs when the function finds a new file inside the folder. 
    But the timeout has passed and the file continues with the downloading pattern.
    """
    pass


class DownloadFolderException(Exception):
    pass


def wait_chrome_download(timeout: float = 10, download_folder: Optional[Path] = None) -> Path:
    def decorator(func: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        def inner(*args: Tuple[Any], **kwargs: Dict[Any, Any]) -> Path:
            """
            This function checks the items in the past folder and compares the update over time. 
            If no file appears or the waiting time elapses, throws exceptions. 
            Otherwise it checks if the file is already downloaded, with defaults in its name.
            And returns its path.
            :args:
                timeout: time the function has to validate that the download has completed
                download_path: path of the download folder that will be used to check if the file is in it
                download_function: callable that sends the download request to the file
            :returns: returns the path of the file that was downloaded
            """
            elemento_pagina = None
            for arg in args:
                if isinstance(arg, Element):
                    elemento_pagina = arg
                    break
                raise DownloadFolderException('Pasta de download não encontrada.')
            download_path = download_folder
            if not download_folder:                
                download_path = elemento_pagina.driver.caps['options']                
            old_files_list = set(Path(download_path).resolve().iterdir())
            end_time = time() + timeout
            print(args, kwargs)
            func(*args, **kwargs)

            while time() <= end_time:
                current_files_list = set(
                    Path(download_path).resolve().iterdir())
                if len(current_files_list) > len(old_files_list):
                    break
            else:
                raise UnintilizedFileDownload('The download did not start')

            while time() <= end_time:
                current_files_list = set(
                    Path(download_path).resolve().iterdir())
                file_path = (old_files_list ^ current_files_list).pop()
                if file_path.suffix not in ('.tmp', '.crdownload') and '.com.google.Chrome.' not in file_path.name:
                    return file_path

            raise UnfinishedFileDownload('The download was not completed')
        return inner
    return decorator