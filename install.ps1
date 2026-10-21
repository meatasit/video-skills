$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Skills = Join-Path $env:USERPROFILE ".claude\skills"
$Agents = Join-Path $env:USERPROFILE ".claude\agents"
New-Item -ItemType Directory -Force $Skills, $Agents | Out-Null
Get-ChildItem (Join-Path $Here "skills") -Directory | ForEach-Object {
  $dst = Join-Path $Skills $_.Name
  if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
  Copy-Item $_.FullName $dst -Recurse
  Write-Host "skill   $($_.Name)"
}
Get-ChildItem (Join-Path $Here "agents") -Filter *.md | Where-Object { $_.Name -notlike "upstream-*" } | ForEach-Object {
  Copy-Item $_.FullName (Join-Path $Agents $_.Name) -Force
  Write-Host "agent   $($_.Name)"
}
if (Get-Command pip -ErrorAction SilentlyContinue) { pip install -q Pillow numpy PyYAML librosa soundfile; pip install -q -e (Join-Path $Here "skills\color-grading-skill") } else { Write-Warning "pip not found - colorist deps skipped" }
if (Get-Command npx -ErrorAction SilentlyContinue) { npx -y skills add remotion-dev/skills --agent claude-code } else { Write-Host "skip remotion (no npx)" }
foreach ($t in "ffmpeg","ffprobe","python") { if (-not (Get-Command $t -ErrorAction SilentlyContinue)) { Write-Warning "$t not found" } }
Write-Host "done - restart Claude Code"
