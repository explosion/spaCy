param (
    [string]$python = $(throw "-python is required."),
    [string]$install_mode = $(throw "-install_mode is required."),
    [string]$pip_date
)
 
if(!(Test-Path -Path ".build"))
{
    virtualenv .build --python $python
}
.build\Scripts\activate.ps1

python build.py $python $install_mode $pip_date
