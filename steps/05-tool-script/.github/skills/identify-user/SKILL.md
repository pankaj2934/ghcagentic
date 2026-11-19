---
name: identify-user
description: Find out who the current user is (their name) and what time it is on their machine. Use this when asked to greet "me", or whenever you need the user's name or local time and they haven't told you.
---

# Identify the current user

Run the script that matches the user's operating system. Run it from the
workspace root and don't change it.

- **Windows (PowerShell):**
  `powershell -NoProfile -ExecutionPolicy Bypass -File .github/skills/identify-user/scripts/whoami.ps1`
- **macOS / Linux:**
  `bash .github/skills/identify-user/scripts/whoami.sh`

The script prints one line of JSON, for example:

```json
{"name":"Pankaj Kumar","username":"pankaj","os":"Windows","local_time":"14:05","part_of_day":"afternoon"}
```

Use `name` (first name only) as the person's name and `part_of_day` for the
time-of-day phrase. If `name` is empty, use `username`.
