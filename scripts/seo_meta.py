"""MkDocs hook: inject Open Graph + Twitter Card meta tags into every page's
<head> so links look rich when shared to WeChat / Twitter / Slack / Discord.

Material's `social` plugin can generate these automatically but requires
cairosvg + a working build-time image renderer that's fragile across
environments. This hook is simpler and deterministic: it derives all the
tags from the page's existing frontmatter / title / site config, no
image rendering required.

Default card uses the site description + the og-card.png in assets/.
Per-page frontmatter can override:
    ---
    title: ...
    description: ...
    og_image: <URL or path under docs_dir>
    ---

Implementation note: we use on_post_page (string manipulation on the
fully rendered HTML) rather than on_page_context, because Material's
templates don't reliably render a custom {{ extrahead }} block without
a theme override.
"""
import html
import re


def _abs(config, path):
    """Resolve a path under docs_dir to an absolute site URL."""
    site = (config.get("site_url") or "").rstrip("/")
    if not site:
        return None
    if path.startswith("http"):
        return path
    return site + "/" + path.lstrip("/")


def on_post_page(output, page, config, **kwargs):
    # Build the meta tags from page + site config.
    meta = page.meta or {}
    site_name = config.get("site_name") or ""
    title = meta.get("title") or page.title or site_name
    description = meta.get("description") or config.get("site_description") or ""
    page_url = page.canonical_url or ""
    site = (config.get("site_url") or "").rstrip("/")

    # OG image: page frontmatter > site-wide default.
    image_path = meta.get("og_image") or (config.get("extra") or {}).get("default_og_image")
    image = _abs(config, image_path) if image_path else None

    tags = []
    def add(prop, val, use_name=False):
        if not val:
            return
        attr = "name" if use_name else "property"
        tags.append(
            f'<meta {attr}="{prop}" content="{html.escape(str(val), quote=True)}">'
        )

    # Open Graph
    add("og:type", "website")
    add("og:site_name", site_name)
    add("og:title", title)
    add("og:description", description)
    add("og:url", page_url)
    add("og:locale", "zh_CN")
    if image:
        add("og:image", image)
        add("og:image:width", "1200")
        add("og:image:height", "630")
        add("og:image:alt", title)

    # Twitter Card
    add("twitter:card", "summary_large_image" if image else "summary",
        use_name=True)
    add("twitter:title", title, use_name=True)
    add("twitter:description", description, use_name=True)
    if image:
        add("twitter:image", image, use_name=True)
        add("twitter:image:alt", title, use_name=True)

    if not tags:
        return output

    block = "\n".join(tags)

    # Inject right before </head>. Material always emits a <head>, so this
    # is safe. We add a leading newline so the inserted block is on its own
    # line for readability of the built HTML.
    if "</head>" in output:
        return output.replace("</head>", block + "\n</head>", 1)
    # Fallback: prepend if there's no </head> for some reason.
    return block + "\n" + output

