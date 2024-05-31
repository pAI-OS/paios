from uuid import uuid4
import hashlib
import os
import aiohttp
import aioftp
import asyncio
import aiofiles
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse
from backend.paths import data_dir, downloads_dir
import time

class DownloadStatus(Enum):
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALID = "invalid"

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

    async def _calculate_hash(self, file_path, hash_type):
        hash_func = getattr(hashlib, hash_type)()
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(4096)
                if not chunk:
                    break
                hash_func.update(chunk)
        return hash_func.hexdigest()

    async def retrieve_all_downloads(self, limit=None, retention_period=600):
        current_time = time.time()
        all_downloads = []

        for download_id, download in list(self.downloads.items()):
            if "finish_time" in download and (current_time - download["finish_time"] > retention_period):
                del self.downloads[download_id]
            else:
                keys_to_include = ["download_id", "source_url", "target_filename", "target_directory", "total_size", "downloaded", "progress", "start_time", "finish_time", "download_rate"]
                download["download_rate"] = self._calculate_download_rate(download)
                filtered_dict = {k: download[k] for k in keys_to_include if k in download}
                filtered_dict["download_id"] = download_id
                filtered_dict["status"] = download["status"].value
                all_downloads.append(filtered_dict)

        return all_downloads if limit is None else all_downloads[:limit]

    def _calculate_download_rate(self, download):
        elapsed_time = time.time() - download["start_time"]
        if elapsed_time > 0:
            return download["downloaded"] / elapsed_time
        return 0

    async def download_file_http(self, download_id):
        download = self.downloads[download_id]
        source_url = download["source_url"]
        start_byte = download["start_byte"]

        headers = {'Range': f'bytes={start_byte}-'} if start_byte > 0 else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(source_url, headers=headers) as response:
                if response.status in [200, 206]:
                    total_size = int(response.headers.get('Content-Length', -1)) + start_byte
                    download["total_size"] = total_size

                    # Determine filename
                    content_disposition = response.headers.get('Content-Disposition')
                    if content_disposition:
                        filename = content_disposition.split('filename=')[-1].strip('"')
                    else:
                        filename = Path(source_url).name or download_id
                    download["target_filename"] = filename

                    temp_file = self.downloads_dir / filename
                    download["temp_file"] = temp_file

                    mode = 'ab' if start_byte > 0 else 'wb'
                    with open(temp_file, mode) as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            download["downloaded"] += len(chunk)
                            if download["total_size"] > 0:
                                download["progress"] = round(
                                    (download["downloaded"] / download["total_size"]) * 100, 2
                                )
                            else:
                                download["progress"] = -1
                else:
                    raise Exception(f"Failed to download {source_url}")

    async def download_file_ftp(self, download_id):
        download = self.downloads[download_id]
        source_url = download["source_url"]
        start_byte = download["start_byte"]

        parsed_url = urlparse(source_url)
        async with aioftp.Client.context(parsed_url.hostname, parsed_url.port or 21, parsed_url.username, parsed_url.password) as client:
            async with client.download_stream(parsed_url.path, offset=start_byte) as stream:
                total_size = await client.stat(parsed_url.path)
                total_size = total_size['size']
                download["total_size"] = total_size

                # Determine filename
                filename = Path(source_url).name or download_id
                download["target_filename"] = filename

                temp_file = self.downloads_dir / filename
                download["temp_file"] = temp_file

                mode = 'ab' if start_byte > 0 else 'wb'
                with open(temp_file, mode) as f:
                    async for chunk in stream.iter_by_block(1024):
                        f.write(chunk)
                        download["downloaded"] += len(chunk)
                        download["progress"] = round(
                            (download["downloaded"] / download["total_size"]) * 100, 2
                        )

    async def download_file(self, download_id):
        download = self.downloads[download_id]
        try:
            source_url = download["source_url"]
            target_directory = download.get("target_directory")
            target_directory_path = download["target_directory_path"]
            start_byte = download["start_byte"]
            hash_type = download.get("hash_type")
            expected_hash = download.get("expected_hash")

            if not self._is_valid_url(source_url):
                raise ValueError(f"Invalid URL: {source_url}")
            if target_directory and not self._is_valid_path(target_directory_path):
                raise ValueError(f"Invalid destination path: {target_directory_path}")

            if target_directory:
                target_directory_path.mkdir(parents=True, exist_ok=True)
                target_file_path = Path(target_directory_path) / download["target_filename"]
                if target_file_path.exists():
                    raise FileExistsError(f"Destination file already exists: {target_file_path}")

            parsed_url = urlparse(source_url)
            if parsed_url.scheme in ('http', 'https'):
                await self.download_file_http(download_id)
            elif parsed_url.scheme == 'ftp':
                await self.download_file_ftp(download_id)
            else:
                raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
            
            download["finish_time"] = time.time()
            download["status"] = DownloadStatus.PROCESSING

            if hash_type and expected_hash:
                actual_hash = await self._calculate_hash(download["temp_file"], hash_type)
                if actual_hash != expected_hash:
                    download["status"] = DownloadStatus.INVALID
                    raise ValueError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")

            if target_directory:
                # Check again before renaming to minimize race condition
                if target_file_path.exists():
                    raise FileExistsError(f"Destination file already exists: {target_file_path}")
                download["temp_file"].rename(target_file_path)
            
            download["status"] = DownloadStatus.COMPLETED

        except Exception as e:
            download["status"] = DownloadStatus.FAILED
            download["error"] = str(e)
            raise

    async def queue_downloads(self, downloads: list):
        download_ids = []
        async with self.semaphore:
            for download in downloads:
                download_id = str(uuid4())
                target_directory = download.get('target_directory')
                if target_directory:
                    target_directory_path = data_dir / Path(target_directory)
                else:
                    target_directory_path = self.downloads_dir

                self.downloads[download_id] = {
                    "source_url": download.get('source_url'),
                    "target_filename": download.get('target_filename'),
                    "target_directory": target_directory,
                    "target_directory_path": target_directory_path,
                    "status": DownloadStatus.DOWNLOADING,
                    "start_byte": 0,
                    "total_size": 0,
                    "downloaded": 0,
                    "progress": 0.0,
                    "start_time": time.time(),
                    "hash_type": download.get('hash_type'),
                    "expected_hash": download.get('expected_hash')
                }

                download_task = asyncio.create_task(self.download_file(download_id))
                self.downloads[download_id]["task"] = download_task
                download_ids.append(download_id)
            
            # Await all tasks to ensure exceptions are handled
            await asyncio.gather(*[self.downloads[download_id]["task"] for download_id in download_ids], return_exceptions=True)
        return download_ids

    async def pause_download(self, download_id):
        if download_id in self.downloads and not self.downloads[download_id]["paused"]:
            self.downloads[download_id]["task"].cancel()
            self.downloads[download_id]["status"] = DownloadStatus.PAUSED
            self.downloads[download_id]["start_byte"] = os.path.getsize(self.downloads[download_id]["target_file"])

    async def resume_download(self, download_id):
        if download_id in self.downloads and self.downloads[download_id]["status"] == DownloadStatus.PAUSED:
            source_url = self.downloads[download_id]["source_url"]
            target_file = self.downloads[download_id]["target_file"]
            start_byte = self.downloads[download_id]["start_byte"]
            download_task = asyncio.create_task(self.download_file(download_id, source_url, target_file, start_byte))
            self.downloads[download_id]["task"] = download_task
            self.downloads[download_id]["paused"] = False
            self.downloads[download_id]["start_time"] = time.time()  # Reset start time for resumed download
            await download_task

    async def delete_download(self, download_id):
        if download_id in self.downloads:
            self.downloads[download_id]["task"].cancel()
            target_file = Path(self.downloads[download_id]["target_file"])
            if target_file.exists():
                target_file.unlink()
            del self.downloads[download_id]

    async def shutdown(self):
        tasks = [download["task"] for download in self.downloads.values()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
