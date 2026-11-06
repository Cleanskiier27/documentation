$ErrorActionPreference = 'Stop'

$tools = @(
    @{ Name = 'dotnet'; Command = 'dotnet' },
    @{ Name = 'python'; Command = 'python' },
    @{ Name = 'py'; Command = 'py' },
    @{ Name = 'node'; Command = 'node' },
    @{ Name = 'docker'; Command = 'docker' }
)

Write-Host 'Runtime audit:' -ForegroundColor Cyan
foreach ($tool in $tools) {
    $result = Get-Command $tool.Command -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host ("[OK] {0}: {1}" -f $tool.Name, $result.Source) -ForegroundColor Green
    }
    else {
        Write-Host ("[MISSING] {0}" -f $tool.Name) -ForegroundColor Yellow
    }
}

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Warning 'Missing .NET SDK is the actual reason the C# build crashed in the prior startup flow.'
}
