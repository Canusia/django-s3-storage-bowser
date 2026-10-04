import { readFileSync } from 'fs';
import { resolve } from 'path';
import postcss from 'postcss';
import { describe, expect, it } from 'vitest';

import { SCOPE, scopeGlobalCss } from '../scopeGlobalCss';

const scope = (css: string) => postcss([scopeGlobalCss()]).process(css, { from: undefined }).css;

// A selector that styles elements by tag alone (no class, id or attribute)
// reaches outside the browser into the host page.
const isGlobal = (selector: string) =>
  selector !== ':root' && !/[.#[]/.test(selector.replace(/:not\([^)]*\)/g, ''));

describe('scopeGlobalCss', () => {
  it('moves html and body rules onto the wrapper', () => {
    expect(scope('html,[data-amplify-theme]{font-family:x}'))
      .toBe(`${SCOPE},[data-amplify-theme]{font-family:x}`);
    expect(scope('body{line-height:1.5}')).toBe(`${SCOPE}{line-height:1.5}`);
    expect(scope('html:focus-within{scroll-behavior:smooth}'))
      .toBe(`${SCOPE}:focus-within{scroll-behavior:smooth}`);
  });

  it('drops the full-viewport min-height Amplify puts on body', () => {
    expect(scope('body{min-height:100vh;line-height:1.5}')).toBe(`${SCOPE}{line-height:1.5}`);
  });

  it('nests bare element selectors inside the wrapper', () => {
    expect(scope('input,button{font:inherit}'))
      .toBe(`${SCOPE} input,${SCOPE} button{font:inherit}`);
    expect(scope('*{box-sizing:border-box}')).toBe(`${SCOPE} *{box-sizing:border-box}`);
  });

  it('leaves class, attribute and :root selectors alone', () => {
    const css = ':root{--a:1}.amplify-button{color:red}[data-amplify-theme] a{color:blue}';
    expect(scope(css)).toBe(css);
  });

  it('leaves keyframe steps alone', () => {
    const css = '@keyframes spin{from{opacity:0}to{opacity:1}}';
    expect(scope(css)).toBe(css);
  });
});

describe('built stylesheet', () => {
  it('has no rule that styles the host page', () => {
    const built = readFileSync(
      resolve(__dirname, '../../s3_storage_browser/static/s3_storage_browser/index.css'), 'utf8');
    const global: string[] = [];
    postcss.parse(built).walkRules((rule) => {
      if (rule.parent?.type === 'atrule' && /keyframes/.test((rule.parent as postcss.AtRule).name)) return;
      global.push(...rule.selectors.filter(isGlobal));
    });
    expect(global).toEqual([]);
  });
});
