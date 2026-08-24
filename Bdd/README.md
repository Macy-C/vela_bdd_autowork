# Vela BDD 项目

`Bdd/`是基于BDD Autowork构建的Vela自动化宿主。产品应用路径、进程与服务名称、
资源标签、Page Object、locator、data、外部集成和产品测试都属于这里，不应进入
`autowork_core/`或框架文档。

## 环境

在项目根目录安装Python依赖：

```powershell
python -m pip install -r requirements.txt
```

Gantry托管程序集集成所需的`pythonnet`由顶层依赖清单统一安装；供应商DLL及环境要求见
[Gantry集成与排障](integrations/gantry/README.md)。

## 应用生命周期

`Bdd/application.py`是Vela应用和Simulator启停、清理及就绪行为的运行时事实源：

- 当`APP_SETTING.APP_PATH`为`runtime`时，必须提供`start_application()`和
  `stop_application()`。
- `prepare_scenario(context, scenario)`和`cleanup_scenario(context, scenario)`
  负责每个UIScenario前后的项目资源。
- `auto`模式启动Vela托管进程并等待Patient窗口就绪；`attach`模式保留已有应用进程。
- 有效的`@gantry`标签会初始化`SimulatorPage`；被跳过或带`@api`的Scenario不会进入
  项目生命周期。

## 产品知识

iPatient UI Inventory MCP是可选的Vela产品知识候选来源。它可以把业务意图映射到控件、
用途、自动化locator和可行性，但它不是运行时证据：不能证明控件当前存在或唯一，也不能
授权PIC。

正式使用结果时，必须冻结Provider和数据库指纹、query、result ID以及结果hash。该MCP
不可用时Recorder V5仍正常降级运行。外部数据库继续由Provider管理，本仓库只保存有界的
查询provenance。

## 项目文档

- [Gantry集成与排障](integrations/gantry/README.md)
- [历史应用脚本](resources/application/README.md)
- [项目AI资产](ai/README.md)

## 更新框架

从框架仓库拉取目标版本后，完整替换本项目中的框架资产目录和根文件；保留整个`Bdd/`、
`config/`和`artifacts/`。项目开发不直接修改`autowork_core/`、顶层`ai/`、`docs/`、
`.github/`或`resources/`。`framework_validation/`不复制到项目仓库。替换后检查Git diff并
运行轻量验证，再在当前项目仓库提交：

```powershell
python -B -m autowork_core.utils.debug_tools.framework_smoke --project-root .
```

只有项目自己的`Bdd/`或`config/`发生变化时才运行项目测试：

```powershell
python -m unittest discover -s Bdd/tests -p "test_*.py"
```