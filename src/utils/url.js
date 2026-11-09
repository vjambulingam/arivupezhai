/**
 * Path helper for GitHub Pages base URL support
 */
export function getUrl(path = '') {
  const rawBase = import.meta.env.BASE_URL || '/';
  const base = rawBase === '/' ? '' : rawBase.replace(/\/$/, '');
  if (!path || path === '/') {
    return base || '/';
  }
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${cleanPath}`;
}
