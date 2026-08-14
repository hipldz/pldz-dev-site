export function buildPublicFileUrl(namespace, path) {
  const encodedPath = String(path)
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
  return new URL("/api/v1/" + namespace + "/" + encodedPath, window.location.origin).href;
}

export async function copyText(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  textarea.style.top = "0";
  document.body.appendChild(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  document.body.removeChild(textarea);
  if (!copied) throw new Error("Unable to copy text");
}
