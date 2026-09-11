// v3.0 interaction identity primitives.
// The effects are deliberately compositor-first: transform / translate / opacity,
// one requestAnimationFrame per active pointer surface, and automatic touch/reduced-motion fallback.
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
const running = new Set();
const elementAnimations = new WeakMap();
const cleanupMap = new WeakMap();

function addCleanup(element, cleanup) {
  const cleanups = cleanupMap.get(element) || [];
  cleanups.push(cleanup);
  cleanupMap.set(element, cleanups);
}

function cleanupElement(element) {
  const cleanups = cleanupMap.get(element) || [];
  cleanupMap.delete(element);
  cleanups.forEach((cleanup) => {
    try {
      cleanup();
    } catch (error) {
      console.warn("motion cleanup failed", error);
    }
  });
}

function canUsePointerMotion() {
  return !reducedMotion.matches && finePointer.matches;
}

function makeFrameRunner(callback) {
  let frame = 0;
  let latest = null;
  const run = (payload) => {
    latest = payload;
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      callback(latest);
    });
  };
  run.cancel = () => {
    if (frame) cancelAnimationFrame(frame);
    frame = 0;
  };
  return run;
}

function trackAnimation(element, animation) {
  elementAnimations.get(element)?.cancel?.();
  elementAnimations.set(element, animation);
  running.add(animation);
  const cleanup = () => {
    running.delete(animation);
    if (elementAnimations.get(element) === animation) elementAnimations.delete(element);
  };
  animation.finished.then(cleanup, cleanup);
}

function animateRevealItem(item, index = 0) {
  if (!item?.animate || reducedMotion.matches) return;
  const delay = Math.min(index * 72, 360);
  const animation = item.animate(
    [
      { opacity: 0, transform: "translate3d(0, 24px, 0) scale(.985)" },
      { opacity: 0.78, transform: "translate3d(0, 4px, 0) scale(.998)", offset: 0.72 },
      { opacity: 1, transform: "translate3d(0, 0, 0) scale(1)" },
    ],
    { duration: 660, delay, easing: "cubic-bezier(0.16, 1, 0.3, 1)", fill: "both" },
  );
  running.add(animation);
  animation.finished.then(
    () => running.delete(animation),
    () => running.delete(animation),
  );
}

export function enterContent(element) {
  if (!element?.animate || reducedMotion.matches) return;
  const animation = element.animate(
    [
      { opacity: 0.35, transform: "translate3d(0, 18px, 0) scale(.992)" },
      { opacity: 1, transform: "translate3d(0, 0, 0) scale(1)" },
    ],
    { duration: 560, easing: "cubic-bezier(0.16, 1, 0.3, 1)" },
  );
  trackAnimation(element, animation);
}

function animateRevealMedia(item, index = 0) {
  if (!item?.animate || reducedMotion.matches) return;
  const delay = Math.min(index * 64 + 70, 360);
  const animation = item.animate(
    [
      { opacity: 0.12, clipPath: "inset(12% 2% 10% 2% round 22px)", transform: "translate3d(0, 18px, 0) scale(1.045)" },
      { opacity: 1, clipPath: "inset(0% 0% 0% 0% round 0px)", transform: "translate3d(0, 0, 0) scale(1)" },
    ],
    { duration: 760, delay, easing: "cubic-bezier(0.16, 1, 0.3, 1)", fill: "both" },
  );
  running.add(animation);
  animation.finished.then(
    () => running.delete(animation),
    () => running.delete(animation),
  );
}

function revealElement(element) {
  element.classList.add("is-revealed");
  const items = Array.from(element.querySelectorAll(":scope [data-reveal-item]"));
  const media = Array.from(element.querySelectorAll(":scope [data-reveal-media]"));
  if (!items.length && !media.length) {
    enterContent(element);
    return;
  }
  items.slice(0, 10).forEach((item, index) => animateRevealItem(item, index));
  media.slice(0, 8).forEach((item, index) => animateRevealMedia(item, index));
}

const revealObserver =
  typeof IntersectionObserver === "undefined"
    ? null
    : new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            revealObserver.unobserve(entry.target);
            revealElement(entry.target);
          }
        },
        { threshold: 0.08 },
      );

