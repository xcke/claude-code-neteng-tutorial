# blog-examples

Companion code and examples for blog posts on [internetworking.dev](https://internetworking.dev).

## Examples

| Folder | Blog post |
|--------|-----------|
| [`claude-code-neteng-tutorial/`](claude-code-neteng-tutorial/) | [Getting started with Claude Code as a network engineer](https://internetworking.dev/blog/getting-started-with-claude-code-as-a-network-engineer) |

## How this works

This directory is the source of truth. A GitHub Action (`.github/workflows/sync-examples.yml`) mirrors its contents to the public repo [xcke/blog-examples](https://github.com/xcke/blog-examples) on every push to `main`.

**To add a new tutorial:**
1. Create a new folder under `examples/` with a README
2. Push to `main` — the sync happens automatically

No extra repos, no PAT updates, no matrix config changes.
