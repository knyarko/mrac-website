# Maryland Responsible AI Council (MRAC) website

Static rebuild of [marylandresponsibleai.org](https://marylandresponsibleai.org), deployed with GitHub Pages.

## Editing content

All text lives in `content/` — no HTML editing needed for routine updates:

- `content/site.json` — intro, "What the Council does" list, key areas, meetings, recommendations
- `content/members.json` — members (`group` is `founding` or `council`), bios, photo paths
- `content/committees.json` — committees and their members (`name`, `role`, `affiliation`). A committee member whose name matches a council member reuses that member's photo and links to their bio; anyone else shows a silhouette until you add `"image": "assets/img/members/<file>"`

Headshots go in `assets/img/members/`. The header and lighthouse photos are set under `photos` in `site.json` (Unsplash License; credits are shown in the footer). Keep large photos under ~700 KB. In a bio, a short line without ending punctuation becomes a heading, and lines starting with `– ` become a bulleted list.

Meetings are generated from `meeting_schedule` in `site.json`: each series is the Nth weekday of the month (General Meeting on the 1st Monday, Core Council Meeting on the 3rd). The site lists meetings from the build date through the end of next month (`"months": 2`), and past meetings drop off. The deploy workflow rebuilds on the 1st of every month, so the list rolls forward on its own.

To cancel one occurrence (a holiday, say), add its date to `skip`. To add a one-off meeting, append to `meetings`:

```json
{ "date": "Jan 15, 2027", "title": "Special Session", "description": "Virtual (Zoom) · By invitation only" }
```

## Preview locally

```bash
python3 build.py --serve
```

Then open http://localhost:8000. Requires only Python 3 (no dependencies).

## Deploying

Pushing to `main` runs `.github/workflows/pages.yml`, which builds the site and publishes it to GitHub Pages.
One-time setup in the GitHub repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

To serve it at `marylandresponsibleai.org`, set the custom domain under Settings → Pages and point the domain's DNS at GitHub Pages.
