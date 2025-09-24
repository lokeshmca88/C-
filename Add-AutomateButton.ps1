param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [string]$ButtonText = 'Automate',

    [Parameter(Mandatory = $false)]
    [ValidateSet('TopLeft','TopRight','BottomLeft','BottomRight','Center')]
    [string]$Position = 'TopRight',

    [Parameter(Mandatory = $false)]
    [int]$OffsetX = 20,

    [Parameter(Mandatory = $false)]
    [int]$OffsetY = 12,

    [Parameter(Mandatory = $false)]
    [int]$ButtonWidth = 200,

    [Parameter(Mandatory = $false)]
    [int]$ButtonHeight = 48,

    [Parameter(Mandatory = $false)]
    [string]$ButtonFill = '#0078D4',

    [Parameter(Mandatory = $false)]
    [string]$ButtonStroke = '#005A9E',

    [Parameter(Mandatory = $false)]
    [int]$StrokeWidth = 2,

    [Parameter(Mandatory = $false)]
    [string]$TextColor = 'white',

    [Parameter(Mandatory = $false)]
    [string]$Font = 'Segoe UI',

    [Parameter(Mandatory = $false)]
    [int]$FontSize = 22
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "Input image not found: $InputPath"
}

if (-not $OutputPath) {
    $dir = Split-Path -Parent $InputPath
    $name = Split-Path -Leaf $InputPath
    $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
    $ext  = [System.IO.Path]::GetExtension($name)
    $OutputPath = Join-Path $dir ("{0}_with_{1}{2}" -f $base, ($ButtonText -replace '\s+','_'), $ext)
}

# Resolve ImageMagick executable name
$magick = Get-Command magick -ErrorAction SilentlyContinue
if (-not $magick) { $magick = Get-Command magick-im7.q16 -ErrorAction SilentlyContinue }
if (-not $magick) { $magick = Get-Command magick.exe -ErrorAction SilentlyContinue }
if (-not $magick) {
    throw 'ImageMagick (magick) not found on PATH. Install ImageMagick and retry.'
}

# Create a temporary button image
$tempDir = [System.IO.Path]::GetTempPath()
$buttonPng = Join-Path $tempDir ("automate_btn_{0}.png" -f ([System.Guid]::NewGuid().ToString('N')))

try {
    $round = [Math]::Max([Math]::Round([Math]::Min($ButtonWidth,$ButtonHeight) * 0.25), 10)
    & $magick -size "${ButtonWidth}x${ButtonHeight}" xc:none `
        -fill $ButtonFill -stroke $ButtonStroke -strokewidth $StrokeWidth `
        -draw "roundrectangle 1,1 $($ButtonWidth-1),$($ButtonHeight-1) $round,$round" `
        -gravity center -font $Font -pointsize $FontSize -fill $TextColor `
        -annotate 0 "$ButtonText" `
        "$buttonPng"

    # Map friendly position names to ImageMagick gravity
    $gravity = switch ($Position) {
        'TopLeft' {'northwest'}
        'TopRight' {'northeast'}
        'BottomLeft' {'southwest'}
        'BottomRight' {'southeast'}
        'Center' {'center'}
    }

    & $magick "$InputPath" "$buttonPng" -gravity $gravity -geometry "+$OffsetX+$OffsetY" -composite "$OutputPath"

    Write-Host "Saved: $OutputPath"
}
finally {
    if (Test-Path -LiteralPath $buttonPng) { Remove-Item -LiteralPath $buttonPng -Force -ErrorAction SilentlyContinue }
}

