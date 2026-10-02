# Website fonts

These WOFF2 files are served with the website. Visitors do not need to connect to
Google Fonts. Vite hashes the text font filenames for caching and embeds the
Material Symbols subset in the built CSS via `?inline`, preventing a separate
icon font request and visible icon ligature names on slow connections.

Manrope (400–800) and Caveat (500–600) retain their variable weights and Latin
coverage. Chinese text uses the existing system font stack. Both text fonts use
`font-display: optional`: slow first visits keep the system font for that page,
without swapping much later and moving the layout. Fast or cached visits can use
the custom fonts. The loading screen always uses a system font.

Material Symbols Rounded keeps variable weights (300–600), including the 380
weight used by the signature. Unused axes are fixed to the standard UI values:
optical size 24, fill 0, grade 0. It includes names in icon spans (including
conditional branches), `icon` data properties and `icon` props. `icons.json`
records that subset. Rerun the script when adding icons and review this list if
introducing another way to choose icon names.

From `website/`, refresh the checked-in assets with Node 22 or newer:

```sh
node scripts/update-fonts.mjs
```

When using an HTTP(S) proxy, use Node 22.21+ and run
`node --use-env-proxy scripts/update-fonts.mjs`.

This is a maintenance command that needs internet access, not a build step.
Normal development and builds use the checked-in assets and work offline.

Sources:

- [Google Fonts CSS API](https://developers.google.com/fonts/docs/css2)
- [Material Symbols](https://developers.google.com/fonts/docs/material_symbols)
- [Manrope license](./OFL-Manrope.txt): SIL Open Font License 1.1
- [Caveat license](./OFL-Caveat.txt): SIL Open Font License 1.1
- [Material Symbols license](./Apache-2.0.txt): Apache License 2.0
