"""Async Downloader module"""

# Standar import
import os
import re
import asyncio
from typing import List, Optional, Iterable

# Non standar import
import inquirer
import aiohttp
from pydantic import BaseModel

class Chunk(BaseModel):
    """Chunk class contains start and end, that can be used for Range headers"""
    start   : int
    end     : int

class FileInfo(BaseModel):
    """FileInfo class"""
    filename    : str
    file_size   : int
    download_url: str
    chunk_list  : Optional[List[Chunk]]

class LinkParser:
    """Class that contains various method to parse download link from various site"""
    def __init__(
        self,
        session : aiohttp.ClientSession
    ) -> None   :
        self.session = session

    async def parse_mediafire(
        self,
        url     : str
    ) -> str    :
        """Method to parse Mediafire url"""
        async with self.session.get(url) as resp:
            assert resp.status == 200, 'Link not working'
            return re.search(r'href\=\"(.*?)\"\s+id\=\"downloadButton\"', await resp.text())[1]

    async def parse_77file(
        self,
        url     : str,
    ) -> str    :
        """Method to parse 77file url"""

class Downloader:
    """The main class"""
    def __init__(
        self,
        filepath : str = './',
        chunk    : str = 10
    ) -> None    :
        self.session    = aiohttp.ClientSession()
        self.parser     = LinkParser(self.session)
        self.filepath   = filepath
        self.chunk      = chunk

    async def get_file_info(
        self,
        url           : str,
        get_chunk_info: bool = True
    ) -> FileInfo     :
        """Method that return FileInfo object that contains File information from given url"""
        download_url   = await self.parser.parse_mediafire(url)
        async with self.session.head(download_url) as resp:
            pattern    = r'filename\=\"(.*?)\"'
            filename   = re.search(pattern, resp.headers.get('Content-Disposition'))[1]
            file_size  = int(resp.headers.get('Content-Length'))
            chunk_size = file_size // self.chunk
            start, end = 0, chunk_size

            if get_chunk_info:
                chunk_list = []
                for idx in range(self.chunk):
                    chunk_list.append(
                        Chunk(
                            start    = start,
                            end      = end
                        )
                    )
                    start    = end + 1
                    end     += file_size if idx == self.chunk - 1 else chunk_size + 1
            else:
                chunk_list   = None

            return FileInfo(
                filename     = filename,
                file_size    = file_size,
                download_url = download_url,
                chunk_list   = chunk_list
            )

    async def get_section(
        self,
        url  : str,
        chunk: Chunk,
    ) -> None:
        """Download section from given range headers"""
        headers ={'Range': f"bytes={chunk.start}-{chunk.end}"}
        async with self.session.get(url, headers = headers) as resp:
            return await resp.content.read()

    async def download(
        self,
        url  : str
    ) -> None:
        """Wrapper for get_section() method. Download single file"""
        file_info = await self.get_file_info(url)

        if file_info.filename in os.listdir():
            questions = [
                inquirer.List(
                    'actions',
                    message = 'File already exists, choose action to perform',
                    choices = [
                        'Replace file',
                        'Rename file',
                        'Cancel download'
                    ]
                ),
                inquirer.Confirm(
                    'confirm_replace_file',
                    message  = 'Are you sure to replace the file',
                    default  = False,
                    ignore   = lambda x: x['actions'] != 'Replace file'
                ),
                inquirer.Text(
                    'rename_file',
                    message  = f'Rename {file_info.filename} to',
                    validate = lambda a, c: c != '',
                    ignore   = lambda x: x['actions'] != 'Rename file'
                ),
                inquirer.Confirm(
                    'confirm_cancel_download',
                    message  = 'Are you sure to cancel download',
                    default  = False,
                    ignore   = lambda x: x['actions'] != 'Cancel download'
                ),
            ]

            answers = inquirer.prompt(questions)
            if answers.get('actions') == 'Replace file' \
            and answers.get('confirm_replace_file'):
                os.system(f'rm "{file_info.filename}"')

            if answers.get('actions') == 'Replace file' \
            and not answers.get('confirm_replace_file'):
                answers = inquirer.prompt(questions)

            if answers.get('actions') == 'Rename file' \
            and answers.get('rename_file'):
                file_info.filename = answers.get('rename_file')

            if answers.get('actions') == 'Cancel download' \
            and answers.get('confirm_cancel_download'):
                return
            if answers.get('actions') == 'Cancel download' \
            and not answers.get('confirm_cancel_download'):
                answers = inquirer.prompt(questions)

        filepath = f'{self.filepath}/{file_info.filename}'
        sections = await asyncio.gather(
            *[
                self.get_section(file_info.download_url, chunk) for chunk in file_info.chunk_list
            ]
        )

        with open(filepath, 'ab') as f_handler:
            for section in sections:
                f_handler.write(section)

        print(f'{file_info.filename} downloaded!')

    async def batch_download(
        self,
        urls : Iterable
    ) -> None:
        """Wrapper for download() method. Download multiple files"""
        async with asyncio.TaskGroup() as task_group:
            for url in urls:
                task_group.create_task(self.download(url))
        await self.close_session()

    async def close_session(self):
        """Closing aiohttp.ClientSession() session"""
        await self.session.close()
