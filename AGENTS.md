squint is a self-hostable document processing pipeline focused on efficiency and a streamlined developer experience.

Use `task --list` to find common project lifecycle commands.

Do not start long running background tasks like `tilt up` inside the agent shell. Use `tilt get session -o yaml` to check if a Tilt session is running. If so, use `tilt logs --json --follow` to stream logs. If not, prompt the user to start `tilt up` or give permission to run `tilt ci`.

All squint services in the dev cluster run with a debugger port open. `.vscode/launch.json` contains the source mappings and debug ports. Use the `debug-live` skill and `debugmcp` MCP server instead of resorting to print-line debugging.

Use `task remove-user EMAIL=<email>` to clean up test accounts unless leaving them is required for further debugging.

Pass `--interactive=false` to `kubectl delete`. Otherwise it prompts for confirmation, which cancels the delete in an agent shell.

Use code comments sparingly; prefer descriptive code instead.
