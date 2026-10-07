import logging
import os
import time

import requests
import yt_dlp
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("video-indexer")


class VideoIndexerService:
    """Small wrapper around Azure Video Indexer."""

    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME")
        self.credential = DefaultAzureCredential()

    def get_access_token(self):
        return self.credential.get_token(
            "https://management.azure.com/.default"
        ).token

    def get_account_token(self, arm_token):
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )

        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {arm_token}"},
            json={"permissionType": "Contributor", "scope": "Account"},
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get Video Indexer token: {response.text}")

        return response.json()["accessToken"]

    def download_youtube_video(self, url, output_path="temp_video.mp4"):
        """Download the YouTube video to a temporary local file."""
        options = {
            "format": "best",
            "outtmpl": output_path,
            "quiet": False,
            "no_warnings": False,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            return output_path
        except Exception as error:
            raise Exception(f"YouTube Download Failed: {error}")

    def upload_video(self, video_path, video_name):
        """Upload the local video file to Azure Video Indexer."""
        account_token = self.get_account_token(self.get_access_token())

        url = (
            f"https://api.videoindexer.ai/{self.location}"
            f"/Accounts/{self.account_id}/Videos"
        )

        params = {
            "accessToken": account_token,
            "name": video_name,
            "privacy": "Private",
            "indexingPreset": "Default",
        }

        with open(video_path, "rb") as video_file:
            response = requests.post(url,params=params,files={"file": video_file},)

        if response.status_code != 200:
            raise Exception(f"Azure Upload Failed: {response.text}")

        return response.json()["id"]

    def wait_for_processing(self, video_id):
        """Wait until Azure Video Indexer finishes processing."""
        while True:
            account_token = self.get_account_token(self.get_access_token())

            url = (
                f"https://api.videoindexer.ai/{self.location}"
                f"/Accounts/{self.account_id}/Videos/{video_id}/Index"
            )
            response = requests.get(
                url,
                params={"accessToken": account_token},
            )
            data = response.json()
            state = data.get("state")
            if state == "Processed":
                return data
            if state == "Failed":
                raise Exception("Video Indexing Failed in Azure.")
            if state == "Quarantined":
                raise Exception("Video Quarantined (Copyright/Content Policy Violation) by Azure.")

            logger.info("Video status: %s. Waiting 30 seconds...", state)
            time.sleep(30)

    def extract_data(self, data):
        """Take transcript and OCR text out of the Video Indexer response."""
        transcript = []
        ocr_text = []

        for video in data.get("videos", []):
            insights = video.get("insights", {})

            for item in insights.get("transcript", []):
                if item.get("text"):
                    transcript.append(item["text"])

            for item in insights.get("ocr", []):
                if item.get("text"):
                    ocr_text.append(item["text"])

        return {
            "transcript": " ".join(transcript),
            "ocr_text": ocr_text,
            "video_metadata": {
                "duration": data.get("summarizedInsights", {})
                .get("duration", {})
                .get("seconds"),
                "platform": "youtube",
            },
        }