const spotlightObserver =
  typeof IntersectionObserver === "undefined"
    ? null
    : new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            entry.target.classList.toggle("is-spotlight", entry.isIntersecting);
          }
        },
        {
          rootMargin: "-16% 0px -64% 0px",
          threshold: 0,
        },
      );

export const reveal = {
  mounted(element) {
    element.classList.add("motion-reveal-root");
    if (reducedMotion.matches || !revealObserver) {
      element.classList.add("is-revealed");
      return;
    }
    if (element.getBoundingClientRect().top < window.innerHeight * 0.9) {
      revealElement(element);
      return;
    }
    revealObserver.observe(element);
  },
  beforeUnmount(element) {
    revealObserver?.unobserve(element);
    elementAnimations.get(element)?.cancel?.();
  },
};

// Current-section focus with a logo-derived spark plus a pointer-local illumination.
// Pointer work is active only while the section is under a fine pointer.
export const spotlight = {
  mounted(element) {
    element.dataset.spotlight = "";
    const marker = document.createElement("span");
    marker.className = "spotlight-spark";
    marker.setAttribute("aria-hidden", "true");
    const guide = document.createElement("span");
    guide.className = "spotlight-guide";
    guide.setAttribute("aria-hidden", "true");
    const aura = document.createElement("span");
    aura.className = "spotlight-aura";
    aura.setAttribute("aria-hidden", "true");
    element.append(marker, guide, aura);

    let runner = null;
    let onMove = null;
    let onEnter = null;
    let onLeave = null;
    if (canUsePointerMotion()) {
      runner = makeFrameRunner(({ x, y }) => {
        const rect = element.getBoundingClientRect();
        element.style.setProperty("--spot-x", `${(x - rect.left).toFixed(1)}px`);
        element.style.setProperty("--spot-y", `${(y - rect.top).toFixed(1)}px`);
      });
      onMove = (event) => runner({ x: event.clientX, y: event.clientY });
      onEnter = () => element.classList.add("is-spotlight-pointer");
      onLeave = () => {
        runner.cancel();
        element.classList.remove("is-spotlight-pointer");
      };
      element.addEventListener("pointerenter", onEnter, { passive: true });
      element.addEventListener("pointermove", onMove, { passive: true });
      element.addEventListener("pointerleave", onLeave, { passive: true });
    }

    if (!spotlightObserver) element.classList.add("is-spotlight");
    else spotlightObserver.observe(element);

    addCleanup(element, () => {
      spotlightObserver?.unobserve(element);
      runner?.cancel();
      if (onMove) element.removeEventListener("pointermove", onMove);
      if (onEnter) element.removeEventListener("pointerenter", onEnter);
      if (onLeave) element.removeEventListener("pointerleave", onLeave);
      marker.remove();
      guide.remove();
      aura.remove();
      element.style.removeProperty("--spot-x");
      element.style.removeProperty("--spot-y");
    });
  },
  beforeUnmount(element) {
    cleanupElement(element);
  },
};

// Magnetic response for primary actions. v2.9 allows a little more travel so the
// response is actually perceptible, while remaining bounded and tap-safe.
export const magnetic = {
  mounted(element, binding) {
    if (binding.value === false || !canUsePointerMotion()) return;
    const strength = Math.max(4, Math.min(Number(binding.value) || 8, 12));
    const runner = makeFrameRunner(({ x, y }) => {
      const rect = element.getBoundingClientRect();
      const nx = ((x - rect.left) / Math.max(rect.width, 1) - 0.5) * 2;
      const ny = ((y - rect.top) / Math.max(rect.height, 1) - 0.5) * 2;
      element.style.translate = `${(nx * strength).toFixed(2)}px ${(ny * strength * 0.68).toFixed(2)}px`;
      element.style.setProperty("--magnetic-x", nx.toFixed(3));
      element.style.setProperty("--magnetic-y", ny.toFixed(3));
    });
    const onMove = (event) => runner({ x: event.clientX, y: event.clientY });
    const onEnter = () => element.classList.add("is-magnetic");
    const onLeave = () => {
      runner.cancel();
      element.classList.remove("is-magnetic");
      element.style.translate = "0 0";
      element.style.removeProperty("--magnetic-x");
      element.style.removeProperty("--magnetic-y");
    };
    element.classList.add("motion-magnetic");
    element.addEventListener("pointerenter", onEnter, { passive: true });
    element.addEventListener("pointermove", onMove, { passive: true });
    element.addEventListener("pointerleave", onLeave, { passive: true });
    addCleanup(element, () => {
      runner.cancel();
      element.removeEventListener("pointerenter", onEnter);
      element.removeEventListener("pointermove", onMove);
      element.removeEventListener("pointerleave", onLeave);
      element.style.translate = "";
      element.classList.remove("motion-magnetic", "is-magnetic");
    });
  },
  beforeUnmount(element) {
    cleanupElement(element);
  },
};

