Scripts are stdlib-only (except Pixabay, below) and honour the shell's `http(s)_proxy`. Cache: `~/.cache/sfx-sources`.

Pixabay (pixabay.com) sits behind Cloudflare, which 403s plain urllib. `pixabay` / `get px:…` re-exec the script under a private venv (`~/.cache/sfx-sources/venv`, created on first use with `pip install curl_cffi`) that impersonates Chrome's TLS. Needs `python3 -m venv` + pip access once. 403s are sporadic and retried; persistent 403 means Cloudflare tightened.

Freesound (freesound.org, servers in Finland) is the only source that is network-sensitive:
- It caps every connection at ~80 KB/s regardless of route, so pick a proxy node by latency, not bandwidth; parallelise via one `get`.
- Some proxy nodes time out entirely; DIRECT from mainland China is ~5–13 KB/s. Route `freesound.org` to a low-latency (often EU) node.
- Originals need an API key + OAuth2 (not supported); previews (~190 kbps mp3) are what `get` downloads.

`scripts/clash_freesound.py` automates this for **ClashX Meta (mihomo) on macOS**, controller `127.0.0.1:9090`, no secret:
- no args: show whether the rule / group exist and the current node's latency.
- `--fix`: add a select group `Freesound` (12 lowest-latency nodes + DIRECT) and first rule `DOMAIN-SUFFIX,freesound.org,Freesound` to the active profile (`~/.config/clash.meta/<selectConfigName>.yaml`, backup saved), reload via `PUT /configs?force=true`, select the fastest node.
- Subscription updates overwrite the profile, so rerun `--fix` after one.

Other Clash clients: add the same group + rule by hand (or via your client's override/merge feature).
