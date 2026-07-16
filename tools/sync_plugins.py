#!/usr/bin/env python3
"""Mirror the proxy modules/scripts referenced by the user's Egern profile.

The script downloads each declared top-level source, recursively mirrors functional
code dependencies declared by script-path/script_url/RULE-SET, rewrites those URLs
to this repository, and emits an integrity manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_BASE = "https://cdn.jsdelivr.net/gh/ciallothu/proxy_plugins@main/"
USER_AGENT = "proxy_plugins-sync/1.0 (+https://github.com/ciallothu/proxy_plugins)"

TOP_LEVEL_SOURCES: dict[str, str] = {
    "modules/core/SubStore.yaml": "https://raw.githubusercontent.com/sub-store-org/Sub-Store/refs/heads/master/config/Egern.yaml",
    "modules/core/Script-Hub.sgmodule": "https://raw.githubusercontent.com/Script-Hub-Org/Script-Hub/main/modules/script-hub.surge.sgmodule",
    "modules/core/BoxJs.sgmodule": "https://raw.githubusercontent.com/chavyleung/scripts/master/box/rewrite/boxjs.rewrite.surge.sgmodule",
    "modules/core/iRingo.WeatherKit.Workers.srmodule": "https://github.com/NSRingo/WeatherKit/raw/main/modules/iRingo.WeatherKit.Workers.srmodule",
    "modules/bilibili/BiliBili.ADBlock.sgmodule": "https://github.com/BiliUniverse/ADBlock/releases/latest/download/BiliBili.ADBlock.sgmodule",
    "modules/ads/kelee-filter.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%8F%AF%E8%8E%89%E5%B9%BF%E5%91%8A%E8%BF%87%E6%BB%A4%E5%99%A8.beta.sgmodule",
    "modules/ads/ad-platform-blocker.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%B9%BF%E5%91%8A%E5%B9%B3%E5%8F%B0%E6%8B%A6%E6%88%AA%E5%99%A8.beta.sgmodule",
    "modules/network/block-httpdns.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E6%8B%A6%E6%88%AAHTTPDNS.beta.sgmodule",
    "modules/ads/baidu-netdisk.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E7%99%BE%E5%BA%A6%E7%BD%91%E7%9B%98%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/jd.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E4%BA%AC%E4%B8%9C%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/jd-waimai.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E4%BA%AC%E4%B8%9C%E5%A4%96%E5%8D%96%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/quark.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%A4%B8%E5%85%8B%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/pinduoduo.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E6%8B%BC%E5%A4%9A%E5%A4%9A%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/didi.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E6%BB%B4%E6%BB%B4%E5%87%BA%E8%A1%8C%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/zhihu.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E7%9F%A5%E4%B9%8E%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/wechat-official.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%BE%AE%E4%BF%A1%E5%85%AC%E4%BC%97%E5%8F%B7%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/wechat-miniprogram.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/tencent-docs.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E8%85%BE%E8%AE%AF%E6%96%87%E6%A1%A3%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/taobao.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E6%B7%98%E5%AE%9D%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/xiaohongshu.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%B0%8F%E7%BA%A2%E4%B9%A6%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/weibo.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E5%BE%AE%E5%8D%9A%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/netease-music.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Beta/%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E5%8E%BB%E5%B9%BF%E5%91%8A.beta.sgmodule",
    "modules/ads/amap.sgmodule": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/%E9%AB%98%E5%BE%B7%E5%9C%B0%E5%9B%BE%E5%8E%BB%E5%B9%BF%E5%91%8A.sgmodule",
    "modules/ads/qidian.sgmodule": "https://raw.githubusercontent.com/app2smile/rules/master/module/qidian.sgmodule",
    "modules/ads/tieba.sgmodule": "https://raw.githubusercontent.com/app2smile/rules/master/module/tieba.sgmodule",
    "modules/ads/general-ad-block.sgmodule": "https://raw.githubusercontent.com/vhvg/Surge-2/master/Module/Ad%20Block.sgmodule",
    "scripts/widgets/weather.js": "https://raw.githubusercontent.com/IBL3ND/module/main/Weather_Widget.JS",
    "scripts/widgets/ip-datacenter.js": "https://raw.githubusercontent.com/magicdan3688/MyProxyScripts/refs/heads/main/ip-dch.js",
    "scripts/widgets/netspeed.js": "https://raw.githubusercontent.com/IBL3ND/module/main/NetSpeed_Widget.JS",
    "scripts/widgets/proxy-check.js": "https://raw.githubusercontent.com/IBL3ND/module/main/Proxy_Check.JS",
    "scripts/widgets/airport-traffic.js": "https://raw.githubusercontent.com/IBL3ND/module/main/airport_widget.js",
}

SCRIPT_PATTERNS = [
    re.compile(r"(?<=script-path=)https?://[^,\s]+"),
    re.compile(r"(?<=script-path\s=\s)https?://[^,\s]+"),
    re.compile(r"(?<=script_url:\s)https?://[^\s]+"),
]
RULE_PATTERN = re.compile(r"(?<=RULE-SET,)https?://[^,\s]+")


def fetch(url: str, attempts: int = 4) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urlopen(req, timeout=90) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"failed to download {url}: {last_error}")


def raw_url(path: str) -> str:
    return RAW_BASE + "/".join(quote(part, safe="._-~") for part in Path(path).parts)


def safe_segment(value: str) -> str:
    value = unquote(value).strip().replace("\\", "-")
    value = re.sub(r"[^A-Za-z0-9._@+~-]+", "-", value)
    return value.strip(".-") or "file"


def dependency_path(url: str, kind: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    parts = [p for p in parsed.path.split("/") if p]
    root = Path("scripts/vendor" if kind == "script" else "rules/vendor")
    if host == "raw.githubusercontent.com" and len(parts) >= 4:
        owner, repo, _ref, *rest = parts
        result = root / safe_segment(owner) / safe_segment(repo)
        for item in rest:
            result /= safe_segment(item)
    elif host == "github.com" and len(parts) >= 2:
        owner, repo, *rest = parts
        result = root / safe_segment(owner) / safe_segment(repo)
        for item in rest:
            result /= safe_segment(item)
    else:
        result = root / safe_segment(host)
        for item in parts:
            result /= safe_segment(item)
    if not result.suffix:
        result = result.with_suffix(".txt")
    if parsed.query:
        digest = hashlib.sha256(parsed.query.encode()).hexdigest()[:10]
        result = result.with_name(f"{result.stem}-{digest}{result.suffix}")
    return result.as_posix()


def find_dependencies(text: str) -> Iterable[tuple[str, str]]:
    seen: set[str] = set()
    for pattern in SCRIPT_PATTERNS:
        for match in pattern.finditer(text):
            url = match.group(0).strip('"\'')
            if "{{" not in url and url not in seen:
                seen.add(url)
                yield url, "script"
    for match in RULE_PATTERN.finditer(text):
        url = match.group(0).strip('"\'')
        if "{{" not in url and url not in seen:
            seen.add(url)
            yield url, "rule"


def write_bytes(relative_path: str, data: bytes) -> None:
    target = REPO_ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def clean_generated_directories() -> None:
    for relative in ("modules", "scripts/widgets", "scripts/vendor", "rules/vendor"):
        path = REPO_ROOT / relative
        if path.exists():
            shutil.rmtree(path)


def load_previous_manifest() -> dict:
    path = REPO_ROOT / "MANIFEST.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    previous_manifest = load_previous_manifest()
    clean_generated_directories()
    provenance: dict[str, str] = {}
    queue: list[str] = []
    for destination, source in TOP_LEVEL_SOURCES.items():
        print(f"download {source} -> {destination}")
        write_bytes(destination, fetch(source))
        provenance[destination] = source
        queue.append(destination)
    processed: set[str] = set()
    while queue:
        relative_path = queue.pop(0)
        if relative_path in processed:
            continue
        processed.add(relative_path)
        path = REPO_ROOT / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        replacements: dict[str, str] = {}
        for source_url, kind in find_dependencies(text):
            destination = dependency_path(source_url, kind)
            if destination not in provenance:
                print(f"dependency {source_url} -> {destination}")
                write_bytes(destination, fetch(source_url))
                provenance[destination] = source_url
                queue.append(destination)
            replacements[source_url] = raw_url(destination)
        if replacements:
            for old, new in replacements.items():
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")

    manifest_files = []
    for relative_path, source in sorted(provenance.items()):
        data = (REPO_ROOT / relative_path).read_bytes()
        manifest_files.append({
            "path": relative_path,
            "raw_url": raw_url(relative_path),
            "source": source,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        })

    if previous_manifest.get("files") == manifest_files and previous_manifest.get("generated_at"):
        generated_at = previous_manifest["generated_at"]
    else:
        generated_at = datetime.now(timezone.utc).isoformat()

    manifest = {
        "repository": "ciallothu/proxy_plugins",
        "generated_at": generated_at,
        "files": manifest_files,
    }
    (REPO_ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Upstream sources", "", f"Last synchronized: `{generated_at}`", "",
        "| Mirror path | Upstream source | SHA-256 |", "|---|---|---|",
    ]
    for item in manifest_files:
        lines.append(f"| `{item['path']}` | {item['source']} | `{item['sha256']}` |")
    lines.extend([
        "",
        "Third-party files retain their original copyright and licensing terms.",
        "The mirror does not grant a new license where an upstream project provides none.",
        "",
    ])
    (REPO_ROOT / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"mirrored {len(manifest_files)} files")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        raise
