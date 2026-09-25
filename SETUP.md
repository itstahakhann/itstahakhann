# Taha Khan GitHub Profile V2

## Install

Copy the contents of this folder into your profile repository:

`itstahakhann/itstahakhann`

Then push to `main`.

## Snake

The snake workflow runs daily and can also be started manually from:

GitHub → Actions → Contribution Snake → Run workflow

It publishes the generated SVG to the `output` branch.

## Coding time

WakaTime requires your own public embeddable chart URL.

1. Set up WakaTime in your editor.
2. Create a public embeddable chart.
3. Replace `YOUR_WAKATIME_EMBED_URL` in README.md.
4. Commit and push.

Do not put a WakaTime API key in README.md or client-side code.

## Latest repositories

The profile-visuals workflow calls the public GitHub API and regenerates
`assets/latest-repositories.svg` every 6 hours.

## Currently building

Edit `assets/currently-building.svg` whenever your current project changes.
This is intentionally a simple, custom SVG so the profile stays black/white
and doesn't depend on another profile-card service.

## Important

The README intentionally uses SVG `<img>` elements rather than inline scripts.
GitHub sanitizes README HTML, so JavaScript-based animations should not be
expected to run. SVG animation is the safer approach for this style of profile.