// Refraction-style depth surface. Only the card currently under the pointer is
// updated. The rim and light are normal DOM gradients; there is no canvas/WebGL.
export const depth = {
  mounted(element, binding) {
    if (binding.value === false || !canUsePointerMotion()) return;
    const amount = Math.max(0.7, Math.min(Number(binding.value) || 1.25, 2.4));
    const light = document.createElement("span");
    light.className = "motion-depth__light";
    light.setAttribute("aria-hidden", "true");
    const rim = document.createElement("span");
    rim.className = "motion-depth__rim";
    rim.setAttribute("aria-hidden", "true");
    const sheen = document.createElement("span");
    sheen.className = "motion-depth__sheen";
    sheen.setAttribute("aria-hidden", "true");
    element.append(light, rim, sheen);
    element.classList.add("motion-depth");
    const layers = () => Array.from(element.querySelectorAll("[data-depth-layer]"));

    const runner = makeFrameRunner(({ x, y }) => {
      const rect = element.getBoundingClientRect();
      const localX = x - rect.left;
      const localY = y - rect.top;
      const nx = localX / Math.max(rect.width, 1) - 0.5;
      const ny = localY / Math.max(rect.height, 1) - 0.5;
      const tiltY = nx * amount * 3.2;
      const tiltX = -ny * amount * 2.5;
      const angle = (Math.atan2(localY - rect.height / 2, localX - rect.width / 2) * 180) / Math.PI + 90;
      light.style.transform = `translate3d(${(localX - 190).toFixed(1)}px, ${(localY - 190).toFixed(1)}px, 0)`;
      rim.style.setProperty("--rim-angle", `${angle.toFixed(1)}deg`);
      element.style.transform = `perspective(1100px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) translate3d(0,-5px,0)`;
      for (const layer of layers()) {
        const factor = Number(layer.dataset.depthLayer) || 1;
        layer.style.translate = `${(-nx * factor * 11).toFixed(2)}px ${(-ny * factor * 8).toFixed(2)}px`;
      }
    });
    const onMove = (event) => runner({ x: event.clientX, y: event.clientY });
    const onEnter = () => element.classList.add("is-depth-active");
    const onLeave = () => {
      runner.cancel();
      element.classList.remove("is-depth-active");
      element.style.transform = "";
      light.style.transform = "translate3d(-420px, -420px, 0)";
      for (const layer of layers()) layer.style.translate = "0 0";
    };
    element.addEventListener("pointerenter", onEnter, { passive: true });
    element.addEventListener("pointermove", onMove, { passive: true });
    element.addEventListener("pointerleave", onLeave, { passive: true });
    addCleanup(element, () => {
      runner.cancel();
      element.removeEventListener("pointerenter", onEnter);
      element.removeEventListener("pointermove", onMove);
      element.removeEventListener("pointerleave", onLeave);
      element.style.transform = "";
      for (const layer of layers()) layer.style.translate = "";
      light.remove();
      rim.remove();
      sheen.remove();
      element.classList.remove("motion-depth", "is-depth-active");
    });
  },
  beforeUnmount(element) {
    cleanupElement(element);
  },
};

