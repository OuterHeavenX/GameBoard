# Gameboard

One board for every game and app on [github.com/OuterHeavenX](https://github.com/OuterHeavenX), sorted by category, with live GitHub status.

Single static page. No backend, no build step: open `index.html` or serve it with GitHub Pages.

## Run it

- **GitHub Pages:** Settings → Pages → Source: *Deploy from a branch* → `main` / `(root)`. The board is then at `https://outerheavenx.github.io/GameBoard/`.
- **Locally:** double-click `index.html`.

## How it works

- **Repo list and status** come live from the public GitHub API (cached for 1 hour; the refresh button forces a reload). Last push, description, language and the Play link (GitHub Pages) update on their own.
- **Categories** come from the `M` manifest at the top of the script in `index.html`. Entries marked with a trailing `1` were categorised from the repo name only and show a *Check category* badge until you open the project and Save it.
- **New repos** you create later appear automatically with a *New repo* badge and a suggested category.
- **Your edits** (stage, version, bugs, QA results, priorities, changelog notes, category changes) are stored in this browser's `localStorage`. Use **Backup → Export / Import** to carry them to another browser or device.
- **Private repos** are not listed by the public API and are not in the manifest, so their names are not published. Add them with **Add project** (stored only in your browser).

## Screenshots

Every card shows a title-screen thumbnail; click it for the gallery (title screen + two gameplay shots).

- **Automatic:** the *Capture screenshots* GitHub Action (Actions tab → Run workflow; also runs Mondays) opens each repo's live GitHub Pages build in headless Chrome, takes the title screen, clicks Start / presses Enter, then takes up to two gameplay shots. Results are committed to `shots/<repo>/{title,play1,play2}.jpg` and listed in `shots/index.json`. It is best effort: games it can't drive just keep whatever shots they have. Repos without GitHub Pages are skipped.
- **By hand:** commit your own `title.jpg`, `play1.jpg`, `play2.jpg` into `shots/<repo>/`; the bot never overwrites files it didn't create. Or use the project's **Screenshots** tab to upload shots (kept in this browser only, and they override repo shots there).
- `shots/config.json` controls the bot: `skip` repos are never visited (password-vault and oft-team-board by default) and `title_only` repos get just the first screen.

## Release gate

A project is flagged ready only when it has a version, no open bugs, and every QA check that applies to its platform targets is *Passed* or *Not applicable*. Real iPhone / Real Steam Deck checks count only when the target is selected.

## Editing the category list

Change the `CATS` array (categories) and `M` rows (`[repo, display name, category id, engine, guessed?]`) in `index.html`, commit, and Pages redeploys.

## Changes from the original zip

The original was a Next/vinext app that needed OpenAI Sites hosting (a D1 database and an `/api/projects` route), so it could not run from GitHub. This version replaces that with static hosting and local storage. See the notes in the pull request or commit message for the bugs fixed along the way.
