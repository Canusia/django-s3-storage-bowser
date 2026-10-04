import type { AtRule, Plugin } from 'postcss';

/** Wrapper element around the browser in templates/s3_storage_browser/_app.html. */
export const SCOPE = '.s3-storage-browser';

// Styles elements by tag alone: no class, id or attribute anywhere in it.
const isGlobal = (selector: string) =>
  selector !== ':root' && !/[.#[]/.test(selector.replace(/:not\([^)]*\)/g, ''));

const scopeSelector = (selector: string) => {
  if (!isGlobal(selector)) return selector;
  const page = selector.match(/^(html|body)(?=$|[\s:>+~])/);
  return page ? SCOPE + selector.slice(page[0].length) : `${SCOPE} ${selector}`;
};

/**
 * Amplify's stylesheet carries page-level rules (html font, body
 * min-height/line-height, form-control resets). Rendered inside a host
 * layout they restyle the host's chrome, so confine them to the wrapper.
 */
export const scopeGlobalCss = (): Plugin => ({
  postcssPlugin: 'scope-global-css',
  Rule(rule) {
    const parent = rule.parent;
    if (parent?.type === 'atrule' && /keyframes$/.test((parent as AtRule).name)) return;
    const scoped = rule.selectors.map(scopeSelector);
    if (scoped.every((s, i) => s === rule.selectors[i])) return;
    if (rule.selectors.includes('body')) {
      rule.walkDecls('min-height', (decl) => {
        if (decl.value === '100vh') decl.remove();
      });
    }
    rule.selectors = scoped;
  },
});
