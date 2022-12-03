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

" LinkParser class 
  Method:
  |Method|Params|
  |------|------|
  |`__init__()`|`session`: `aiohttp.ClientSession()`|
  |`parse_mediafire()`|`url`: Mediafire url|
  
* Downloader class 
  Method:
  |Method|Params|
  |------|------|
  |`__init__()`|`filepath` : (str) Path where files stored|
  |            |`download_limit` : (int) How many download can be performed simultaneously|
  |            |`chunk` : (int) How many chunks for 1 files|
  |            |`chunk_size` : (int) Read n sized chunk|
  

  
