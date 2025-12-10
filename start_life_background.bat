@echo off
:: 隐藏窗口运行后台服务
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin

:: 切换到项目目录
cd /d "D:\10_DOING\LifeOS"

:: 激活环境并运行服务
call python main.py serve

