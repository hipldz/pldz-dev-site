import { randomUUID } from "node:crypto";
import { constants } from "node:fs";
import { copyFile, mkdir, readFile, readdir, rename, rm, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const destination = path.join(root, "src/assets/fonts");
const userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";

async function download(url) {
  const response = await fetch(url, { headers: { "User-Agent": userAgent }, signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`${response.status} while downloading ${url}`);
  return response;
}

async function writeAssets(assets) {
  await mkdir(destination, { recursive: true });
  const batch = randomUUID();
  const files = [];
  try {
    // Prepare every replacement and backup before changing any active asset.
    for (const [name, data] of assets) {
      const filename = path.join(destination, name);
      const file = {
        filename,
        temporary: `${filename}.${batch}.tmp`,
        backup: `${filename}.${batch}.bak`,
        hadOriginal: false,
        installed: false,
        keepBackup: false,
      };
      files.push(file);
      try {
        await copyFile(filename, file.backup, constants.COPYFILE_EXCL);
        file.hadOriginal = true;
      } catch (error) {
        if (error.code !== "ENOENT") throw error;
      }
      await writeFile(file.temporary, data, { flag: "wx" });
    }
    for (const file of files) {
      await rename(file.temporary, file.filename);
      file.installed = true;
    }
  } catch (error) {
    const rollbackErrors = [];
    for (const file of [...files].reverse()) {
      if (!file.installed) continue;
      try {
        if (file.hadOriginal) await rename(file.backup, file.filename);
        else await rm(file.filename, { force: true });
      } catch (rollbackError) {
        file.keepBackup = file.hadOriginal;
        const recovery = file.hadOriginal ? `; backup retained at ${file.backup}` : "";
        rollbackErrors.push(new Error(`Failed to restore ${file.filename}${recovery}`, { cause: rollbackError }));
      }
    }
    if (rollbackErrors.length) throw new AggregateError([error, ...rollbackErrors], "Font update failed and rollback was incomplete");
    throw error;
  } finally {
    for (const file of files) {
      for (const filename of file.keepBackup ? [file.temporary] : [file.temporary, file.backup]) {
        try {
          await rm(filename, { force: true });
        } catch (error) {
          console.warn(`Unable to remove temporary file ${filename}: ${error.message}`);
        }
      }
    }
  }
}

async function sourceTokens(directory) {
  const tokens = new Set();
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name === "fonts") continue;
    const filename = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      for (const token of await sourceTokens(filename)) tokens.add(token);
    } else if (/\.(vue|js|css)$/.test(entry.name)) {
      const rawSource = await readFile(filename, "utf8");
      const source = rawSource.replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/g, "");
      const addNames = (value) => {
        if (/^[a-z][a-z0-9_]*$/.test(value.trim())) tokens.add(value.trim());
        for (const match of value.matchAll(/(["'`])([a-z][a-z0-9_]*)\1/g)) tokens.add(match[2]);
      };
      // Static names and both branches of conditional icon expressions.
      for (const match of source.matchAll(/<span\b[^>]*class="[^"]*\b(?:material-symbols-rounded|ui-icon)\b[^"]*"[^>]*>([\s\S]*?)<\/span\s*>/g)) {
        addNames(match[1]);
      }
      // Command/result icon data and icon props passed to AccountDialog.
      for (const match of source.matchAll(/\bicon:\s*(["'`])([a-z][a-z0-9_]*)\1/g)) tokens.add(match[2]);
      for (const match of source.matchAll(/\b:?icon="([^"]+)"/g)) addNames(match[1]);
      // Pseudo-element icon names can live in CSS or Vue style blocks.
      const styles = entry.name.endsWith(".css")
        ? [rawSource]
        : Array.from(rawSource.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/g), (match) => match[1]);
      for (const style of styles) {
        const css = style.replace(/\/\*[\s\S]*?\*\//g, "");
        for (const match of css.matchAll(/(?:^|[;{])\s*content\s*:\s*(["'])([a-z][a-z0-9_]*)\1/g)) tokens.add(match[2]);
      }
    }
  }
  return tokens;
}

const codepoints = await (
  await download(
    "https://raw.githubusercontent.com/google/material-design-icons/master/variablefont/MaterialSymbolsRounded%5BFILL%2CGRAD%2Copsz%2Cwght%5D.codepoints",
  )
).text();
const tokens = await sourceTokens(path.join(root, "src"));
const icons = codepoints
  .split(/\r?\n/)
  .map((line) => line.split(" ")[0])
  .filter((name) => tokens.has(name))
  .sort();
if (!icons.length) throw new Error("No Material Symbols found in source files");

const families = [
  { name: "Manrope", query: "Manrope:wght@400..800", file: "manrope-latin.woff2", display: "optional", latin: true },
  { name: "Caveat", query: "Caveat:wght@500..600", file: "caveat-latin.woff2", display: "optional", latin: true },
  {
    name: "Material Symbols Rounded",
    query: "Material Symbols Rounded:opsz,wght,FILL,GRAD@24,300..600,0,0",
    file: "material-symbols-rounded.woff2",
    display: "block",
    icons,
  },
];

const assets = new Map();
const rules = ["/* Generated by node scripts/update-fonts.mjs. See README.md for sources and licenses. */"];
for (const family of families) {
  const url = new URL("https://fonts.googleapis.com/css2");
  url.searchParams.set("family", family.query);
  url.searchParams.set("display", family.display);
  if (family.icons) url.searchParams.set("icon_names", family.icons.join(","));
  const css = await (await download(url)).text();
  const faces = css.match(/@font-face\s*\{[^}]+\}/g) || [];
  const face = family.latin ? faces.find((rule) => rule.includes("U+0000-00FF")) : faces[0];
  if (!face) throw new Error(`Missing font face for ${family.name}`);
  const fontUrl = face.match(/url\(([^)]+)\)\s*format\(['"]woff2['"]\)/)?.[1];
  if (!fontUrl) throw new Error(`Expected WOFF2 for ${family.name}`);
  const buffer = Buffer.from(await (await download(fontUrl)).arrayBuffer());
  if (buffer.length < 48 || buffer.subarray(0, 4).toString() !== "wOF2" || buffer.readUInt32BE(8) !== buffer.length) {
    throw new Error(`Invalid WOFF2 for ${family.name}`);
  }
  assets.set(family.file, buffer);
  // Ship icon ligatures with the CSS, so a late font request cannot expose their names.
  const asset = `./${family.file}${family.icons ? "?inline" : ""}`;
  rules.push(face.replace(/url\([^)]+\)/, `url("${asset}")`));
  console.log(`${family.file}: ${buffer.length} bytes`);
}
assets.set("fonts.css", `${rules.join("\n\n")}\n`);
assets.set("icons.json", `${JSON.stringify(icons, null, 2)}\n`);

for (const [file, url] of [
  ["OFL-Manrope.txt", "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/OFL.txt"],
  ["OFL-Caveat.txt", "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/OFL.txt"],
  ["Apache-2.0.txt", "https://raw.githubusercontent.com/google/material-design-icons/master/LICENSE"],
]) {
  assets.set(file, await (await download(url)).text());
}
await writeAssets(assets);
console.log(`Included ${icons.length} Material Symbols; review icons.json after adding icons.`);
