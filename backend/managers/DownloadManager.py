import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class DownloadManager:
    def __init__(self, max_concurrent_downloads=5):
        self.max_concurrent_downloads = max_concurrent_downloads
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_downloads)
        self.downloads = {}
        self.lock = threading.Lock()

    def start_download(self, download_id, url, local_path):
        with self.lock:
            if download_id in self.downloads:
                return {"error": "Download already in progress"}, 400

            self.downloads[download_id] = {
                "url": url,
                "local_path": local_path,
                "status": "starting",
                "progress": 0,
                "size": 0,
                "downloaded": 0,
                "start_time": time.time(),
                "thread": None
            }

        future = self.executor.submit(self._download_file, download_id, url, local_path)
        with self.lock:
            self.downloads[download_id]["thread"] = future
        return {"message": "Download started"}, 200

    def _download_file(self, download_id, url, local_path):
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                self._update_download_status(download_id, "in_progress", total_size, 0)

                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            self._update_download_progress(download_id, len(chunk))

            self._update_download_status(download_id, "completed")
        except Exception as e:
            self._update_download_status(download_id, "failed", error=str(e))

    def _update_download_status(self, download_id, status, size=0, downloaded=0, error=None):
        with self.lock:
            if download_id in self.downloads:
                self.downloads[download_id].update({
                    "status": status,
                    "size": size,
                    "downloaded": downloaded,
                    "error": error
                })

    def _update_download_progress(self, download_id, bytes_downloaded):
        with self.lock:
            if download_id in self.downloads:
                self.downloads[download_id]["downloaded"] += bytes_downloaded
                self.downloads[download_id]["progress"] = round(
                    (self.downloads[download_id]["downloaded"] / self.downloads[download_id]["size"]) * 100, 2
                )

    def stop_download(self, download_id):
        with self.lock:
            if download_id in self.downloads and self.downloads[download_id]["status"] == "in_progress":
                self.downloads[download_id]["status"] = "stopping"
                self.downloads[download_id]["thread"].cancel()
                return {"message": "Download stopping"}, 200
            return {"error": "Download not in progress"}, 400

    def get_download_status(self, download_id):
        with self.lock:
            return self.downloads.get(download_id, {"error": "Download not found"})


# Example usage
if __name__ == "__main__":
    manager = DownloadManager()
    manager.start_download("example", "http://example.com/largefile.zip", "largefile.zip")
