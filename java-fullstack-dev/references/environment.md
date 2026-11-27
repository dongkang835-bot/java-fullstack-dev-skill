# 环境安装与启动指南

此页是**发现和记录流程**，不是某家公司的固定配置。目标是让另一个开发者按记录复现启动结果，同时避免误连共享环境。

## 1. 先检查仓库

在项目根目录执行只读命令：

```sh
git status --short
find . -maxdepth 2 -name 'pom.xml' -o -name 'build.gradle*' -o -name 'mvnw' -o -name 'gradlew' -o -name 'package.json'
java -version
node --version
```

macOS 可以用 `/usr/libexec/java_home -V` 查看已安装的 JDK。若没有符合要求的版本，先从团队确认发行版、版本和安装渠道，再设置 IDE Project SDK 与终端 `JAVA_HOME`；两处都要核对。不要为了通过编译而随意升级父 POM 或覆盖项目固定版本。

确认当前分支、JDK 目标、Node 版本文件、构建 Wrapper、父子模块、配置中心、容器编排和 CI 命令。仓库有 Wrapper 时优先用 `./mvnw` 或 `./gradlew`，版本仍以项目要求为准。若 `find` 结果很多，按服务目录缩小范围。

在 macOS 上可进一步核对终端、IDE 和构建进程是否真用同一个 JDK：

```sh
/usr/libexec/java_home -V
java -version
./mvnw -v
```

`./mvnw -v` 仅适用于仓库有 Maven Wrapper 的情况；Gradle 用 `./gradlew --version`。查看 `pom.xml` 的 `maven.compiler.release`、`source/target` 或 Gradle Toolchain，再与 IDE Project SDK、Run Configuration 比较。Node 版本检查 `.nvmrc`、`.node-version`、`package.json` 的 `engines` 和锁文件；选仓库使用的包管理器与安装命令。

## 2. 配置来源与安全边界

列出配置来源的**名称和优先级**：本地文件、环境变量、Profile、配置中心、容器或 IDE 启动参数。不要把配置值复制到公开文档或日志。特别核对数据库、Redis、MQ、对象存储和第三方 API 指向本地、开发还是共享环境；“本地进程”不等于“本地数据”。

对每个服务记录：JDK 版本、启动命令、Profile、端口、依赖、健康检查 URL（私有文档中）、是否会注册服务发现、是否会执行定时任务、是否会自动迁移或写共享数据。未知时先停在只读检查。

首次启动按“一个服务一张卡”记录，避免第二天重新猜：

```md
服务/模块：
代码分支与提交：
JDK、构建工具与前端包管理器：
配置来源与 Profile（不记录密钥值）：
依赖服务及环境：
启动命令与端口：
健康检查/只读请求与实际结果：
启动失败时第一条有效错误及解决依据：
记录时间与待确认项：
```

若需要安装工具，先从项目的 CI/README/团队渠道确认版本和下载源；IDE 能运行而终端失败时，重点对比 JDK、环境变量、工作目录和 Profile。不要直接照搬别的项目的 `JAVA_HOME` 或 Maven 私服配置。

## 3. 最小验证

Maven 项目示例（仅在确认该命令适用于项目后运行）：

```sh
./mvnw -v
./mvnw -pl <module> -am test
```

Gradle 项目使用仓库 Wrapper 的相应任务。然后按团队文档启动服务，验证进程、健康检查、一个**只读**接口、前端代理和登录态。记录实际结果及时间。只有 `BUILD SUCCESS` 说明该构建目标成功，不能代替服务启动或业务验证。

## 4. 常见故障定位顺序

| 现象 | 先核对 |
| --- | --- |
| 编译不通过 | JDK 与 `source/target`、父 POM、私有 Maven 仓库、模块选择 |
| 启动找不到配置 | Profile、配置中心访问、环境变量、配置优先级 |
| 端口占用或健康检查失败 | 实际监听端口、启动日志、外部依赖、健康检查路径 |
| 接口 401/403 | 登录态、后端权限、数据权限；前端按钮状态不能证明接口授权 |
| 接口有数据但页面空白 | 响应契约、分页字段、代理地址、浏览器网络请求、时区 |
| 测试偶发失败 | 共享数据、时序、并发、测试隔离、外部依赖 |

修好后更新**目标项目私有**的项目画像，写明证据和日期。不要把公司环境地址写进这个公开 Skill。
