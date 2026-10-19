import { readFile, writeFile } from 'node:fs/promises';
import { parseHTML } from 'linkedom';
import { codeToHtml } from 'shiki';

const stylesheetId = 'create-html-code-style';
const codeStyles = `
pre.shiki {
  box-sizing: border-box;
  max-width: 100%;
  overflow-x: auto;
  padding: 1rem;
  border-radius: .75rem;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: .9rem;
  line-height: 1.7;
  tab-size: 2;
}
pre.shiki > code {
  display: block;
  padding: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  white-space: pre;
  overflow-wrap: normal;
  word-break: normal;
}
pre.shiki:focus-visible { outline: 3px solid #2563eb; outline-offset: 3px; }
`;

try {
  const [input, output, ...extra] = process.argv.slice(2);
  if (!input || !output || extra.length) {
    throw new Error('Usage: node highlight.mjs input.html output.html');
  }

  const { document } = parseHTML(await readFile(input, 'utf8'));
  if (document.documentElement?.localName !== 'html'
      || !document.querySelector('head') || !document.querySelector('body')) {
    throw new Error('Input must be a complete HTML document with head and body.');
  }

  const blocks = document.querySelectorAll('pre > code');
  for (const code of blocks) {
    const languageClass = [...code.classList].find(name => name.startsWith('language-'));
    if (!languageClass) {
      throw new Error('Every code block needs a language-* class. Use language-text for plain text.');
    }
    const language = languageClass.slice('language-'.length);
    const highlighted = await codeToHtml(code.textContent.replace(/\r\n?/g, '\n'), {
      lang: language,
      theme: 'dark-plus',
    });
    const highlightedPre = parseHTML(highlighted).document.querySelector('pre');
    code.innerHTML = highlightedPre.querySelector('code').innerHTML;
    const pre = code.parentElement;
    pre.classList.add('shiki');
    pre.style.backgroundColor = highlightedPre.style.backgroundColor;
    pre.style.color = highlightedPre.style.color;
    pre.setAttribute('tabindex', pre.getAttribute('tabindex') ?? '0');
  }

  if (blocks.length) {
    document.getElementById(stylesheetId)?.remove();
    const style = document.createElement('style');
    style.id = stylesheetId;
    style.textContent = codeStyles;
    document.head.append(style);
  }
  await writeFile(output, document.toString(), { encoding: 'utf8', flag: 'wx' });
  console.log(`Highlighted ${blocks.length} code blocks. Wrote ${output}`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
