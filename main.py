import asyncio
from async_download.downloader import Downloader

async def main():
    URLS = []
    downloader = Downloader()
    resp = await downloader.batch_download(URLS)
    

if __name__ == '__main__':
    asyncio.run(main())