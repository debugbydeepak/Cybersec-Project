@echo off
cd "c:\Users\nandk\Desktop\Project\hackathon winning idea"
xcopy secureway\accounts\* accounts\ /Y /E
xcopy secureway\assets\* assets\ /Y /E
xcopy secureway\core\* core\ /Y /E
xcopy secureway\dashboard\* dashboard\ /Y /E
xcopy secureway\reports\* reports\ /Y /E
xcopy secureway\scanner\* scanner\ /Y /E
xcopy secureway\templates templates\ /Y /E /I
xcopy secureway\static static\ /Y /E /I
rmdir /s /q secureway\accounts
rmdir /s /q secureway\assets
rmdir /s /q secureway\core
rmdir /s /q secureway\dashboard
rmdir /s /q secureway\reports
rmdir /s /q secureway\scanner
rmdir /s /q secureway\templates
rmdir /s /q secureway\static
