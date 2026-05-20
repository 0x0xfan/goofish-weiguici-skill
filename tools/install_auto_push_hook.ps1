$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel
$hookPath = Join-Path $repoRoot ".git/hooks/post-commit"

$hook = @'
#!/bin/sh
branch="$(git branch --show-current)"
if [ -n "$branch" ]; then
  git push -u origin "$branch"
fi
'@

Set-Content -LiteralPath $hookPath -Value $hook -NoNewline -Encoding Ascii
Write-Host "Installed post-commit auto-push hook at $hookPath"
