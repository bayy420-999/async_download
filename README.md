# Python module for downloading file asynchronously 

## Installation 

* Download project 
  ```console
  git clone https://github.com/bayy420-999/async_download.git
  ```

* Move to project folder 
  ```console
  cd async_download
  ```

* Install packages
  ```console
  pip install .
  ```

## Usage 

### Example
* Basic example
  ```py
  import asyncio # You should importing asyncio package
  from async_download.downloader import Downloader # Importing module

  async def main():
      URLS = ['mediafire url 1'
              'mediafire url 2'] # store mediafire link in any iterable object (list, tuple, etc)

      downloader = Downloader() # Making Downloader instance
      await downloader.batch_download(URLS) # Pass iterable here

  if __name__ == '__main__':
      asyncio.run(main())
  ```

* Read urls from txt file
  ```py
  import asyncio # You should importing asyncio package
  from async_download.downloader import Downloader # Importing module

  async def main():
      with open('urls.txt', 'r') as f:
          URLS = f.read().split() # Splitting url by newline

      downloader = Downloader() # Making Downloader instance
      await downloader.batch_download(URLS) # Pass iterable here

  if __name__ == '__main__':
      asyncio.run(main())
  ```

* Parsing mediafire url
  ```py
  import asyncio # You should importing asyncio
  from async_download.downloader import Downloader # Importing module

  async def main():
      URLS = ['mediafire url 1'
              'mediafire url 2'] # store mediafire link in any iterable object (list, tuple, etc)

      downloader = Downloader()
      result = await asyncio.gather(*[downloader.get_file_info(url, get_chunk_info = False) for url in URLS])
      await downloader.close_session()

      for data in result:
          print(data.download_url)

  if __name__ == '__main__':
      asyncio.run(main())
  ```
