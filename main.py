import asyncio
from api.downloader import Downloader

async def main():
    URLS = ['https://www.mediafire.com/file/2r67agc22kkj4qo/Coser%40usejan%E8%93%9D%E8%93%9D_Vol.006.rar/file',
           'https://www.mediafire.com/file/ewd3gmg6fgohsqd/Coser%2540%25E6%25B0%25B4%25E6%25B7%25BCAqua_Vol.133.rar/file']
    downloader = Downloader()
    resp = await downloader.batch_download(URLS)
    

if __name__ == '__main__':
    asyncio.run(main())