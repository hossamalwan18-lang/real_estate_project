@echo off
chcp 65001 >nul
echo ========================================================
echo        تشغيل موقع عقارات مصر - Egypt Real Estate
echo ========================================================
echo.
echo جاري بدء خادم الويب...
echo.
start http://127.0.0.1:5000
python app.py
pause
