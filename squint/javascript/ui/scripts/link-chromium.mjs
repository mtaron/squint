// Points .playwright-mcp/chromium at the installed Chromium so the Playwright MCP's
// PLAYWRIGHT_MCP_EXECUTABLE_PATH survives Playwright upgrades, which change the revision directory.
import { existsSync, mkdirSync, rmSync, symlinkSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const executable = chromium.executablePath();
if (!existsSync(executable)) process.exit(0);

const linkDir = resolve(dirname(fileURLToPath(import.meta.url)), "../../../../.playwright-mcp");
const link = resolve(linkDir, "chromium");
mkdirSync(linkDir, { recursive: true });
rmSync(link, { force: true });
symlinkSync(dirname(executable), link);
