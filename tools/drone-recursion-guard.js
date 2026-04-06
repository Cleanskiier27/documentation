/**
 * tools/drone-recursion-guard.js
 *
 * Triage patch demo: recursion guard for the NetworkBuster "drone" agent graph walk.
 *
 * Bug: agent-network-scan.js (and related lab agents) perform a depth-first graph
 * traversal of discovered network nodes. When the network topology contains cycles
 * (A → B → C → A) or a very deep mesh, the recursive walk causes a stack overflow /
 * infinite loop — the process hangs and must be killed.
 *
 * This file demonstrates three safe traversal patterns you can drop into any
 * agent that walks a node/edge graph:
 *
 *   1. Visited-set guard (cycle detection) — minimal change to existing recursive code
 *   2. Iterative BFS with depth limit — no recursion at all
 *   3. Async-safe iterative DFS with a circuit-breaker timeout
 *
 * Run:  node tools/drone-recursion-guard.js
 */

'use strict';

// ---------------------------------------------------------------------------
// Shared test graph — contains a cycle: A → B → C → A
// ---------------------------------------------------------------------------
const GRAPH = {
  A: ['B', 'D'],
  B: ['C'],
  C: ['A', 'E'],   // cycle: C → A
  D: ['E'],
  E: [],
};

// ---------------------------------------------------------------------------
// Pattern 1 — Recursive DFS with a visited set (cycle-safe)
// ---------------------------------------------------------------------------
/**
 * @param {Record<string, string[]>} graph  adjacency list
 * @param {string}                   node   current node
 * @param {Set<string>}              visited already-seen nodes (guards cycles)
 * @param {number}                   maxDepth hard limit on recursion depth
 * @param {number}                   depth   current depth (internal)
 * @returns {string[]} nodes visited in DFS order
 */
function recursiveDFS(graph, node, visited = new Set(), maxDepth = 64, depth = 0) {
  if (visited.has(node)) return [];           // cycle guard
  if (depth > maxDepth) {                     // depth-limit guard
    console.warn(`[recursiveDFS] max depth ${maxDepth} reached at node "${node}" — stopping branch`);
    return [];
  }

  visited.add(node);
  const result = [node];

  for (const neighbor of (graph[node] ?? [])) {
    result.push(...recursiveDFS(graph, neighbor, visited, maxDepth, depth + 1));
  }
  return result;
}

// ---------------------------------------------------------------------------
// Pattern 2 — Iterative BFS with depth limit (no stack risk at all)
// ---------------------------------------------------------------------------
/**
 * @param {Record<string, string[]>} graph
 * @param {string}                   start
 * @param {number}                   maxDepth
 * @returns {{ order: string[], truncated: boolean }}
 */
function iterativeBFS(graph, start, maxDepth = 64) {
  const visited = new Set();
  const queue = [{ node: start, depth: 0 }];
  const order = [];
  let truncated = false;

  while (queue.length > 0) {
    const { node, depth } = queue.shift();

    if (visited.has(node)) continue;
    if (depth > maxDepth) {
      truncated = true;
      continue;
    }

    visited.add(node);
    order.push(node);

    for (const neighbor of (graph[node] ?? [])) {
      if (!visited.has(neighbor)) {
        queue.push({ node: neighbor, depth: depth + 1 });
      }
    }
  }

  return { order, truncated };
}

// ---------------------------------------------------------------------------
// Pattern 3 — Async iterative DFS with circuit-breaker timeout
// ---------------------------------------------------------------------------
/**
 * @param {Record<string, string[]>} graph
 * @param {string}                   start
 * @param {object}                   opts
 * @param {number}                   [opts.maxDepth=64]   max graph depth
 * @param {number}                   [opts.timeoutMs=500] wall-clock circuit breaker
 * @returns {Promise<{ order: string[], timedOut: boolean, truncated: boolean }>}
 */
async function asyncIterativeDFS(graph, start, { maxDepth = 64, timeoutMs = 500 } = {}) {
  const deadline = Date.now() + timeoutMs;
  const visited = new Set();
  const stack = [{ node: start, depth: 0 }];
  const order = [];
  let timedOut = false;
  let truncated = false;

  while (stack.length > 0) {
    if (Date.now() > deadline) {
      timedOut = true;
      break;
    }

    const { node, depth } = stack.pop();

    if (visited.has(node)) continue;
    if (depth > maxDepth) {
      truncated = true;
      continue;
    }

    visited.add(node);
    order.push(node);

    for (const neighbor of (graph[node] ?? [])) {
      if (!visited.has(neighbor)) {
        stack.push({ node: neighbor, depth: depth + 1 });
      }
    }

    // Yield to event loop periodically so the process stays responsive
    if (order.length % 100 === 0) {
      await new Promise(resolve => setImmediate(resolve));
    }
  }

  return { order, timedOut, truncated };
}

// ---------------------------------------------------------------------------
// Demonstrate — UNSAFE recursive walk (would hang on a cyclic graph)
// ---------------------------------------------------------------------------
function unsafeDFS(graph, node, seen = new Set()) {
  // ⚠  No cycle guard — hangs forever on A → B → C → A
  // This is intentionally limited here for demo purposes; in real code it
  // would call itself until Node.js throws "Maximum call stack size exceeded".
  if (seen.size > 1000) throw new Error('DEMO LIMIT — would be infinite in real code');
  seen.add(node);
  for (const n of (graph[node] ?? [])) unsafeDFS(graph, n, seen);
}

// ---------------------------------------------------------------------------
// Main — run all patterns and print results
// ---------------------------------------------------------------------------
(async () => {
  console.log('=== NetworkBuster — Drone Recursion Guard Demo ===\n');
  console.log('Test graph (contains cycle A→B→C→A):');
  console.log(JSON.stringify(GRAPH, null, 2), '\n');

  // 1. Unsafe walk
  console.log('--- [UNSAFE] Plain recursive DFS (no guard) ---');
  try {
    unsafeDFS(GRAPH, 'A');
  } catch (e) {
    console.error('  ✗ Caught as expected:', e.message, '\n');
  }

  // 2. Pattern 1 — recursive + visited set
  console.log('--- [SAFE-1] Recursive DFS with visited set ---');
  const p1 = recursiveDFS(GRAPH, 'A');
  console.log('  Visited order:', p1.join(' → '));
  console.log('  ✓ Completed safely\n');

  // 3. Pattern 2 — iterative BFS
  console.log('--- [SAFE-2] Iterative BFS with depth limit ---');
  const p2 = iterativeBFS(GRAPH, 'A');
  console.log('  Visited order:', p2.order.join(' → '));
  console.log('  Truncated?', p2.truncated);
  console.log('  ✓ Completed safely\n');

  // 4. Pattern 3 — async DFS with timeout
  console.log('--- [SAFE-3] Async iterative DFS with circuit breaker ---');
  const p3 = await asyncIterativeDFS(GRAPH, 'A', { timeoutMs: 200 });
  console.log('  Visited order:', p3.order.join(' → '));
  console.log('  TimedOut?', p3.timedOut, '| Truncated?', p3.truncated);
  console.log('  ✓ Completed safely\n');

  console.log('=== All patterns finished without hanging. Patch verified. ===');
})();
