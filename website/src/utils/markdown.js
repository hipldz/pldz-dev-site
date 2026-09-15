import { marked } from "marked";
import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import css from "highlight.js/lib/languages/css";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import markdown from "highlight.js/lib/languages/markdown";
import plaintext from "highlight.js/lib/languages/plaintext";
import python from "highlight.js/lib/languages/python";
import scss from "highlight.js/lib/languages/scss";
import typescript from "highlight.js/lib/languages/typescript";
import xml from "highlight.js/lib/languages/xml";
import yaml from "highlight.js/lib/languages/yaml";

hljs.registerLanguage("bash", bash);
hljs.registerLanguage("shell", bash);
hljs.registerLanguage("sh", bash);
hljs.registerLanguage("css", css);
hljs.registerLanguage("html", xml);
hljs.registerLanguage("vue", xml);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("js", javascript);
hljs.registerLanguage("json", json);
hljs.registerLanguage("markdown", markdown);
hljs.registerLanguage("md", markdown);
hljs.registerLanguage("plaintext", plaintext);
hljs.registerLanguage("text", plaintext);
hljs.registerLanguage("python", python);
hljs.registerLanguage("py", python);
hljs.registerLanguage("scss", scss);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("ts", typescript);
hljs.registerLanguage("yaml", yaml);
hljs.registerLanguage("yml", yaml);

function slugify(value = "") {
  return (
    String(value)
      .toLowerCase()
      .trim()
      .replace(/<[^>]+>/g, "")
      .replace(/[^\w\u4e00-\u9fa5\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "") || "section"
  );
}

function createSlugFactory() {
  const counts = new Map();
  return (text) => {
    const base = slugify(text);
    const current = counts.get(base) || 0;
    counts.set(base, current + 1);
    return current === 0 ? base : `${base}-${current + 1}`;
  };
}

function walkTokens(tokens, visitor) {
  if (!Array.isArray(tokens)) return;

  for (const token of tokens) {
    visitor(token);

    if (Array.isArray(token.tokens)) {
      walkTokens(token.tokens, visitor);
    }

    if (Array.isArray(token.items)) {
      walkTokens(token.items, visitor);
    }
  }
}

function escapeHtml(value = "") {
  return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function normalizeLanguage(lang = "") {
  const language = String(lang || "")
    .trim()
    .toLowerCase();
  if (!language) return "";
  if (hljs.getLanguage(language)) return language;
  return "";
}

function toOriginalImageUrl(value = "") {
  const url = String(value || "").trim();
  if (!url || /^(?:data:|blob:)/i.test(url)) return url;

  const hashIndex = url.indexOf("#");
  const hash = hashIndex >= 0 ? url.slice(hashIndex) : "";
  const withoutHash = hashIndex >= 0 ? url.slice(0, hashIndex) : url;
  const queryIndex = withoutHash.indexOf("?");
  const query = queryIndex >= 0 ? withoutHash.slice(queryIndex) : "";
  const path = queryIndex >= 0 ? withoutHash.slice(0, queryIndex) : withoutHash;

  return `${path.endsWith("@original") ? path : `${path}@original`}${query}${hash}`;
}

export function renderMarkdown(source = "") {
  const markdown = String(source || "");
  const tokens = marked.lexer(markdown, {
    gfm: true,
    breaks: true,
  });

  const nextSlug = createSlugFactory();
  const headings = [];
  const images = [];

  walkTokens(tokens, (token) => {
    if (token.type === "heading") {
      const id = nextSlug(token.text);
      token.headingId = id;
      headings.push({
        id,
        text: token.text,
        depth: token.depth,
      });
    }

    if (token.type === "image") {
      token.imageIndex = images.length;
      const source = String(token.href || "");
      images.push({
        src: source,
        originalSrc: toOriginalImageUrl(source),
        alt: String(token.text || ""),
      });
    }
  });

  const renderer = new marked.Renderer();

  renderer.heading = function ({ tokens: inlineTokens, depth, text, headingId }) {
    const innerHtml = this.parser.parseInline(inlineTokens);
    return `<h${depth} id="${headingId || slugify(text)}">${innerHtml}</h${depth}>`;
  };

  renderer.link = function ({ href, title, tokens: inlineTokens }) {
    const innerHtml = this.parser.parseInline(inlineTokens);

    // Images render their own original-image link so article lightbox semantics stay consistent.
    if (Array.isArray(inlineTokens) && inlineTokens.length === 1 && inlineTokens[0]?.type === "image") {
      return innerHtml;
    }

    const safeHref = escapeHtml(href || "#");
    const isExternal = /^https?:\/\//i.test(href || "");
    const titleAttr = title ? ` title="${escapeHtml(title)}"` : "";
    const targetAttr = isExternal ? ' target="_blank" rel="noopener noreferrer"' : "";
    return `<a href="${safeHref}"${titleAttr}${targetAttr}>${innerHtml}</a>`;
  };

  renderer.image = function ({ href, title, text, imageIndex }) {
    const source = String(href || "");
    const originalSource = toOriginalImageUrl(source);
    const safeSource = escapeHtml(source);
    const safeOriginal = escapeHtml(originalSource);
    const safeAlt = escapeHtml(text || "");
    const titleAttr = title ? ` title="${escapeHtml(title)}"` : "";
    const ariaLabel = escapeHtml(text ? `查看原图：${text}` : "查看文章原图");

    return `<a class="markdown-image-link" href="${safeOriginal}" data-original-src="${safeOriginal}" data-image-index="${Number.isInteger(imageIndex) ? imageIndex : 0}" target="_blank" rel="noopener noreferrer" aria-label="${ariaLabel}"><img src="${safeSource}" alt="${safeAlt}" loading="lazy" decoding="async"${titleAttr}></a>`;
  };

  renderer.code = function ({ text, lang }) {
    const language = normalizeLanguage(lang) || "plaintext";
    const languageLabel = language.toUpperCase();
    const encodedCode = encodeURIComponent(text || "");
    const highlightedHtml = hljs.getLanguage(language) ? hljs.highlight(text || "", { language }).value : escapeHtml(text || "");

    return [
      '<div class="code-block">',
      '  <div class="code-block__header">',
      `    <span class="code-block__lang">${escapeHtml(languageLabel)}</span>`,
      `    <button class="code-block__copy" type="button" data-code="${encodedCode}">复制</button>`,
      "  </div>",
      `  <pre><code class="hljs language-${escapeHtml(language)}">${highlightedHtml}</code></pre>`,
      "</div>",
    ].join("");
  };

  const html = marked.parser(tokens, {
    gfm: true,
    breaks: true,
    renderer,
  });

  return { html, headings, images };
}
