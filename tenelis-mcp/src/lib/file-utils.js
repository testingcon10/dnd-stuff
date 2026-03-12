import path from "path";
import { fileURLToPath } from "url";
import { mkdirSync } from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const VAULT_ROOT = path.resolve(__dirname, "../../../Tenelis");
export const ASSETS_DIR = path.join(VAULT_ROOT, "assets");

export function slugify(name) {
  return name
    .toLowerCase()
    .replace(/'/g, "-")
    .replace(/\.\s/g, "-")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export function slugifyScene(desc) {
  const words = desc.split(/\s+/).slice(0, 5).join(" ");
  return slugify(words);
}

export function getAssetPath(category, filename) {
  const dir = path.join(ASSETS_DIR, category);
  mkdirSync(dir, { recursive: true });
  return path.join(dir, filename);
}

export function getRelativeAssetPath(category, filename) {
  return `assets/${category}/${filename}`;
}
