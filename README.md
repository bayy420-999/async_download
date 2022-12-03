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

## Usage 

* LinkParser class 
  Method:
  |Method|Params|Return|
  |------|------|------|
  |`__init__()`|`session`: `aiohttp.ClientSession()`|`None`|
  |`parse_mediafire()`|`url`: Mediafire url|Mediafire direct download link|
  
* Downloader class 
  Method:
  |Method|Params|Return|
  |------|------|------|
  |`__init__()`|`filepath` : (str) Path where files stored|`None`|
  |            |`download_limit` : (int) How many download can be performed simultaneously||
  |            |`chunk` : (int) How many chunks for 1 files||
  |            |`chunk_size` : (int) Read n sized chunk||
  |`get_file_info()`|`url` : (str) Mediafire direct download link|File info (headers)|
  |`get_section()`|`filename` : (str) Name of the part-file that will saved|`None`|
  |               |`url` : (str) Mediafire direct download link||
  |               | `headers` : (dict[str, str]) Range headers||


### Example
* Basic example
  ```py
  import asyncio # You should importing asyncio package
  from api.download import Downloader # Importing module

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
  from api.download import Downloader # Importing module

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
  import asyncio, aiohttp # You should importing asyncio and aiohttp packages
  from api.link_parser import LinkParser # Importing module

  async def main():
      URLS = ['mediafire url 1'
              'mediafire url 2'] # store mediafire link in any iterable object (list, tuple, etc)

      session = aiohttp.ClientSession() # Making aiohttp session
      parser = LinkParser(session) # Making parser by passing aiohttp session

      direct_links = await asyncio.gather(*[parser.parse_mediafire(url) for url in URLS]) # gather all tasks with asyncio.gather()
      session.close() # Closing aiohttp session

      for link in direct_links:
          print(link) # Print result to terminal

  if __name__ == '__main__':
      asyncio.run(main())
  ```