// Large-surface pointer field. v2.9 makes the parallax and illumination clearly
// visible while still limiting updates to the single active surface.
export const field = {
  mounted(element) {
    if (!canUsePointerMotion()) return;
    const light = document.createElement("span");
    light.className = "motion-field__light";
    light.setAttribute("aria-hidden", "true");
    const mesh = document.createElement("span");
    mesh.className = "motion-field__mesh";
    mesh.setAttribute("aria-hidden", "true");
    element.append(light, mesh);
    element.classList.add("motion-field");
    const layers = () => Array.from(element.querySelectorAll("[data-motion-layer]"));

    const runner = makeFrameRunner(({ x, y }) => {
      const rect = element.getBoundingClientRect();
      const localX = x - rect.left;
      const localY = y - rect.top;
      const nx = localX / Math.max(rect.width, 1) - 0.5;
      const ny = localY / Math.max(rect.height, 1) - 0.5;
      light.style.transform = `translate3d(${(localX - 310).toFixed(1)}px, ${(localY - 310).toFixed(1)}px, 0)`;
      mesh.style.translate = `${(nx * 28).toFixed(2)}px ${(ny * 18).toFixed(2)}px`;
      for (const layer of layers()) {
        const factor = Math.max(-1.8, Math.min(Number(layer.dataset.motionLayer) || 0.75, 1.8));
        layer.style.translate = `${(nx * factor * 30).toFixed(2)}px ${(ny * factor * 22).toFixed(2)}px`;
      }
    });
    const onMove = (event) => runner({ x: event.clientX, y: event.clientY });
    const onEnter = () => element.classList.add("is-field-active");
    const onLeave = () => {
      runner.cancel();
      element.classList.remove("is-field-active");
      light.style.transform = "translate3d(-680px, -680px, 0)";
      mesh.style.translate = "0 0";
      for (const layer of layers()) layer.style.translate = "0 0";
    };
    element.addEventListener("pointerenter", onEnter, { passive: true });
    element.addEventListener("pointermove", onMove, { passive: true });
    element.addEventListener("pointerleave", onLeave, { passive: true });
    addCleanup(element, () => {
      runner.cancel();
      element.removeEventListener("pointerenter", onEnter);
      element.removeEventListener("pointermove", onMove);
      element.removeEventListener("pointerleave", onLeave);
      for (const layer of layers()) layer.style.translate = "";
      light.remove();
      mesh.remove();
      element.classList.remove("motion-field", "is-field-active");
    });
  },
  beforeUnmount(element) {
    cleanupElement(element);
  },
};

// A small contextual cursor badge for high-value media and navigation surfaces.
// It supplements the native cursor instead of replacing it, and is disabled on touch.
let cursorBadge = null;
let cursorOwner = null;
function ensureCursorBadge() {
  if (cursorBadge?.isConnected) return cursorBadge;
  const badge = document.createElement("span");
  badge.className = "motion-cursor-badge";
  badge.setAttribute("aria-hidden", "true");
  badge.innerHTML = "<i></i><b></b>";
  document.body.appendChild(badge);
  cursorBadge = badge;
  return badge;
}
function hideCursorBadge(owner) {
  if (owner && cursorOwner !== owner) return;
  cursorOwner = null;
  cursorBadge?.classList.remove("is-visible");
}

export const cursor = {
  mounted(element, binding) {
    if (!canUsePointerMotion()) return;
    const label = String(binding.value || "OPEN")
      .slice(0, 14)
      .toUpperCase();
    const runner = makeFrameRunner(({ x, y }) => {
      const badge = ensureCursorBadge();
      badge.style.transform = `translate3d(${(x + 18).toFixed(1)}px, ${(y + 16).toFixed(1)}px, 0)`;
    });
    const onEnter = (event) => {
      const badge = ensureCursorBadge();
      cursorOwner = element;
      badge.querySelector("b").textContent = label;
      badge.classList.add("is-visible");
      runner({ x: event.clientX, y: event.clientY });
    };
    const onMove = (event) => runner({ x: event.clientX, y: event.clientY });
    const onLeave = () => {
      runner.cancel();
      hideCursorBadge(element);
    };
    element.addEventListener("pointerenter", onEnter, { passive: true });
    element.addEventListener("pointermove", onMove, { passive: true });
    element.addEventListener("pointerleave", onLeave, { passive: true });
    addCleanup(element, () => {
      runner.cancel();
      element.removeEventListener("pointerenter", onEnter);
      element.removeEventListener("pointermove", onMove);
      element.removeEventListener("pointerleave", onLeave);
      hideCursorBadge(element);
    });
  },
  beforeUnmount(element) {
    cleanupElement(element);
  },
};

reducedMotion.addEventListener("change", () => {
  if (!reducedMotion.matches) return;
  for (const animation of running) animation.cancel();
});
