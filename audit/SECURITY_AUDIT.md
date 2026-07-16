# Security audit

Audit date: 2026-07-16

Scope: every external module and generic widget script referenced by the supplied Egern profile, plus all functional `script-path`, `script_url`, and `RULE-SET` dependencies discovered inside those modules. The supplied Surge main profile contains remote rule sets but no embedded Surge module list; those rule sets already point to `ciallothu/proxy_rules`.

## Executive conclusion

No reviewed snapshot contained an obvious credential-stealing or deliberate exfiltration payload. This is **not** a declaration that the modules are safe. Several modules have enough privilege to read authenticated HTTPS responses, alter application behavior, access subscription URLs, or redirect official service traffic to third-party infrastructure. The main systemic risk was mutable remote code loaded from `master`, `main`, `latest`, or `kelee.one`; this repository mirrors those dependencies and rewrites module references to a controlled origin.

Mirroring reduces upstream supply-chain replacement risk, but it does not remove runtime privacy risks, overly broad MITM scope, application breakage, or risks inherent in the mirrored code itself.

## Highest-risk findings

### 1. iRingo WeatherKit — High

The module rewrites Apple WeatherKit API requests from `weatherkit.apple.com` to `weatherkit.nanocat.cloud`. This exposes weather request metadata, which may include precise or approximate location data, to a third-party service. Mirroring the module does not change that redirect. Disable this module unless the third-party service is explicitly trusted.

### 2. Sub-Store — High privilege

The module intercepts `sub.store`, handles subscription preview/download/synchronization, and can synchronize artifacts to a private Gist. It therefore operates on subscription URLs and potentially node credentials. Its default CORS allowlist is materially safer than `*`; do not set CORS to `*`. The mirrored scripts remain high-trust code.

### 3. Script Hub — High privilege

Script Hub converts arbitrary rewrite modules, rule sets, and scripts supplied by the user. This is expected functionality, but it makes the module a code-processing trust boundary. A compromised converter could alter generated scripts or rules. Keep it disabled when not actively used.

### 4. Kelee/QingRex application modules — High supply-chain and MITM risk

Multiple modules load mutable JavaScript from `kelee.one` and MITM authenticated APIs belonging to JD, Zhihu, Taobao, Xiaohongshu, Weibo, NetEase Music, and Amap. Some hostname scopes are broad, including `*.zhihu.com`, `*.weibo.com`, and `*.amap.com`. The scripts can read the complete matched response body. Reviewed snapshots primarily remove or reorder JSON fields, but the permission scope is substantially larger than the advertised “remove ads” function.

The mirror recursively copies these JavaScript dependencies and rewrites the module references, removing the live dependency on `kelee.one`. App updates can still make the rewrites destructive or incompatible.

### 5. BiliBili ADBlock — High privilege

The module intercepts Bilibili JSON and binary gRPC responses, including feed, view, dynamic, playback, search, comments, and other application APIs. It loads release-bundled request and response scripts. The mirror removes the `latest`/release runtime dependency, but the module can still break playback or account functions after Bilibili protocol changes.

### 6. IP/datacenter and proxy-check widgets — High privacy risk

The widgets send the current exit IP to several external IP intelligence services. Reviewed endpoints include IPIP, NetEase, ip-api, proxycheck.io, Blackbox, ipapi.is, and ip.net.coffee. Some requests use plain HTTP, allowing network observers or intermediaries to modify results. These widgets should be treated as deliberate IP disclosure tools rather than passive local diagnostics.

## Medium-risk findings

### BoxJs

BoxJs provides persistent storage and settings for scripts. Its risk depends on what other scripts store in it. Do not store reusable passwords, long-lived access tokens, or unrelated secrets.

### Airport traffic widget

The widget sends each configured subscription URL directly to that subscription endpoint and reads `subscription-userinfo`. The reviewed code did not forward subscription URLs to an unrelated collector. The URLs themselves contain bearer-like tokens and must not be committed to this public repository.

### Weather widget

The widget sends the configured location and QWeather API key to the configured QWeather API host. The API key is visible in the Egern profile and should be rotated if the profile has been shared publicly.

### App-specific static/JQ modules

Baidu Netdisk, JD Waimai, Quark, Pinduoduo, Didi, WeChat Official Accounts, WeChat Mini Programs, Tencent Docs, and several other modules are mostly static rules, `Map Local`, URL rewrites, or local JQ response edits. They did not show a separate exfiltration path in the reviewed snapshot. Their principal risks are broad TLS interception, false positives, broken application features, and removal of non-advertising data.

### app2smile Qidian and Tieba

These modules MITM application APIs and execute JavaScript from a moving branch. The mirror captures the scripts and Tieba rule set. Protocol changes can cause malformed binary responses or application failures.

## Lower-risk findings

### NetSpeed widget

The widget downloads approximately 3 MB from Cloudflare per refresh. It does not require account data, but frequent refreshes consume bandwidth, battery, and server traffic.

### Advertising platform blocker and Surge-2 Ad Block

These are primarily static domain/IP rejection lists. They have low code-execution risk but a significant false-positive risk because analytics, push, crash reporting, HTTPDNS, and legitimate shared infrastructure may be blocked together with advertising.

## Sensitive material excluded from this repository

The unredacted Egern and Surge profiles contain credentials and cryptographic material, including subscription tokens, a weather API key, and MITM PKCS#12 data/passphrases. They are intentionally not committed here. Making this repository public while committing those profiles would disclose reusable credentials and the private interception CA.

## Recommended operating controls

1. Keep this repository public only for executable modules/scripts; keep unredacted profiles elsewhere.
2. Review `MANIFEST.json` after each automated update and compare SHA-256 changes before deploying.
3. Disable Sub-Store, Script Hub, BoxJs, WeatherKit, and broad application MITM modules when not needed.
4. Prefer narrowly scoped hostnames and endpoints over wildcards such as `*.weibo.com` and `*.amap.com`.
5. Remove or replace plain-HTTP IP intelligence endpoints.
6. Rotate exposed subscription tokens, QWeather keys, and MITM certificates if they have ever been placed in a public repository.
