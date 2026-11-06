$script:PortyDefaults = [ordered]@{
    Host = 'http://localhost'
    Origin = 8000
    Api = 8000
    Web = 3000
    Mesh = 9000
    Map = 8100
    Satellite = 8101
    Analytics = 8200
    Telemetry = 8300
    UniversalApi = 8080
}

function Test-PortAvailable {
    param([int]$Port)

    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    }
    catch {
        return $false
    }
}

function Get-PortyConfig {
    $hostBase = if ([string]::IsNullOrWhiteSpace($env:AIWORLD_HOST)) { $script:PortyDefaults.Host } else { $env:AIWORLD_HOST.TrimEnd('/') }

    $originPort = if ([string]::IsNullOrWhiteSpace($env:AIWORLD_PORT)) { $script:PortyDefaults.Origin } else { [int]$env:AIWORLD_PORT }
    $apiPort = if ([string]::IsNullOrWhiteSpace($env:SATGPU_API_PORT)) { $script:PortyDefaults.Api } else { [int]$env:SATGPU_API_PORT }
    $webPort = if ([string]::IsNullOrWhiteSpace($env:SATGPU_WEB_PORT)) { $script:PortyDefaults.Web } else { [int]$env:SATGPU_WEB_PORT }
    $meshPort = if ([string]::IsNullOrWhiteSpace($env:SATGPU_WORKER_PORT)) { $script:PortyDefaults.Mesh } else { [int]$env:SATGPU_WORKER_PORT }
    $mapPort = if ([string]::IsNullOrWhiteSpace($env:SATELLITE_MAP_PORT)) { $script:PortyDefaults.Map } else { [int]$env:SATELLITE_MAP_PORT }
    $satellitePort = if ([string]::IsNullOrWhiteSpace($env:SATELLITE_VIEW_PORT)) { $script:PortyDefaults.Satellite } else { [int]$env:SATELLITE_VIEW_PORT }
    $analyticsPort = if ([string]::IsNullOrWhiteSpace($env:ANALYTICS_PORT)) { $script:PortyDefaults.Analytics } else { [int]$env:ANALYTICS_PORT }
    $telemetryPort = if ([string]::IsNullOrWhiteSpace($env:TELEMETRY_PORT)) { $script:PortyDefaults.Telemetry } else { [int]$env:TELEMETRY_PORT }
    $universalPort = if ([string]::IsNullOrWhiteSpace($env:UNIVERSAL_API_PORT)) { $script:PortyDefaults.UniversalApi } else { [int]$env:UNIVERSAL_API_PORT }

    $resolvedPorts = [ordered]@{
        Host = $hostBase
        OriginPort = $originPort
        ApiPort = $apiPort
        WebPort = $webPort
        MeshPort = $meshPort
        MapPort = $mapPort
        SatellitePort = $satellitePort
        AnalyticsPort = $analyticsPort
        TelemetryPort = $telemetryPort
        UniversalApiPort = $universalPort
        MainOriginUrl = "${hostBase}:$originPort/index.html"
        NASAUrl = "${hostBase}:$originPort/nasa.html"
        PublicUrl = "${hostBase}:$originPort/public.html"
        UniversalApiUrl = "${hostBase}:$universalPort"
        ApiUrl = "${hostBase}:$apiPort"
        WebUrl = "${hostBase}:$webPort"
        MeshUrl = "${hostBase}:$meshPort"
        MapUrl = "${hostBase}:$mapPort"
        SatelliteUrl = "${hostBase}:$satellitePort"
        AnalyticsUrl = "${hostBase}:$analyticsPort"
        TelemetryUrl = "${hostBase}:$telemetryPort"
    }

    $keys = @($resolvedPorts.Keys)
    foreach ($key in $keys) {
        if ($resolvedPorts[$key] -is [int]) {
            $resolvedPorts[$key] = [int]$resolvedPorts[$key]
        }
    }

    $resolvedPorts['PortCheck'] = @{
        Origin = Test-PortAvailable -Port $originPort
        Api = Test-PortAvailable -Port $apiPort
        Web = Test-PortAvailable -Port $webPort
        Mesh = Test-PortAvailable -Port $meshPort
        Map = Test-PortAvailable -Port $mapPort
        Satellite = Test-PortAvailable -Port $satellitePort
        Analytics = Test-PortAvailable -Port $analyticsPort
        Telemetry = Test-PortAvailable -Port $telemetryPort
        UniversalApi = Test-PortAvailable -Port $universalPort
    }

    return [pscustomobject]$resolvedPorts
}

function Show-PortyStatus {
    $config = Get-PortyConfig
    Write-Host 'Porty port manager status:' -ForegroundColor Cyan
    foreach ($name in @('OriginPort','ApiPort','WebPort','MeshPort','MapPort','SatellitePort','AnalyticsPort','TelemetryPort','UniversalApiPort')) {
        $available = $config.PortCheck[$name.Replace('Port','')]
        $status = if ($available) { 'available' } else { 'in-use' }
        Write-Host ("  {0}: {1} ({2})" -f $name, $config.$name, $status) -ForegroundColor $(if ($available) {'Green'} else {'Yellow'})
    }
}
