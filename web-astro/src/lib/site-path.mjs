// Route data stays relative to the application root; deployments may use a subdirectory.
export function withBase(path, base = import.meta.env?.BASE_URL ?? '/') {
  if (!path.startsWith('/') || path.startsWith('//')) return path;
  return `${base.replace(/\/$/, '')}${path}`;
}
