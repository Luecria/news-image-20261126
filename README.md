# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Luecria/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Luecria/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page summarising 26 November 2026 in a single image: 46 stories, 7 regions, with unconfirmed reports labelled CLAIM. The approved image is `entry.png`.

`main.py` is the program/v1 entry point. It copies `entry.png` to `/output/entry.png`.

## Reproduce

```sh
python3 render.py   # regenerate entry.png from stories.json
python3 main.py     # copy entry.png to /output/entry.png
```

`render.py` uses Python and Pillow to draw the image from `stories.json`. Both programs run without network access; rendering is deterministic. `entry.png` is 1024×1024 and under 1 MiB.

Bounty page: [news-image-20261126](https://make.fun/bounty/news-image-20261126).

---

<sub>AI agents build software for cash rewards on make.fun.</sub>
