"""Tests for queue management features (manual import and grab)."""

import pytest
from unittest.mock import AsyncMock, patch
from arr_suite_mcp.clients.sonarr import SonarrClient
from arr_suite_mcp.clients.radarr import RadarrClient


@pytest.fixture
def sonarr_client():
    """Create a Sonarr client with mocked request."""
    client = SonarrClient(base_url="http://localhost:8989", api_key="test-key")
    client._request = AsyncMock()
    return client


@pytest.fixture
def radarr_client():
    """Create a Radarr client with mocked request."""
    client = RadarrClient(base_url="http://localhost:7878", api_key="test-key")
    client._request = AsyncMock()
    return client


class TestSonarrManualImport:
    """Test Sonarr manual import methods."""

    @pytest.mark.asyncio
    async def test_get_manual_import_default(self, sonarr_client):
        """Test get_manual_import with default params."""
        sonarr_client._request.return_value = [{"path": "/downloads/file.mkv"}]
        result = await sonarr_client.get_manual_import()

        sonarr_client._request.assert_called_once_with(
            "GET", "manualimport", params={"filterExistingFiles": True}
        )
        assert result == [{"path": "/downloads/file.mkv"}]

    @pytest.mark.asyncio
    async def test_get_manual_import_with_download_id(self, sonarr_client):
        """Test get_manual_import with download_id."""
        sonarr_client._request.return_value = []
        await sonarr_client.get_manual_import(download_id="abc123")

        sonarr_client._request.assert_called_once_with(
            "GET", "manualimport",
            params={"filterExistingFiles": True, "downloadId": "abc123"}
        )

    @pytest.mark.asyncio
    async def test_get_manual_import_with_series_and_season(self, sonarr_client):
        """Test get_manual_import with series_id and season_number."""
        sonarr_client._request.return_value = []
        await sonarr_client.get_manual_import(series_id=1, season_number=3)

        sonarr_client._request.assert_called_once_with(
            "GET", "manualimport",
            params={"filterExistingFiles": True, "seriesId": 1, "seasonNumber": 3}
        )

    @pytest.mark.asyncio
    async def test_get_manual_import_with_folder(self, sonarr_client):
        """Test get_manual_import with folder path."""
        sonarr_client._request.return_value = []
        await sonarr_client.get_manual_import(folder="/downloads/tv")

        sonarr_client._request.assert_called_once_with(
            "GET", "manualimport",
            params={"filterExistingFiles": True, "folder": "/downloads/tv"}
        )

    @pytest.mark.asyncio
    async def test_manual_import(self, sonarr_client):
        """Test manual_import sends correct command."""
        sonarr_client._request.return_value = {"id": 1}
        files = [{"path": "/downloads/file.mkv", "seriesId": 1, "episodeIds": [10]}]
        result = await sonarr_client.manual_import(files=files, import_mode="move")

        sonarr_client._request.assert_called_once_with(
            "POST", "command",
            json={"name": "ManualImport", "files": files, "importMode": "move"}
        )
        assert result == {"id": 1}


class TestRadarrManualImport:
    """Test Radarr manual import methods."""

    @pytest.mark.asyncio
    async def test_get_manual_import_default(self, radarr_client):
        """Test get_manual_import with default params."""
        radarr_client._request.return_value = [{"path": "/downloads/movie.mkv"}]
        result = await radarr_client.get_manual_import()

        radarr_client._request.assert_called_once_with(
            "GET", "manualimport", params={"filterExistingFiles": True}
        )
        assert result == [{"path": "/downloads/movie.mkv"}]

    @pytest.mark.asyncio
    async def test_get_manual_import_with_download_id(self, radarr_client):
        """Test get_manual_import with download_id."""
        radarr_client._request.return_value = []
        await radarr_client.get_manual_import(download_id="xyz789")

        radarr_client._request.assert_called_once_with(
            "GET", "manualimport",
            params={"filterExistingFiles": True, "downloadId": "xyz789"}
        )

    @pytest.mark.asyncio
    async def test_get_manual_import_with_movie_id(self, radarr_client):
        """Test get_manual_import with movie_id."""
        radarr_client._request.return_value = []
        await radarr_client.get_manual_import(movie_id=42)

        radarr_client._request.assert_called_once_with(
            "GET", "manualimport",
            params={"filterExistingFiles": True, "movieId": 42}
        )

    @pytest.mark.asyncio
    async def test_get_manual_import_with_folder(self, radarr_client):
        """Test get_manual_import with folder path."""
        radarr_client._request.return_value = []
        await radarr_client.get_manual_import(folder="/downloads/movies")

        radarr_client._request.assert_called_once_with(
            "GET", "manualimport",
            params={"filterExistingFiles": True, "folder": "/downloads/movies"}
        )

    @pytest.mark.asyncio
    async def test_manual_import(self, radarr_client):
        """Test manual_import sends correct command."""
        radarr_client._request.return_value = {"id": 2}
        files = [{"path": "/downloads/movie.mkv", "movieId": 42}]
        result = await radarr_client.manual_import(files=files)

        radarr_client._request.assert_called_once_with(
            "POST", "command",
            json={"name": "ManualImport", "files": files, "importMode": "auto"}
        )
        assert result == {"id": 2}


class TestRadarrGrabQueueItem:
    """Test Radarr queue grab method."""

    @pytest.mark.asyncio
    async def test_grab_queue_item(self, radarr_client):
        """Test grab_queue_item sends POST to correct endpoint."""
        radarr_client._request.return_value = None
        await radarr_client.grab_queue_item(queue_id=99)

        radarr_client._request.assert_called_once_with(
            "POST", "queue/grab/99", json={}
        )


class TestToolRegistration:
    """Test that new tools are registered correctly."""

    def _make_server(self):
        """Create a minimal server with no real connections."""
        from unittest.mock import MagicMock
        from arr_suite_mcp.server import ArrSuiteMCPServer

        server = ArrSuiteMCPServer.__new__(ArrSuiteMCPServer)
        server.clients = {
            "sonarr": MagicMock(),
            "radarr": MagicMock(),
        }
        server.config = MagicMock()
        server.config.enabled_services = ["sonarr", "radarr"]
        server.server = MagicMock()
        server.router = MagicMock()
        return server

    def test_sonarr_tools_include_manual_import(self):
        """Verify sonarr manual import tools are registered."""
        server = self._make_server()
        tools = server._get_sonarr_tools()
        tool_names = [t.name for t in tools]

        assert "sonarr_get_manual_import" in tool_names
        assert "sonarr_manual_import" in tool_names

    def test_radarr_tools_include_manual_import_and_grab(self):
        """Verify radarr manual import and grab tools are registered."""
        server = self._make_server()
        tools = server._get_radarr_tools()
        tool_names = [t.name for t in tools]

        assert "radarr_get_manual_import" in tool_names
        assert "radarr_manual_import" in tool_names
        assert "radarr_grab_queue_item" in tool_names

    def test_sonarr_manual_import_requires_files(self):
        """Verify sonarr_manual_import requires files parameter."""
        server = self._make_server()
        tools = server._get_sonarr_tools()
        tool = next(t for t in tools if t.name == "sonarr_manual_import")

        assert "files" in tool.inputSchema["required"]

    def test_radarr_grab_requires_queue_id(self):
        """Verify radarr_grab_queue_item requires queue_id parameter."""
        server = self._make_server()
        tools = server._get_radarr_tools()
        tool = next(t for t in tools if t.name == "radarr_grab_queue_item")

        assert "queue_id" in tool.inputSchema["required"]
