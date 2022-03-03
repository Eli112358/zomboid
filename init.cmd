@echo off
path %~dp0src;%path%
pushd %userprofile%\Zomboid
%~dp0venv\Scripts\activate 2>nul
cls
