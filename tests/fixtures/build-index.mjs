import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Test-only stand-in for the factory index builder. These fields are deliberately
// named here so the asset policy tests remain hermetic and still cover the
// durable review contract.
const REVIEW_FIELDS = [
  "description",
  "tags",
  "status",
  "notes",
  "resolution_warning",
  "acceptance_basis",
];

const catalogRoot = path.dirname(fileURLToPath(import.meta.url));
const libraryRoot = path.resolve(catalogRoot, "..");
const factoryRoot = path.resolve(libraryRoot, "..");
const metadataPath = path.join(catalogRoot, "metadata.json");
const outputPath = path.join(catalogRoot, "assets.json");

function readJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return fallback;
    throw error;
  }
}

function findManifestAssets(root) {
  const results = [];
  if (!fs.existsSync(root)) return results;
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const entryPath = path.join(root, entry.name);
    if (entry.isDirectory()) {
      results.push(...findManifestAssets(entryPath));
    } else if (entry.name === "assets.json" && path.basename(path.dirname(entryPath)) === "manifest") {
      const payload = readJson(entryPath, { assets: [] });
      results.push(...(Array.isArray(payload.assets) ? payload.assets : []));
    }
  }
  return results;
}

function resolveAssetPath(record) {
  if (!record.path) return null;
  return path.isAbsolute(record.path)
    ? record.path
    : path.resolve(libraryRoot, record.path);
}

const metadata = readJson(metadataPath, { assets: {} });
const discovered = findManifestAssets(path.join(factoryRoot, "projects"));
const existing = readJson(outputPath, { assets: [] });
const byId = new Map();

for (const record of [...(Array.isArray(existing.assets) ? existing.assets : []), ...discovered]) {
  if (record && record.asset_id) byId.set(record.asset_id, record);
}

const assets = [...byId.values()].map((record) => {
  const manual = metadata.assets?.[record.asset_id] || {};
  const merged = { ...record, ...manual };
  const resolvedPath = resolveAssetPath(record);
  const stat = resolvedPath && fs.existsSync(resolvedPath) ? fs.statSync(resolvedPath) : null;
  return {
    ...merged,
    file_exists: Boolean(stat),
    file_size_bytes: stat ? stat.size : 0,
    path: record.path,
  };
});

fs.writeFileSync(
  outputPath,
  JSON.stringify(
    {
      schema_version: 1,
      library_id: "report-video-asset-library",
      root: "asset-library",
      resolution_key: "asset_id",
      review_fields: REVIEW_FIELDS,
      assets,
    },
    null,
    2,
  ) + "\n",
  "utf8",
);
