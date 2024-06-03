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
        downloads_dir.mkdir(parents=True, exist_ok=True)

    def _is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ('http', 'https', 'ftp')

    def _is_valid_path(self, path):
        resolved_path = Path(path).resolve()
        return resolved_path.is_relative_to(data_dir) and resolved_path.exists()

    def _is_duplicate_download(self, source_url, file_name, target_directory):
        for existing_download in self.downloads.values():
            if (existing_download["source_url"] == source_url and
                existing_download["file_name"] == file_name and
                existing_download["target_directory"] == target_directory):
                return True
        return False

    def _is_file_already_downloading(self, current_download):
        for existing_download in self.downloads.values():
            if existing_download is current_download:
                continue
            if (existing_download["file_name"] == current_download["file_name"] and
                existing_download["target_directory"] == current_download["target_directory"] and
                existing_download["status"] in {DownloadStatus.DOWNLOADING, DownloadStatus.PAUSED}):
                return True
        return False

    async def _calculate_hash(self, file_path, hash_type):
        hash_func = getattr(hashlib, hash_type)()
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(4096)
                if not chunk:
                    break
                hash_func.update(chunk)
        return hash_func.hexdigest()

    async def retrieve_downloads(self, limit=100, offset=0):
        current_time = time.time()
        all_downloads = []

        for download_id, download in list(self.downloads.items()):
            if "finish_time" in download and (current_time - download["finish_time"] > 600):
                del self.downloads[download_id]
            else:
                keys_to_include = ["download_id", "source_url", "file_name", "target_directory", "total_size", "downloaded", "progress", "start_time", "finish_time", "transfer_rate"]
                download["transfer_rate"] = self._calculate_transfer_rate(download)
                filtered_dict = {k: download[k] for k in keys_to_include if k in download}
                filtered_dict["download_id"] = download_id
                filtered_dict["status"] = download["status"].value
                all_downloads.append(filtered_dict)

        total_count = len(all_downloads)
        paginated_downloads = all_downloads[offset:offset + limit]
        return paginated_downloads, total_count

    def _calculate_transfer_rate(self, download):
        elapsed_time = time.time() - download["start_time"]
        if elapsed_time > 0:
            return download["downloaded"] / elapsed_time
        return 0

    async def download_file_http(self, id):
        download = self.downloads[id]
        source_url = download["source_url"]
        start_byte = download["start_byte"]

        headers = {'Range': f'bytes={start_byte}-'} if start_byte > 0 else {}
        print(f"HTTP download {id} started ({source_url})")
        async with aiohttp.ClientSession() as session:
            async with session.get(source_url, headers=headers) as response:
                if response.status in [200, 206]:
                    total_size = int(response.headers.get('Content-Length', -1)) + start_byte
                    download["total_size"] = total_size

                    # If file_name not specified, get it from Content-Disposition headers, URL, or default to id
                    if not download.get("file_name"):
                        content_disposition = response.headers.get('Content-Disposition')
                        if content_disposition:
                            resolved_file_name = content_disposition.split('filename=')[-1].strip('"')
                        else:
                            resolved_file_name = Path(source_url).name or id
                        download["file_name"] = resolved_file_name

                    temp_file = downloads_dir / download.get("file_name")
                    if temp_file.exists():
                        raise FileExistsError(f"Temporary file already exists: {temp_file}")
                    download["temp_file"] = temp_file

                    print("temp_file: ", temp_file)

                    # Check if the target file is being used by an active or paused download
                    if self._is_file_already_downloading(download):
                        raise ValueError(f"File {download.get('file_name')} is currently being downloaded or paused")

                    mode = 'ab' if start_byte > 0 else 'wb'
                    try:
                        with open(temp_file, mode) as f:
                            while True:
                                chunk_start_time = time.time()
                                chunk = await response.content.read(1024)
                                chunk_end_time = time.time()
                                if not chunk:
                                    break
                                f.write(chunk)
                                download["downloaded"] += len(chunk)
                                chunk_time = chunk_end_time - chunk_start_time
                                if chunk_time > 0:
                                    if download["status"] != DownloadStatus.PAUSED:
                                        download["transfer_rate"] = len(chunk) / chunk_time
                                if download["total_size"] > 0:
                                    download["progress"] = round(
                                        (download["downloaded"] / download["total_size"]) * 100, 2
                                    )
                                else:
                                    download["progress"] = -1
                    except asyncio.CancelledError:
                        # Handle the cancellation here
                        download["status"] = DownloadStatus.PAUSED
                        raise
                else:
                    raise Exception(f"Failed to download {source_url}")

    async def download_file_ftp(self, id):
        download = self.downloads[id]
        source_url = download["source_url"]
        start_byte = download["start_byte"]

        parsed_url = urlparse(source_url)
        async with aioftp.Client.context(parsed_url.hostname, parsed_url.port or 21, parsed_url.username, parsed_url.password) as client:
            async with client.download_stream(parsed_url.path, offset=start_byte) as stream:
                total_size = await client.stat(parsed_url.path)
                total_size = total_size['size']
                download["total_size"] = total_size

                if not download.get("file_name"):
                    resolved_file_name = Path(source_url).name or id
                    download["file_name"] = resolved_file_name

                temp_file = downloads_dir / download.get("file_name")
                download["temp_file"] = temp_file

                # Check if the target file is being used by an active or paused download
                if self._is_file_already_downloading(download.get('file_name'), download.get('target_directory')):
                    raise ValueError(f"File {download.get('file_name')} is currently being downloaded or paused")

                mode = 'ab' if start_byte > 0 else 'wb'
                try:
                    with open(temp_file, mode) as f:
                        while True:
                            chunk_start_time = time.time()
                            chunk = await stream.read(1024)
                            chunk_end_time = time.time()
                            if not chunk:
                                break
                            f.write(chunk)
                            download["downloaded"] += len(chunk)
                            chunk_time = chunk_end_time - chunk_start_time
                            if chunk_time > 0:
                                if download["status"] != DownloadStatus.PAUSED:
                                    download["transfer_rate"] = len(chunk) / chunk_time
                            download["progress"] = round(
                                (download["downloaded"] / download["total_size"]) * 100, 2
                            )
                except asyncio.CancelledError:
                    # Handle the cancellation here
                    download["status"] = DownloadStatus.PAUSED
                    raise

    async def download_file(self, id):
        download = self.downloads[id]
        try:
            source_url = download["source_url"]
            target_directory = download.get("target_directory")
            hash_type = download.get("hash_type")
            expected_hash = download.get("expected_hash")

            if not self._is_valid_url(source_url):
                raise ValueError(f"Invalid URL: {source_url}")
 
            # Ensure the target_directory (if specified) is valid and exists
            if target_directory:
                target_directory_path = data_dir / Path(target_directory)
            else:
                target_directory_path = downloads_dir
            target_directory_path.mkdir(parents=True, exist_ok=True)
            if not self._is_valid_path(target_directory_path):
                raise ValueError(f"Invalid destination path: {target_directory_path}")

            if download.get('file_name'):
                if (target_directory_path / download.get("file_name")).exists():
                    raise FileExistsError(f"Destination file already exists: {target_directory_path / download.get('file_name')}")

            parsed_url = urlparse(source_url)
            if parsed_url.scheme in ('http', 'https'):
                await self.download_file_http(id)
            elif parsed_url.scheme == 'ftp':
                await self.download_file_ftp(id)
            else:
                raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
            
            download["finish_time"] = time.time()
            download["status"] = DownloadStatus.PROCESSING

            if hash_type and expected_hash:
                actual_hash = await self._calculate_hash(download["temp_file"], hash_type)
                if actual_hash != expected_hash:
                    download["status"] = DownloadStatus.INVALID
                    raise ValueError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")

            # If a target_directory has been specified, we need to move the file out of the general downloads directory
            if target_directory:
                file_path = target_directory_path / download.get('file_name')
                if file_path.exists():
                    raise FileExistsError(f"Destination file already exists: {file_path}")
                download["temp_file"].rename(file_path)
            del(download["temp_file"])

            download["status"] = DownloadStatus.COMPLETED

        except asyncio.CancelledError:
            # CancelledError is expected when the download is paused or about to be deleted
            return  # Ensure the function exits on cancellation

        # TODO: This may catch download errors and send them to the client instead of the logs
        except Exception as e:
            download["status"] = DownloadStatus.FAILED
            download["error"] = str(e)
            raise

    def _handle_task_exception(self, task, download):
        try:
            task.result()
        except Exception as e:
            download["status"] = DownloadStatus.FAILED
            download["error"] = str(e)
            print(f"Error in download {download['source_url']}: {e}")

    async def queue_downloads(self, downloads: list):
        download_ids = []
        for download in downloads:
            download_id = str(uuid4())

            self.downloads[download_id] = {
                "source_url": download.get('source_url'),
                "file_name": download.get('file_name'),
                "target_directory": download.get('target_directory'),
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
        
            # Add done callback but pass in the download along with the task object so we know what it was later
            download_task.add_done_callback(lambda t, d=self.downloads[download_id]: self._handle_task_exception(t, d))

        return download_ids

    async def pause_download(self, id):
        if id in self.downloads and not self.downloads[id]["status"] == DownloadStatus.PAUSED:
            self.downloads[id]["task"].cancel()
            self.downloads[id]["status"] = DownloadStatus.PAUSED
            if "transfer_rate" in self.downloads[id]:
                del self.downloads[id]["transfer_rate"]
            self.downloads[id]["start_byte"] = os.path.getsize(self.downloads[id]["file_path"])

    async def resume_download(self, id):
        if id in self.downloads and self.downloads[id]["status"] == DownloadStatus.PAUSED:
            download_task = asyncio.create_task(self.download_file(id))
            self.downloads[id]["task"] = download_task
            self.downloads[id]["status"] = DownloadStatus.DOWNLOADING
            self.downloads[id]["start_time"] = time.time()  # Reset start time for resumed download
            await download_task

    async def delete_download(self, id: str):
        download = self.downloads.get(id)
        if not download:
            raise ValueError(f"Download with ID {id} does not exist")

        # Cancel the download task if it's active or paused
        if download["status"] in ["downloading", "paused"]:
            download["task"].cancel()
            try:
                await download["task"]
            except asyncio.CancelledError:
                pass

        # Unlink the downloaded file if it exists
        file_path = Path(download.get("file_path", ""))
        if file_path.exists():
            file_path.unlink()

        del self.downloads[id]

    async def shutdown(self):
        tasks = [download["task"] for download in self.downloads.values()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
