# data/db

This directory stores internal, persistent records. These files are
implementation details and must never be exposed by the raw resource API.

- `content/`: article indexes and comments.
- `identity/`: users, credentials and authorization state.
- `analytics/`: analytics events and aggregates.
- `deployment/`: deployment history.

The `data/db` directory is used to store project database.

All `*.json` files are ignored by Git.
