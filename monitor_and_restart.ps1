while ($true) {
    if (Test-Path "D:\voice-check\voice-check\accuracy_report.txt") {
        Write-Host "Training complete. Restarting python server..."
        taskkill /F /IM python.exe /T
        Start-Sleep -Seconds 2
        start "AuthGuard Python AI" /MIN cmd /c "cd /d D:\voice-check\voice-check && python run.py"
        break
    }
    Start-Sleep -Seconds 10
}
