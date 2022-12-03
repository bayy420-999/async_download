import re

class LinkParser:
    def __init__(self, session):
        self.session = session

    async def parse_mediafire(self, url):
        async with self.session.get(url) as resp:
            assert resp.status == 200, 'Link not working'
            html = await resp.text()
            return re.search(r'href\=\"(.*?)\"\s+id\=\"downloadButton\"', html)[1]