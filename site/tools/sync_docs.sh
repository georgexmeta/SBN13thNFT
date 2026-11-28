#!/bin/sh
# Copy the cabin site (site/world) into docs/ for GitHub Pages (claysons.xyz). Run after every site change.
cd "$(dirname "$0")/../.." && rm -rf docs/img docs/media && cp -r site/world/index.html site/world/holders.json site/world/owners.json site/world/img site/world/media docs/ && echo claysons.xyz > docs/CNAME && touch docs/.nojekyll
