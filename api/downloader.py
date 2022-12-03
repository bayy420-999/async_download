import os, re
import asyncio, aiohttp, aiofiles
from tqdm.asyncio import tqdm
from api.link_parser import LinkParser

class Downloader:
    def __init__(self, filepath = './', download_limit = 5, chunk = 10, chunk_size = 1024):
        self.session = aiohttp.ClientSession()
        self.filepath = filepath
        self.chunk = chunk
        self.chunk_size = chunk_size * 10
        
    async def get_file_info(self, url):
        async with self.session.head(url) as resp:
            return resp.headers

    async def get_section(self, filename, url, headers):
        async with self.session.get(url, headers = headers) as resp:
            total = int(resp.headers.get('Content-Length'))
            async with aiofiles.open(filename, mode = 'wb') as f:
                with tqdm(total = total, unit = 'B', unit_scale = True, leave = True) as pbar:
                    while True:
                        if resp.content.at_eof():
                            pbar.close()
                            break
                        chunk = await resp.content.read(self.chunk_size)
                        await f.write(chunk)
                        pbar.update(len(chunk))

    def merge_file(self, temp_path, filename):
        files = sorted(os.listdir(temp_path))
        filename = self.filepath + filename

        with open(filename, 'ab') as outfile:
            for file in files:
                with open(f'{temp_path}/{file}', 'rb') as f:
                    outfile.write(f.read())

        os.system(f'rm -rf "{temp_path}"')
 
    async def download(self, url):
        parser = LinkParser(self.session)
        direct_link = await parser.parse_mediafire(url)
        file_info = await self.get_file_info(direct_link)
        filename = re.search(r'filename\=\"(.*?)\"', file_info.get('Content-Disposition'))[1]
        file_size = int(file_info.get('Content-Length'))
        chunk_size = file_size // self.chunk
        start, end = 0, chunk_size
        
        temp_path = f'temp/{filename}'
        os.makedirs(temp_path, exist_ok = True)
        async with asyncio.TaskGroup() as tg:
            for idx in range(self.chunk):
                if idx == self.chunk - 1:
                    tg.create_task(self.get_section(f'{temp_path}/part-{idx}.tmp', direct_link, {'Range': f"bytes={start}-{file_size}"}))
                    break
            
                tg.create_task(self.get_section(f'{temp_path}/part-{idx}.tmp', direct_link, {'Range': f"bytes={start}-{end}"}))
                start = end + 1
                end += chunk_size + 1
        
        self.merge_file(temp_path, filename)

    async def batch_download(self, urls):
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                tg.create_task(self.download(url))
        await self.close_session()

    async def close_session(self):
        await self.session.close()