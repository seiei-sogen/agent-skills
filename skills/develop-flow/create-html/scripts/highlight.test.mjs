import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { test } from 'node:test';
import { parseHTML } from 'linkedom';

const run = promisify(execFile);
const script = fileURLToPath(new URL('./highlight.mjs', import.meta.url));
const page = '<!doctype html><html lang="ja"><head><title>色分け</title></head><body><h1>コードの説明</h1><svg viewBox="0 0 100 40"><text x="5" y="20">入力 → 出力</text></svg><p><code>inline()</code></p></body></html>';

test('highlights real grammars while preserving code, page elements and attributes', async t => {
  const dir = await mkdtemp(join(tmpdir(), 'create-html-test-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const { document } = parseHTML(page);
  const examples = new Map([
    ['ts', 'type User = { name: string };\n// 日本語\nfunction greet(user: User) { return `Hello ${user.name}`; }\n'],
    ['rb', 'class Greeter\n  def greet(name)\n    puts "Hello #{name}"\n  end\nend\n'],
    ['python', 'def greet(name: str) -> str:\n    return f"Hello {name}"\n'],
    ['sql', "SELECT name FROM users WHERE active = true AND visits > 42;"],
    ['html', '<script>alert("<&>")</script>\n<div title="引用">日本語</div>\n'],
    ['text', '\t<&> "日本語"\r\n\r\n'],
  ]);
  for (const [language, source] of examples) {
    const pre = document.createElement('pre');
    pre.id = language;
    pre.className = 'original';
    pre.setAttribute('aria-label', language);
    const code = document.createElement('code');
    code.className = `language-${language}`;
    code.textContent = source;
    pre.append(code);
    document.body.append(pre);
  }
  const input = join(dir, 'input.html');
  const output = join(dir, 'output.html');
  await writeFile(input, document.toString());
  await run(process.execPath, [script, input, output]);
  const rendered = await readFile(output, 'utf8');
  const result = parseHTML(rendered).document;
  for (const [language, source] of examples) {
    const pre = result.getElementById(language);
    assert.equal(pre.querySelector('code').textContent, source.replace(/\r\n?/g, '\n'));
    assert.equal(pre.getAttribute('aria-label'), language);
    assert.ok(pre.classList.contains('original'));
    assert.ok(pre.style.backgroundColor);
    if (language !== 'text') {
      const colors = new Set([...pre.querySelectorAll('span[style]')].map(span => span.style.color));
      assert.ok(colors.size >= 3, `${language} has distinct syntax colors`);
    }
  }
  const tsTokens = [...result.querySelectorAll('#ts span[style]')];
  const colorOf = word => tsTokens.find(span => span.textContent.trim() === word)?.style.color;
  assert.notEqual(colorOf('type'), colorOf('User'));
  assert.notEqual(colorOf('User'), colorOf('greet'));
  assert.equal(result.querySelector('svg').getAttribute('viewBox'), '0 0 100 40');
  assert.equal(result.querySelector('svg text').textContent, '入力 → 出力');
  assert.equal(result.querySelector('p code').outerHTML, '<code>inline()</code>');
  assert.equal(result.querySelectorAll('script, link, [src]').length, 0);
  assert.equal(result.querySelector('h1').textContent, 'コードの説明');

  const repeated = join(dir, 'repeated.html');
  await run(process.execPath, [script, output, repeated]);
  assert.equal(await readFile(repeated, 'utf8'), rendered);
});

test('rejects missing or unknown languages without writing a partial output', async t => {
  const dir = await mkdtemp(join(tmpdir(), 'create-html-errors-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  for (const className of ['', 'language-not-a-real-language']) {
    const input = join(dir, 'input.html');
    const output = join(dir, 'output.html');
    await writeFile(input, page.replace('</body>', `<pre><code class="language-js">const ok = 1;</code></pre><pre><code class="${className}">oops</code></pre></body>`));
    await assert.rejects(run(process.execPath, [script, input, output]), error => {
      assert.match(error.stderr, /language|not-a-real-language/i);
      return true;
    });
    await assert.rejects(readFile(output), { code: 'ENOENT' });
  }
});

test('handles pages without code and refuses to overwrite existing files', async t => {
  const dir = await mkdtemp(join(tmpdir(), 'create-html-files-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const input = join(dir, 'input.html');
  const output = join(dir, 'output.html');
  await writeFile(input, page);
  await run(process.execPath, [script, input, output]);
  assert.equal(parseHTML(await readFile(output, 'utf8')).document.querySelector('h1').textContent, 'コードの説明');
  await writeFile(output, 'existing output');
  await assert.rejects(run(process.execPath, [script, input, output]), /EEXIST/);
  assert.equal(await readFile(output, 'utf8'), 'existing output');
  await assert.rejects(run(process.execPath, [script, input, input]), /EEXIST/);
  assert.equal(await readFile(input, 'utf8'), page);
  await assert.rejects(run(process.execPath, [script]), /Usage:/);
});
