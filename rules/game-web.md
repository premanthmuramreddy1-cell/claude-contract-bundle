Pairs with → design.md (shared tokens), swarm.md (trinity for game builds), human-output.md (game-world feel), master §25G.

# PART 12G — GAME ENGINE, WEBGL & REAL-TIME WEB PROTOCOL

> **Scope:** Canvas, WebGL, Three.js, Pixi.js, Babylon, Phaser, WebSockets, WebRTC, and real-time interactive game systems.
> **Loading Trigger:** Any task touching game logic, 2D/3D canvas rendering, asset pipelines, or live socket synchronization.

---

## §25G.1 Frame Budget & Loop Discipline (60/120 FPS Rule)

Every interactive loop (`requestAnimationFrame`, canvas render tick, or game loop) is strictly budgeted:
* **Target Budget:** ≤16.6ms per frame (60 FPS) · ≤8.3ms per frame (120 FPS).
* **Zero Allocation in Loop:** Never instantiate objects (`new Vector3()`, `new Object()`), allocate closures/lambdas, or resize arrays inside the render/update tick.
* **Object Pooling:** Pre-allocate bullet pools, particle arrays, vector math scratchpads, and temporary matrices at startup.
* **Fixed vs Variable Delta:** Decouple physics from rendering. Use a fixed timestep accumulator (e.g. `1/60s`) for collision and physics; interpolate transforms for rendering.

```
TICK DISCIPLINE:
  RAF Tick ──► Read Inputs ──► Fixed Physics Step (accumulated) ──► Interpolate ──► Render ──► (sleep/yield)
  [CRITICAL: If physics step takes >100ms, clamp accumulator to prevent "spiral of death"]
```

---

## §25G.2 Context & GPU Lifecycle (Disposal Contract)

WebGL contexts and GPU memory are finite and DO NOT garbage collect automatically. Memory leaks will crash client browser tabs.
* **Component Unmount Contract:** On React/Vue/Svelte unmount or screen transition:
  * Traversed scene graph: `.dispose()` on every geometry, material, texture, render target, and shader program.
  * Stop render loop: `cancelAnimationFrame(rafId)`.
  * Audio context: Close or suspend `AudioContext` and disconnect source nodes.
  * WebGL Context loss handler: Listen to `webglcontextlost` and prevent default to handle graceful reload or warning.
* **DOM Event Cleanup:** Remove pointer locks, resize listeners, and keyboard listeners explicitly.

---

## §25G.3 Asset Optimization & Delivery Gates

Never ship raw desktop-sized 3D or media assets to a web client.
* **3D Geometry:** glTF/GLB Draco-compressed or Meshopt. Check total triangle budget (<100k polygons for mobile web target).
* **Textures:** Use WebP or Basis/KTX2 compressed textures. Max texture dimensions: 2048×2048 for hero assets, 1024×1024 or smaller for general sprites/materials. Enable mipmaps.
* **Audio:** Opus/OGG for music/sfx (MP3 fallback). Stream long background music, buffer short SFX.
* **Autoplay Compliance:** Audio context must initialize suspended and resume only after the first user gesture (`pointerdown` or `keydown`).
* **Preloader Contract:** Always provide an explicit asset loader with progress feedback (`loaded / total`) and failure retry/timeout.

---

## §25G.4 Real-Time Networking & Socket Protocol

For WebSocket, PartyKit, Colyseus, or socket.io real-time game state:
* **Connection Lifecycle State Machine:**
  * States: `DISCONNECTED` ──► `CONNECTING` ──► `CONNECTED` ──► `RECONNECTING` ──► `FAILED`.
  * **Exponential Backoff:** Initial 500ms, doubling up to 10s cap + random jitter (±20%) to prevent thundering herd on server restarts.
  * **Heartbeat:** Ping/Pong interval every 15–30s. If 2 consecutive heartbeats fail, transition to `RECONNECTING`.
* **State Synchronization & Delta Encoding:**
  * Never broadcast entire room/game state on every tick.
  * Broadcast delta updates: only changed entities or compressed binary payloads.
  * Messages must include sequence IDs and timestamps: `{ seq: 1042, t: 1712345678, type: "PLAYER_MOVE", data: {...} }`.
* **Client-side Prediction & Reconciliation:**
  * For player movement, apply inputs locally immediately. Reconcile smoothly against authoritative server snapshots.
  * Interpolate remote entities over a 50–100ms interpolation buffer.
* **Clean Session Termination:**
  * Handle `window.beforeunload` to emit an explicit leave event.
  * Support room rejoin tokens to reconnect dropped players within a 60-second grace window without resetting game progress.

---

## §25G.5 Dev Server & Safe Port Hygiene

Multi-tier game web stacks (Vite UI + Node Game Server + WebSocket gateway) frequently leave zombie processes or collide on ports.
* **Port Matrix:**
  * Frontend Dev: `3000` / `5173`
  * API / Backend: `4000` / `8000` / `8080`
  * WebSocket Gateway: `3001` / `8081`
* **Safe Pre-flight Port Sweep:**
  * Before starting a dev server or running E2E suites:
    ```bash
    # Check what process holds the target port before terminating:
    lsof -i :<port> -sTCP:LISTEN
    # Terminate cleanly only if it is an orphaned node/vite runner:
    lsof -ti :<port> | xargs kill -15 2>/dev/null || true
    ```
  * **Safety Guard:** Never kill processes outside the expected web stack (e.g. system services, Docker, system databases). If unsure, check `ps -p <pid> -o command=`.
* **Graceful Process Shutdown:** In server scripts, hook `SIGINT` and `SIGTERM` to close socket connections, flush metrics/logs, and terminate listeners cleanly.
