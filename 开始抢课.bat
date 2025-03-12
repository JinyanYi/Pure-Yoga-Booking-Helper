@echo off
setlocal

:: Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git未安装, 安装中...

    :: Check if winget is available (Windows 10/11)
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo 使用winget安装Git...
        winget install --id Git.Git -e --source winget
    ) else (
        echo Winget未安装, 请手动安装Git从https://git-scm.com/download/win
        pause
        exit /b 1
    )
)

:: Git is installed, continue updating repo
echo Git已安装. 继续更新代码...

git fetch --all
git reset --hard origin/main
git pull origin main

echo 更新完成!

python start_booking.py 