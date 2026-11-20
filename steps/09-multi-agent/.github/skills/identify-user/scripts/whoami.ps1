# Prints the current user's name and local time as one line of JSON.
# Works in Windows PowerShell 5.1 and PowerShell 7. Nothing to install.
$name = ""
try { $name = (git config user.name) 2>$null } catch {}
$hour = (Get-Date).Hour
$part = if ($hour -lt 12) { "morning" } elseif ($hour -lt 18) { "afternoon" } else { "evening" }
[ordered]@{
  name        = "$name"
  username    = $env:USERNAME
  os          = "Windows"
  local_time  = (Get-Date -Format "HH:mm")
  part_of_day = $part
} | ConvertTo-Json -Compress
