## Gitsync.py

Simple script to automatically sync repositories.

### Configuration

Configuration JSON should be placed at: `$XDG_CONFIG_DIR/gitsync/config.json`, where `$XDG_CONFIG_DIR` is usually `$HOME/.config`.
It should look like following:

```json
{
    "dotfiles": {
        "path": "~/workspace/dotfiles",
        "remote": "private"
    },
    "work": {
        "path": "~/workspace/someprivaterepo",
        "remote": "origin"
    }
}
```

Each first-level key is human-readable name, used only for logging.
`path` is actual path to repository, tilda will be correctly expanded to user home directory.
`remote` is git remote to which it should be pushed.

### Run

Script doesn't accept any options and can be configured only via its config JSON file.
It checks if any files that were added to repository previously are changed and if so - commits them.
It checks if any commits were not pushed and if so - pushed them.
That's it.
