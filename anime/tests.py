from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Anime, Episode, Genre


class _MockTelegramResponse:
	def __init__(self, status_code=200, headers=None, chunks=None):
		self.status_code = status_code
		self.headers = headers or {}
		self._chunks = chunks or [b"data"]

	def iter_content(self, chunk_size=1024 * 1024):
		for chunk in self._chunks:
			yield chunk


class EpisodeStreamTests(TestCase):
	def setUp(self):
		self.genre = Genre.objects.create(name="Action", slug="action")
		self.anime = Anime.objects.create(
			title="Test Anime",
			description="desc",
			release_year=2024,
			rating=8.5,
		)
		self.anime.genres.add(self.genre)

		self.episode = Episode.objects.create(
			anime=self.anime,
			episode_number=1,
			telegram_file_id="test-file-id",
		)

	@patch("anime.views.requests.get")
	@patch("anime.views.get_telegram_file_url")
	def test_episode_stream_full_response(self, mock_get_file_url, mock_requests_get):
		mock_get_file_url.return_value = "https://telegram.local/file.mp4"
		mock_requests_get.return_value = _MockTelegramResponse(
			status_code=200,
			headers={
				"Content-Type": "video/mp4",
				"Content-Length": "4",
			},
			chunks=[b"test"],
		)

		response = self.client.get(reverse("episode_stream", args=[self.episode.id]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "video/mp4")
		self.assertEqual(response["Content-Length"], "4")
		self.assertEqual(response["Accept-Ranges"], "bytes")

	@patch("anime.views.requests.get")
	@patch("anime.views.get_telegram_file_url")
	def test_episode_stream_range_response(self, mock_get_file_url, mock_requests_get):
		mock_get_file_url.return_value = "https://telegram.local/file.mp4"
		mock_requests_get.return_value = _MockTelegramResponse(
			status_code=206,
			headers={
				"Content-Type": "video/mp4",
				"Content-Range": "bytes 0-3/10",
				"Content-Length": "4",
				"Accept-Ranges": "bytes",
			},
			chunks=[b"test"],
		)

		response = self.client.get(
			reverse("episode_stream", args=[self.episode.id]),
			HTTP_RANGE="bytes=0-3",
		)

		self.assertEqual(response.status_code, 206)
		self.assertEqual(response["Content-Range"], "bytes 0-3/10")
		self.assertEqual(response["Accept-Ranges"], "bytes")

		_, kwargs = mock_requests_get.call_args
		self.assertEqual(kwargs["headers"].get("Range"), "bytes=0-3")

	@patch("anime.views.requests.get")
	@patch("anime.views.get_telegram_file_url")
	def test_episode_stream_upstream_failure_redirects(self, mock_get_file_url, mock_requests_get):
		mock_get_file_url.return_value = "https://telegram.local/file.mp4"
		mock_requests_get.return_value = _MockTelegramResponse(status_code=500)

		response = self.client.get(reverse("episode_stream", args=[self.episode.id]))

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse("detail", args=[self.anime.id]), response.url)
