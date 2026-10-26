$msiPath = (Resolve-Path "dist/Touchline-Analizador-FM26.msi").Path
$installer = New-Object -ComObject WindowsInstaller.Installer
$db = $installer.GetType().InvokeMember("OpenDatabase", "InvokeMethod", $null, $installer, @($msiPath, 0))

Write-Host "=== MSI PROPERTIES ==="
$view = $db.GetType().InvokeMember("OpenView", "InvokeMethod", $null, $db, @("SELECT Property, Value FROM Property"))
$view.GetType().InvokeMember("Execute", "InvokeMethod", $null, $view, $null)
while ($rec = $view.GetType().InvokeMember("Fetch", "InvokeMethod", $null, $view, $null)) {
    $prop = $rec.GetType().InvokeMember("StringData", "GetProperty", $null, $rec, @(1))
    $val = $rec.GetType().InvokeMember("StringData", "GetProperty", $null, $rec, @(2))
    Write-Host "$prop = $val"
}

Write-Host "`n=== SHORTCUTS ==="
$view = $db.GetType().InvokeMember("OpenView", "InvokeMethod", $null, $db, @("SELECT Shortcut, Directory_, Name, Target FROM Shortcut"))
$view.GetType().InvokeMember("Execute", "InvokeMethod", $null, $view, $null)
while ($rec = $view.GetType().InvokeMember("Fetch", "InvokeMethod", $null, $view, $null)) {
    $id = $rec.GetType().InvokeMember("StringData", "GetProperty", $null, $rec, @(1))
    $dir = $rec.GetType().InvokeMember("StringData", "GetProperty", $null, $rec, @(2))
    $name = $rec.GetType().InvokeMember("StringData", "GetProperty", $null, $rec, @(3))
    $target = $rec.GetType().InvokeMember("StringData", "GetProperty", $null, $rec, @(4))
    Write-Host "$id in $dir -> $name (Target: $target)"
}

Write-Host "`n=== FILE COUNT ==="
$view = $db.GetType().InvokeMember("OpenView", "InvokeMethod", $null, $db, @("SELECT File FROM File"))
$view.GetType().InvokeMember("Execute", "InvokeMethod", $null, $view, $null)
$count = 0
while ($rec = $view.GetType().InvokeMember("Fetch", "InvokeMethod", $null, $view, $null)) {
    $count++
}
Write-Host "Total files packaged: $count"
