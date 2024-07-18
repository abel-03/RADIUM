import asyncio
import hashlib
import tempfile
from pathlib import Path

import aiohttp


async def fetch_file(
    session: aiohttp.ClientSession, url: str, dest: Path
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with session.get(url) as response:
        response.raise_for_status()
        dest.write_bytes(await response.read())


async def download_files_recursive(
    session: aiohttp.ClientSession, url: str, temp_dir: Path
) -> None:
    async with session.get(url) as response:
        response.raise_for_status()
        contents = await response.json()

    tasks = []
    for item in contents:
        if item["type"] == "dir":
            subdir_url = f"{url}/{item['name']}"
            subdir_path = (
                temp_dir / item["name"]
            )
            tasks.append(download_files_recursive(
                session, subdir_url, subdir_path))

        elif item["type"] == "file":
            file_url = item["download_url"]
            file_path = (
                temp_dir / item["name"]
            )
            file_path.parent.mkdir(parents=True, exist_ok=True)
            tasks.append(fetch_file(session, file_url, file_path))

    await asyncio.gather(*tasks)


async def download_repo_files(repo_url: str, temp_dir: Path) -> None:
    async with aiohttp.ClientSession() as session:
        await download_files_recursive(session, repo_url, temp_dir)

    return list(temp_dir.glob("**/*"))


async def calculate_sha256(file_path: Path) -> None:
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return file_path, sha256.hexdigest()


async def main() -> None:
    repo_url = (
        "https://gitea.radium.group/api/v1/repos/"
        "radium/project-configuration/contents"
    )
    temp_dir_path = Path(tempfile.mkdtemp())
    downloaded_files = await download_repo_files(repo_url, temp_dir_path)

    tasks = [calculate_sha256(file)
             for file in downloaded_files if file.is_file()]

    hashes = await asyncio.gather(*tasks)

    for file_path, sha256_hash in hashes:
        print(f"{file_path}: {sha256_hash}")


if __name__ == "__main__":
    asyncio.run(main())
