import hashlib
from pathlib import Path
import aiohttp
import pytest
from aioresponses import aioresponses
from main import (
    calculate_sha256,
    download_files_recursive,
    download_repo_files,
    fetch_file,
)


@pytest.mark.asyncio
async def test_fetch_file(tmp_path: Path) -> None:
    with aioresponses() as m:
        url = "https://example.com/testfile.txt"
        content = b"test content"
        m.get(url, body=content)

        dest = tmp_path / "testfile.txt"
        async with aiohttp.ClientSession() as session:
            await fetch_file(session, url, dest)

        assert dest.exists()
        assert dest.read_bytes() == content


@pytest.mark.asyncio
async def test_download_files_recursive() -> None:
    url = "http://example.com/files"
    temp_dir = Path("/tmp/test_download")

    mock_contents = [
        {"type": "dir", "name": "subdir1"},
        {
            "type": "file",
            "name": "file1.txt",
            "download_url": "http://example.com/download/file1.txt",
        },
        {
            "type": "file",
            "name": "file2.txt",
            "download_url": "http://example.com/download/file2.txt",
        },
    ]
    mock_subdir_contents = [
        {
            "type": "file",
            "name": "subfile.txt",
            "download_url": "http://example.com/download/subfile.txt",
        }
    ]

    with aioresponses() as m:
        m.get(url, payload=mock_contents)
        m.get("http://example.com/download/file1.txt", body=b"File 1 contents")
        m.get("http://example.com/download/file2.txt", body=b"File 2 contents")
        m.get("http://example.com/files/subdir1", payload=mock_subdir_contents)
        m.get(
            "http://example.com/download/subfile.txt",
            body=b"Subfile contents",
        )

        async with aiohttp.ClientSession() as session:
            await download_files_recursive(session, url, temp_dir)

    assert (temp_dir / "file1.txt").is_file()
    assert (temp_dir / "file2.txt").is_file()
    assert (temp_dir / "subdir1" / "subfile.txt").is_file()


@pytest.mark.asyncio
async def test_download_repo_files(tmp_path: Path) -> None:
    with aioresponses() as m:
        repo_url = "https://example.com/api/v1/repos/test/repo/contents"
        contents = [
            {
                "type": "file",
                "name": "testfile.txt",
                "download_url": "https://example.com/testfile.txt",
            }
        ]
        m.get(repo_url, payload=contents)
        m.get("https://example.com/testfile.txt", body=b"test content")

        files = await download_repo_files(repo_url, tmp_path)

        assert len(files) == 1
        assert files[0].read_bytes() == b"test content"


@pytest.mark.asyncio
async def test_calculate_sha256(tmp_path: Path) -> None:
    file_path = tmp_path / "testfile.txt"
    content = b"test content"
    file_path.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    _, sha256_hash = await calculate_sha256(file_path)

    assert sha256_hash == expected_hash
