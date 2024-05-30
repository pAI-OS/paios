from uuid import uuid4
import hashlib
import os
import aiohttp
import aioftp
import asyncio
from pathlib import Path
from urllib.parse import urlparse
from backend.paths import data_dir, downloads_dir
import time

class DownloadsManager:
    def __init__(self, max_concurrent_downloads=5):
        self.max_concurrent_downloads = max_concurrent_downloads
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)
        self.downloads = {}
        self.downloads_dir = downloads_dir
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

    def _is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ('http', 'https', 'ftp')

    def _is_valid_path(self, path):
        return Path(path).resolve().is_relative_to(data_dir)

    def _calculate_hash(self, file_path, hash_type):
        hash_func = getattr(hashlib, hash_type)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    async def retrieve_all_downloads(self, limit=None):
        all_downloads = [
            {
                "id": download_id,
                "source_url": download["source_url"],
                "target_file": download["target_file"],
                "target_dir": download["target_dir"],
                "total_size": download["total_size"],
                "downloaded": download["downloaded"],
                "progress": download["progress"],
                "status": "paused" if download["paused"] else "downloading",
                "download_rate": self._calculate_download_rate(download)
            }
            for download_id, download in self.downloads.items()
        ]
        return all_downloads if limit is None else all_downloads[:limit]

    def _calculate_download_rate(self, download):
        elapsed_time = time.time() - download["start_time"]
        if elapsed_time > 0:
            return download["downloaded"] / elapsed_time
        return 0

    async def download_file_http(self, id, url, temp_dest, start_byte=0):
        headers = {'Range': f'bytes={start_byte}-'} if start_byte > 0 else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status in [200, 206]:
                    total_size = int(response.headers.get('Content-Length', 0)) + start_byte
                    self.downloads[id]["total_size"] = total_size
                    mode = 'ab' if start_byte > 0 else 'wb'
                    with open(temp_dest, mode) as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            self.downloads[id]["downloaded"] += len(chunk)
                            self.downloads[id]["progress"] = round(
                                (self.downloads[id]["downloaded"] / self.downloads[id]["total_size"]) * 100, 2
                            )
                else:
                    raise Exception(f"Failed to download {url}")

    async def download_file_ftp(self, id, url, temp_dest, start_byte=0):
        parsed_url = urlparse(url)
        async with aioftp.Client.context(parsed_url.hostname, parsed_url.port or 21, parsed_url.username, parsed_url.password) as client:
            async with client.download_stream(parsed_url.path) as stream:
                total_size = await client.stat(parsed_url.path)
                total_size = total_size['size']
                self.downloads[id]["total_size"] = total_size
                mode = 'ab' if start_byte > 0 else 'wb'
                with open(temp_dest, mode) as f:
                    async for chunk in stream.iter_by_block(1024):
                        f.write(chunk)
                        self.downloads[id]["downloaded"] += len(chunk)
                        self.downloads[id]["progress"] = round(
                            (self.downloads[id]["downloaded"] / self.downloads[id]["total_size"]) * 100, 2
                        )

    async def download_file(self, id, url, dest, start_byte=0, hash_type=None, expected_hash=None):
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        if not self._is_valid_path(dest):
            raise ValueError(f"Invalid destination path: {dest}")

        temp_dest = self.downloads_dir / Path(dest).name

        parsed_url = urlparse(url)
        if parsed_url.scheme in ('http', 'https'):
            await self.download_file_http(id, url, temp_dest, start_byte)
        elif parsed_url.scheme == 'ftp':
            await self.download_file_ftp(id, url, temp_dest, start_byte)
        else:
            raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")

        if hash_type and expected_hash:
            actual_hash = self._calculate_hash(temp_dest, hash_type)
            if actual_hash != expected_hash:
                raise ValueError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")

        final_dest = Path(dest)
        if final_dest.exists():
            raise FileExistsError(f"Destination file already exists: {final_dest}")

        temp_dest.rename(final_dest)

    async def start_download(self, source_url, target_file=None, target_dir=None, hash_type=None, expected_hash=None):
        async with self.semaphore:
            id = str(uuid4())
            if target_dir:
                target_dir_path = data_dir / Path(target_dir)
                target_dir_path.mkdir(parents=True, exist_ok=True)
            else:
                target_dir_path = self.downloads_dir

            filename = target_file or Path(source_url).name
            dest = target_dir_path / filename

            # Check if the destination file already exists
            if dest.exists():
                raise FileExistsError(f"Destination file already exists: {filename}")

            download_task = asyncio.create_task(self.download_file(id, source_url, dest, hash_type=hash_type, expected_hash=expected_hash))
            self.downloads[id] = {
                "task": download_task,
                "source_url": source_url,
                "target_file": str(dest),
                "target_dir": str(target_dir_path),
                "paused": False,
                "start_byte": 0,
                "total_size": 0,
                "downloaded": 0,
                "progress": 0.0,
                "start_time": time.time()
            }
            
            return id

    def pause_download(self, id):
        if id in self.downloads and not self.downloads[id]["paused"]:
            self.downloads[id]["task"].cancel()
            self.downloads[id]["paused"] = True
            self.downloads[id]["start_byte"] = os.path.getsize(self.downloads[id]["target_file"])

    async def resume_download(self, id):
        if id in self.downloads and self.downloads[id]["paused"]:
            source_url = self.downloads[id]["source_url"]
            target_file = self.downloads[id]["target_file"]
            start_byte = self.downloads[id]["start_byte"]
            download_task = asyncio.create_task(self.download_file(id, source_url, target_file, start_byte))
            self.downloads[id]["task"] = download_task
            self.downloads[id]["paused"] = False
            self.downloads[id]["start_time"] = time.time()  # Reset start time for resumed download
            await download_task

    async def delete_download(self, id):
        if id in self.downloads:
            self.downloads[id]["task"].cancel()
            target_file = Path(self.downloads[id]["target_file"])
            if target_file.exists():
                target_file.unlink()
            del self.downloads[id]

    def get_stats(self, id):
        if id in self.downloads:
            return {
                "source_url": self.downloads[id]["source_url"],
                "target_file": self.downloads[id]["target_file"],
                "target_dir": self.downloads[id]["target_dir"],
                "total_size": self.downloads[id]["total_size"],
                "downloaded": self.downloads[id]["downloaded"],
                "progress": self.downloads[id]["progress"],
                "status": "paused" if self.downloads[id]["paused"] else "downloading",
                "download_rate": self._calculate_download_rate(self.downloads[id])
            }
        return {"error": "Download not found"}

    async def shutdown(self):
        tasks = [download["task"] for download in self.downloads.values()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
