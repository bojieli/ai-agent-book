"""Inject Open Graph + Twitter Card meta tags into every page so links
look rich when shared to WeChat / Twitter / Slack.

Material's `social` plugin can do this but needs cairosvg + image
rendering that silently no-ops in some CI environments. This hook is
simpler: it derives all tags from page + site config, no images.

(One concession: there's no og:image. We'd need either a pre-generated
PNG checked into the repo, or cairosvg on the CI runner. Cards still
render with title + description — they just don't have a hero image.
If we want images later, add a single default_og_image path here.)
"""
import html


def on_post_page(output, page, config, **kwargs):
    meta = page.meta or {}
    title = meta.get("title") or page.title or config.get("site_name", "")
    desc = meta.get("description") or config.get("site_description", "")
    url = page.canonical_url or ""
    site = config.get("site_name", "")

    def add(attr, key, val):
        return f'<meta {attr}="{key}" content="{html.escape(str(val), quote=True)}">'

    tags = [
        add("property", "og:type", "website"),
        add("property", "og:site_name", site),
        add("property", "og:title", title),
        add("property", "og:description", desc),
        add("property", "og:url", url),
        add("property", "og:locale", "zh_CN"),
        add("name", "twitter:card", "summary"),
        add("name", "twitter:title", title),
        add("name", "twitter:description", desc),
    ]
    block = "\n".join(t for t in tags if 'content=""' not in t)
    return output.replace("</head>", block + "\n</head>", 1)
