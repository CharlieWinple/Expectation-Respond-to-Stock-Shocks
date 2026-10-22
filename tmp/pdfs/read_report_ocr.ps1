$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.DataWriter,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null=[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null=[Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime]
$asTask=([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'})[0]
function AwaitOp($op,$type){$task=$asTask.MakeGenericMethod($type).Invoke($null,@($op));try{$task.Wait()}catch{Write-Output $_.Exception.ToString();throw};$task.Result}
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('en-US'))
$folder='D:\wyp_Files\xx.Files\data\CSMAR_fund_202608\20260823 exp stock\outputs\platform_runs\sme_rf_wave_cell_diagnostics\run_001\batch4_pages'
foreach($img in Get-ChildItem -LiteralPath $folder -Filter *.png){
 $stream=New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
 $writer=New-Object Windows.Storage.Streams.DataWriter($stream)
 $writer.WriteBytes([IO.File]::ReadAllBytes($img.FullName))
 $null=AwaitOp ($writer.StoreAsync()) ([uint32])
 $stream.Seek(0)
 $decoder=AwaitOp ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
 $bitmap=AwaitOp ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
 $result=AwaitOp ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
 $lines=@($result.Lines | ForEach-Object { $_.Text })
 [IO.File]::WriteAllLines(($img.FullName+'.ocr.txt'),$lines,[Text.Encoding]::UTF8)
 $bitmap.Dispose();$stream.Dispose()
 Write-Output $img.Name
}

