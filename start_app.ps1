$backend = Start-Process python -ArgumentList "-m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru
Write-Host "Backend started with PID: $($backend.Id)"

Set-Location "src/frontend"
$frontend = Start-Process npm -ArgumentList "run dev" -PassThru
Write-Host "Frontend started with PID: $($frontend.Id)"

Write-Host "App is running!"
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:5173"
Write-Host "Press any key to stop servers..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Stop-Process -Id $backend.Id -Force
Stop-Process -Id $frontend.Id -Force
Write-Host "Stopped."
