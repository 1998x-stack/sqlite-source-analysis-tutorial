# SQLite WASM lab

Pinned baseline: `@sqlite.org/sqlite-wasm@3.54.1-build1`.

## Node.js smoke test

Node.js support in the official package is currently limited to in-memory databases.

```bash
npm install
npm run test:node
```

## Browser Worker + OPFS demo

```bash
npm install
npm run dev
```

The Vite server and preview server send:

- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Embedder-Policy: require-corp`

The worker checks whether the OPFS VFS is available. If it is not, it explicitly reports and uses an in-memory fallback. Do not treat that fallback as persistence. Production hosting must send the required response headers itself; GitHub Pages does not inherit Vite's local server configuration.
