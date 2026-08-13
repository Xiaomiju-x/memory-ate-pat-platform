@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions
cd /d "%~dp0"

echo =====================================================
echo  BY25Q40AL PAT Generator - 复赛版打包脚本
echo =====================================================
echo.

set "PYTHON_CMD="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if not defined PYTHON_CMD (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo [错误] 未找到 Python 3。请先安装 Python 3.10 或更高版本。
    goto :failed
)

%PYTHON_CMD% -c "import sys; raise SystemExit(0 if sys.version_info.major == 3 and sys.version_info.minor in range(10, 100) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 版本过低，要求 Python 3.10 或更高版本。
    %PYTHON_CMD% --version
    goto :failed
)

if not exist "by25q40al_pat_generator.py" (
    echo [错误] 缺少程序入口：by25q40al_pat_generator.py
    goto :failed
)

if not exist "BY25Q40AL_PAT_Generator.spec" (
    echo [错误] 缺少打包配置：BY25Q40AL_PAT_Generator.spec
    goto :failed
)

if not exist "..\..\requirements-dev.txt" (
    echo [错误] 缺少锁定的构建依赖：..\..\requirements-dev.txt
    goto :failed
)

echo [1/4] 安装锁定的构建依赖...
%PYTHON_CMD% -m pip install -r "..\..\requirements-dev.txt"
if errorlevel 1 (
    echo [错误] 构建依赖安装失败。
    goto :failed
)

echo [2/4] 运行公开回归测试...
%PYTHON_CMD% -m unittest discover -s tests -v
if errorlevel 1 (
    echo [错误] 回归测试失败，已停止打包。
    goto :failed
)

echo [3/4] 构建无第三方竞赛资产的单文件 GUI 程序...
%PYTHON_CMD% -m PyInstaller --clean --noconfirm "BY25Q40AL_PAT_Generator.spec"
if errorlevel 1 (
    echo [错误] PyInstaller 构建失败，请查看上方日志。
    goto :failed
)

if not exist "dist\BY25Q40AL_PAT_Generator.exe" (
    echo [错误] 构建命令已结束，但未找到预期的 EXE。
    goto :failed
)

echo [4/4] 构建完成。
echo.
echo 输出文件：%CD%\dist\BY25Q40AL_PAT_Generator.exe
echo.
exit /b 0

:failed
echo.
echo 打包未完成。
exit /b 1
