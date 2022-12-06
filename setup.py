from distutils.core import setup

setup(
    name             = 'Async Download',
    version          = '0.1.0',
    author           = 'Bayu Aji',
    author_email     = 'getkilla5@gmail.com',
    packages         = ['async_download'],
    description      = 'Download files asynchronously',
    install_requires = [
        'aiofiles >= 22.1.0',
        'aiohttp  >= 3.8.3',
        'pydantic >= 1.10.2',
        'inquirer >= 3.0.0'
    ]
)