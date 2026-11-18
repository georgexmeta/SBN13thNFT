# Claysons trait explorer

Live page: https://claude.ai/artifact/PQE3u5jATfLJthDe8nDGx1

Rebuild (e.g. after the Body trait lands):

    unzip -q launch/export-YYYY-MM-DD/claysons-images-small.zip -d /tmp/imgs   # <tokenID>.jpg
    python3 build_explorer.py generator/published_traits.csv /tmp/imgs out      # or pass the zip directly

Then republish out/index.html to the same artifact URL with files s/0-12.jpg and l/0-12.jpg.
Categories are read from the attributes[...] columns, so a new Body column needs no code change.
