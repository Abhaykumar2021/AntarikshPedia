/**
 * search.js — fuzzy search over the mission record using Fuse.js
 * (vendored ESM build in ./vendor/fuse.mjs — no bundler required).
 */

import Fuse from './vendor/fuse.mjs';

/**
 * Build a search index over missions.
 *
 * @param {Array<Object>} missions - Mission records.
 * @returns {Fuse} Configured Fuse instance.
 */
export function createSearchIndex(missions) {
  return new Fuse(missions, {
    keys: [
      { name: 'name', weight: 3 },
      { name: 'lead_partner', weight: 1 },
      { name: 'target', weight: 1 },
      { name: 'category', weight: 0.5 },
      { name: 'outcome', weight: 0.5 },
    ],
    threshold: 0.34,      // tolerant of misspellings like "voyagr"
    ignoreLocation: true,
    minMatchCharLength: 2,
  });
}

/**
 * Run a query and cap the result list.
 *
 * @param {Fuse} index - Index from createSearchIndex.
 * @param {string} query - Raw user text.
 * @param {number} [limit=8] - Max results.
 * @returns {Array<Object>} Mission records, best match first.
 */
export function fuzzySearch(index, query, limit = 8) {
  if (!query || query.trim().length < 2) return [];
  return index
    .search(query.trim(), { limit })
    .map(result => result.item);
}
