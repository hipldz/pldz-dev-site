# data/cache

This directory contains disposable data that can be regenerated or downloaded
again without losing authoritative application state.

- `webp/`: generated image variants.
- `article-index/`: rebuildable metadata derived from Markdown articles.
- `deployments/artifacts/`: downloaded deployment archives.
- `deployments/work/`: temporary extraction workspaces.
- Files at the root are managed by the generic cache API.
