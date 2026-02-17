# Concatenate all files in the current directory tree into a single file
# WARNING: This will include source code contents; review before sharing externally.
# Usage: pwsh -File scripts/ConcatAllFiles.ps1 -Output Combined.txt

param(
    [string]$Root = (Get-Location).Path,
    [string]$Output = "Combined.txt",
    [string[]]$IncludeExtensions = @(".py", ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".js", ".css")
)

Write-Host "Concatenating files under $Root ..."
$excludeDirs = @(".git", "node_modules", "__pycache__", "venv", ".venv", "logs", "output")

$targets = Get-ChildItem -Path $Root -Recurse -Force -File |
    Where-Object {
        $ext = [System.IO.Path]::GetExtension($_.Name)
        $relative = $_.FullName.Substring($Root.Length)
        ($IncludeExtensions -contains $ext) -and (
            ($relative -notmatch "\\\\.git\\\\") -and
            ($relative -notmatch "\\\\node_modules\\\\") -and
            ($relative -notmatch "\\\\__pycache__\\\\") -and
            ($relative -notmatch "\\\\venv\\\\|\\\\.venv\\\\") -and
            ($relative -notmatch "\\\\logs\\\\") -and
            ($relative -notmatch "\\\\output\\\\")
        )
    }

$writer = New-Object System.IO.StreamWriter (Join-Path $Root $Output), $false, (New-Object System.Text.UTF8Encoding($false))
try {
    foreach ($f in $targets) {
        $rel = $f.FullName.Substring($Root.Length + 1)
        $writer.WriteLine("\n\n===== $rel =====\n")
        try {
            $content = Get-Content -LiteralPath $f.FullName -ErrorAction Stop
            $writer.WriteLine(($content -join "`n"))
        } catch {
            $writer.WriteLine("(Failed to read: $rel)")
        }
    }
} finally {
    $writer.Dispose()
}

Write-Host "Wrote $($targets.Count) files into $Output"