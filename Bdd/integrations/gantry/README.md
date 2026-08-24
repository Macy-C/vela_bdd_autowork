# Vela Gantry 集成

`easy_control.py`是Vela拥有的Gantry托管API Python门面。默认程序集目录是相邻的`bin/`
目录。DLL必须成组保存在该目录中，因为`GantryEasyControl.dll`运行时会从这里解析其托管
依赖。

该集成只在`@gantry` Scenario中延迟导入。Python桥接依赖`pythonnet`由顶层
`requirements.txt`统一声明；不使用该集成的项目不需要这些二进制文件。

## COM 注册

`REGDB_E_CLASSNOTREG (0x80040154)`表示托管程序集已经加载，但依赖的COM Server没有
注册到当前Python进程使用的注册表视图。请确认Vela设备或Simulator安装完整，并确认
Python与COM Server位数兼容。应使用供应商提供的安装或注册流程；不要对用途不明确的
DLL直接执行`regsvr32`。

```powershell
Test-Path 'Registry::HKEY_CLASSES_ROOT\CLSID\{报错中的 CLSID}'
Test-Path 'Registry::HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{报错中的 CLSID}'
```