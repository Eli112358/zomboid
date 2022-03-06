@echo off
path %~dp0src;%path%
pushd %userprofile%\Zomboid\Saves
prompt ~\Zomboid$+$g
cls
%~dp0venv\Scripts\activate 2>nul
