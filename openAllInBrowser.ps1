$lines = Get-Content -Path input.txt
$lines | ForEach-Object {
   Start-Process https://pl.pons.com/t%C5%82umaczenie/niemiecki-polski/$_ 
}