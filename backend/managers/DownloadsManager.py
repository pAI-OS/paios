import asyncio
import aiohttp
import aioftp
import os
from urllib.parse import urlparse
from pathlib import Path
from paths import data_dir

class DownloadsManager:
    def __init__(self, max_concurrent_downloads=5):
        self.max_concurrent_downloads = max_concurrent_downloads
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)
        self.downloads = {}

    def _is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ('http', 'https', 'ftp')

    def _is_valid_path(self, path):
        return Path(path).resolve().is_relative_to(data_dir)

    async def download_file_http(self, url, dest, start_byte=0):
        headers = {'Range': f'bytes={start_byte}-'} if start_byte > 0 else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status in [200, 206]:
                    total_size = int(response.headers.get('Content-Length', 0)) + start_byte
                    self.downloads[url]["total_size"] = total_size
                    mode = 'ab' if start_byte > 0 else 'wb'
                    with open(dest, mode) as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            self.downloads[url]["downloaded"] += len(chunk)
                            self.downloads[url]["progress"] = round(
                                (self.downloads[url]["downloaded"] / self.downloads[url]["total_size"]) * 100, 2
                            )
                else:
                    raise Exception(f"Failed to download {url}")

    async def download_file_ftp(self, url, dest, start_byte=0):
        parsed_url = urlparse(url)
        async with aioftp.Client.context(parsed_url.hostname, parsed_url.port or 21, parsed_url.username, parsed_url.password) as client:
            async with client.download_stream(parsed_url.path) as stream:
                total_size = await client.stat(parsed_url.path)
                total_size = total_size['size']
                self.downloads[url]["total_size"] = total_size
                mode = 'ab' if start_byte > 0 else 'wb'
                with open(dest, mode) as f:
                    async for chunk in stream.iter_by_block(1024):
                        f.write(chunk)
                        self.downloads[url]["downloaded"] += len(chunk)
                        self.downloads[url]["progress"] = round(
                            (self.downloads[url]["downloaded"] / self.downloads[url]["total_size"]) * 100, 2
                        )

    async def download_file(self, url, dest, start_byte=0):
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        if not self._is_valid_path(dest):
            raise ValueError(f"Invalid destination path: {dest}")

        parsed_url = urlparse(url)
        if parsed_url.scheme in ('http', 'https'):
            await self.download_file_http(url, dest, start_byte)
        elif parsed_url.scheme == 'ftp':
            await self.download_file_ftp(url, dest, start_byte)
        else:
            raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")

    async def start_download(self, url, dest):
        async with self.semaphore:
            download_task = asyncio.create_task(self.download_file(url, dest))
            self.downloads[url] = {
                "task": download_task,
                "dest": dest,
                "paused": False,
                "start_byte": 0,
                "total_size": 0,
                "downloaded": 0,
                "progress": 0.0
            }
            await download_task

    def pause_download(self, url):
        if url in self.downloads and not self.downloads[url]["paused"]:
            self.downloads[url]["task"].cancel()
            self.downloads[url]["paused"] = True
            self.downloads[url]["start_byte"] = os.path.getsize(self.downloads[url]["dest"])

    async def resume_download(self, url):
        if url in self.downloads and self.downloads[url]["paused"]:
            dest = self.downloads[url]["dest"]
            start_byte = self.downloads[url]["start_byte"]
            download_task = asyncio.create_task(self.download_file(url, dest, start_byte))
            self.downloads[url]["task"] = download_task
            self.downloads[url]["paused"] = False
            await download_task

    def stop_download(self, url):
        if url in self.downloads:
            self.downloads[url]["task"].cancel()
            del self.downloads[url]

    def get_stats(self, url):
        if url in self.downloads:
            return {
                "total_size": self.downloads[url]["total_size"],
                "downloaded": self.downloads[url]["downloaded"],
                "progress": self.downloads[url]["progress"],
                "status": "paused" if self.downloads[url]["paused"] else "downloading"
            }
        return {"error": "Download not found"}

    async def shutdown(self):
        tasks = [download["task"] for download in self.downloads.values()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    manager = DownloadsManager()
    try:
        asyncio.run(manager.start_download('http://example.com/largefile.zip', 'largefile.zip'))
    except KeyboardInterrupt:
        asyncio.run(manager.shutdown())