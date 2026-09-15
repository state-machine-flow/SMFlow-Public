# SMFlow-Public — release role

This repository is the public face of SMFlow: documentation, samples, and the **published
releases**. The editor's source lives in the private `SMFlow` repo (`F:/repos/ctacke/SMFlow`), and
its release workflow publishes installers *here*. Nothing is built in this repository.

## When a release is asked for

A release is never cut from this repository alone. The full sequence lives in the private repo's
`CLAUDE.md` under "Releasing" — follow it there. This repository's part of it:

1. **Add the version's entry to `releases/CHANGELOG.md`** before the release is published. Keep a
   Changelog form, `## [<version>] - <date>`, newest first, written for the person installing it.
   This file is user-facing and is *not* generated from the private repo's `CHANGELOG.md`; both must
   be updated, and they are worded differently on purpose.
2. **Commit and push it to `main`** ahead of the tag, so the release tag lands on a commit that
   documents the release.
3. **Do not create the `v<version>` tag by hand.** The private repo's workflow creates it here when
   it publishes, pointing at whatever `main` is then. A hand-made local tag will disagree with it.
4. **Verify the release is not a draft** once the workflow is green:

   ```
   gh release view v<version> --json isDraft,isPrerelease,assets
   ```

   The packaging tool merges into a leftover draft if one exists, which leaves the release
   undownloadable while the workflow still reports success. Publish with
   `gh release edit v<version> --draft=false --prerelease`.

A release only counts as done when `gh release view` reports `isDraft=false` and the five assets
(`SMFlow-win-Setup.exe`, `SMFlow-win-Portable.zip`, the `.nupkg`, `RELEASES`, `releases.win.json`)
are attached. Betas stay marked as prereleases — that is the channel the in-app updater follows.

# context-mode — MANDATORY routing rules

You have context-mode MCP tools available. These rules are NOT optional — they protect your context window from flooding. A single unrouted command can dump 56 KB into context and waste the entire session.

## BLOCKED commands — do NOT attempt these

### curl / wget — BLOCKED
Any Bash command containing `curl` or `wget` is intercepted and replaced with an error message. Do NOT retry.
Instead use:
- `ctx_fetch_and_index(url, source)` to fetch and index web pages
- `ctx_execute(language: "javascript", code: "const r = await fetch(...)")` to run HTTP calls in sandbox

### Inline HTTP — BLOCKED
Any Bash command containing `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, or `http.request(` is intercepted and replaced with an error message. Do NOT retry with Bash.
Instead use:
- `ctx_execute(language, code)` to run HTTP calls in sandbox — only stdout enters context

### WebFetch — BLOCKED
WebFetch calls are denied entirely. The URL is extracted and you are told to use `ctx_fetch_and_index` instead.
Instead use:
- `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` to query the indexed content

## REDIRECTED tools — use sandbox equivalents

### Bash (>20 lines output)
Bash is ONLY for: `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`, and other short-output commands.
For everything else, use:
- `ctx_batch_execute(commands, queries)` — run multiple commands + search in ONE call
- `ctx_execute(language: "shell", code: "...")` — run in sandbox, only stdout enters context

### Read (for analysis)
If you are reading a file to **Edit** it → Read is correct (Edit needs content in context).
If you are reading to **analyze, explore, or summarize** → use `ctx_execute_file(path, language, code)` instead. Only your printed summary enters context. The raw file content stays in the sandbox.

### Grep (large results)
Grep results can flood context. Use `ctx_execute(language: "shell", code: "grep ...")` to run searches in sandbox. Only your printed summary enters context.

## Tool selection hierarchy

1. **GATHER**: `ctx_batch_execute(commands, queries)` — Primary tool. Runs all commands, auto-indexes output, returns search results. ONE call replaces 30+ individual calls.
2. **FOLLOW-UP**: `ctx_search(queries: ["q1", "q2", ...])` — Query indexed content. Pass ALL questions as array in ONE call.
3. **PROCESSING**: `ctx_execute(language, code)` | `ctx_execute_file(path, language, code)` — Sandbox execution. Only stdout enters context.
4. **WEB**: `ctx_fetch_and_index(url, source)` then `ctx_search(queries)` — Fetch, chunk, index, query. Raw HTML never enters context.
5. **INDEX**: `ctx_index(content, source)` — Store content in FTS5 knowledge base for later search.

## Subagent routing

When spawning subagents (Agent/Task tool), the routing block is automatically injected into their prompt. Bash-type subagents are upgraded to general-purpose so they have access to MCP tools. You do NOT need to manually instruct subagents about context-mode.

## Output constraints

- Keep responses under 500 words.
- Write artifacts (code, configs, PRDs) to FILES — never return them as inline text. Return only: file path + 1-line description.
- When indexing content, use descriptive source labels so others can `ctx_search(source: "label")` later.

## ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call the `ctx_stats` MCP tool and display the full output verbatim |
| `ctx doctor` | Call the `ctx_doctor` MCP tool, run the returned shell command, display as checklist |
| `ctx upgrade` | Call the `ctx_upgrade` MCP tool, run the returned shell command, display as checklist |
