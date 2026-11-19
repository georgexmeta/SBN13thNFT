# claysons.xyz

Static one-page site for Claysons. No build step: deploy the `site/` folder as-is.

- `index.html`: the page (generated from `page.html` by wrapping it in a document head; edit `page.html`, then regenerate).
- `img/`, `media/`: title, sneak-peek tokens (public pre-reveal set), pre-reveal video (720p, re-encoded).
- Reveal time for the countdown: `REVEAL` in the script at the bottom.

Hosting: Cloudflare Pages (or Netlify) with build output directory `site`, then add the custom domain claysons.xyz.
