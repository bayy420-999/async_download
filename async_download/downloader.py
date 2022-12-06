import os, re, inquirer
import asyncio, aiohttp, aiofiles
from pydantic import BaseModel
from typing import Optional, List, Dict

class Chunk(BaseModel):
    filename: str
    size    : int 
    start   : int 
    end     : int

class FileInfo(BaseModel):
    filename    : str
    file_size   : int 
    download_url: str 
    chunk_list  : Optional[List[Chunk]]

class LinkParser:
    def __init__(
        self,
        session  : aiohttp.ClientSession
        ) -> None:
        self.session = session 

    async def parse_mediafire(
        self,
        url     : str
        ) -> str:
        async with self.session.get(url) as resp:
            assert resp.status == 200, 'Link not working'
            return re.search(r'href\=\"(.*?)\"\s+id\=\"downloadButton\"', await resp.text())[1]

class Downloader:
    def __init__(
        self,
        filepath : str = './',
        chunk    : str = 10
        ) -> None:
        self.session    = aiohttp.ClientSession()
        self.parser     = LinkParser(self.session)
        self.filepath   = filepath
        self.chunk      = chunk

    async def get_file_info(
        self,
        url           : str,
        get_chunk_info: bool = True
        ) -> FileInfo :
        download_url   = await self.parser.parse_mediafire(url)
        async with self.session.head(download_url) as resp:
            filename   = re.search(r'filename\=\"(.*?)\"', resp.headers.get('Content-Disposition'))[1]
            file_size  = int(resp.headers.get('Content-Length'))
            temp_path  = f'temp/{filename}'
            chunk_size = file_size // self.chunk
            start, end = 0, chunk_size

            if get_chunk_info:
                chunk_list = []
                for idx in range(self.chunk):
                    tempfile         = f'part-{idx}.tmp'
                    chunk_chunk_size = end - start + 1
                    chunk_list.append(
                        Chunk(
                            filename = tempfile,
                            size     = chunk_chunk_size,
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
        url      : str,
        chunk    : Chunk,
        temp_path: str
        ) -> None:
        headers ={'Range': f"bytes={chunk.start}-{chunk.end}"}
        async with self.session.get(url, headers = headers) as resp:
            async with aiofiles.open(f'{temp_path}/{chunk.filename}', mode = 'wb') as f:
                await f.write(await resp.content.read())

    def merge_file(
        self,
        temp_path: str,
        filename : str
        ) -> None:
        files = sorted(os.listdir(temp_path))
        filename = self.filepath + filename

        with open(filename, 'ab') as outfile:
            for file in files:
                with open(f'{temp_path}/{file}', 'rb') as f:
                    outfile.write(f.read())

        os.system(f'rm -rf "{temp_path}"')
 
    async def download(
        self,
        url      : str
        ) -> None:
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
                    message  = 'Are you sure to replace the file',
                    default  = False,
                    ignore   = lambda x: x['actions'] != 'Cancel download'
                ),
            ]

            answers = inquirer.prompt(questions)
            if answers.get('actions') == 'Replace file' and answers.get('confirm_replace_file'):
                os.system(f'rm {file_info.filename}')
            elif answers.get('actions') == 'Replace file' and not answers.get('confirm_replace_file'):
                answers = inquirer.prompt(questions)

            if answers.get('actions') == 'Rename file' and answers.get('rename_file'):
                file_info.filename = answers.get('rename_file')

            if answers.get('actions') == 'Cancel download' and answers.get('confirm_cancel_download'):
                return
            elif answers.get('actions') == 'Cancel download' and not answers.get('confirm_cancel_download'):
                answers = inquirer.prompt(questions)

        temp_path = f'{self.filepath}/temp/{file_info.filename}'
        os.makedirs(temp_path, exist_ok = True)
        async with asyncio.TaskGroup() as tg:
            for chunk in file_info.chunk_list:
                tg.create_task(
                    self.get_section(
                        file_info.download_url,
                        chunk,
                        temp_path
                    )
                )

        self.merge_file(temp_path, file_info.filename)
        print(f'{file_info.filename} downloaded!')

    async def batch_download(
        self,
        urls     : List[str]
        ) -> None:
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                tg.create_task(self.download(url))
        await self.close_session()

    async def close_session(self):
        await self.session.close()
