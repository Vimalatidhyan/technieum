# Recursively list all files in the solution and write to SolutionFileStructure.txt
# Usage: pwsh -File scripts/ListSolutionFiles.ps1

param(
    [string]$Root = (Get-Location).Path,
    [string]$Output = "SolutionFileStructure.txt"
)

Write-Host "Listing files under $Root ..."
$exclude = @(".git", "node_modules", "__pycache__", "venv", ".venv", "logs", "output")

$files = Get-ChildItem -Path $Root -Recurse -Force -File |
    Where-Object {
        $relative = $_.FullName.Substring($Root.Length)
        $exclude -notcontains ($_ | Split-Path -Leaf) -and (
            ($relative -notmatch "\\\\.git\\\\") -and
            ($relative -notmatch "\\\\node_modules\\\\") -and
            ($relative -notmatch "\\\\__pycache__\\\\") -and
            ($relative -notmatch "\\\\venv\\\\|\\\\.venv\\\\") -and
            ($relative -notmatch "\\\\logs\\\\") -and
            ($relative -notmatch "\\\\output\\\\")
        )
    } |
    ForEach-Object { $_.FullName.Substring($Root.Length + 1) }

$files | Sort-Object | Set-Content -Path (Join-Path $Root $Output)
Write-Host "Wrote $($files.Count) entries to $Output"