squint is a self-hostable document processing pipeline focused on efficiency and a streamlined developer experience.

Use `task --list` to find common project lifecycle commands.

Do not start long running background tasks like `tilt up` inside the agent shell. Use `tilt get session -o yaml` to check if a Tilt session is running. If so, use `tilt logs --json --follow` to stream logs, otherwise use `tilt ci`.

Use `task remove-user EMAIL=<email>` to clean up test accounts unless leaving them is required for further debugging.

Use code comments sparingly; prefer descriptive code instead.
