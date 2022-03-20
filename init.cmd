@echo off
where python>nul || goto missing_python
if not exist %~dp0venv call :missing_venv
path %~dp0src;%path%
pushd %userprofile%\Zomboid\Saves
prompt ~\Zomboid$+$g
cls
echo Reminder: Don't forget to cd/pushd into the save game directory (or use -t and -n)
call %~dp0venv\Scripts\activate
exit/b
:missing_venv
pushd %~dp0
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
popd
exit/b
:missing_python
echo Please install Python 3
