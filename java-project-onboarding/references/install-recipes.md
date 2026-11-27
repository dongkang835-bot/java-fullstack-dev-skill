# 确认版本后的安装与验证操作页

先跑 `workstation_doctor.py --project <仓库目录>`，读取 CI、README、POM/Gradle 和前端版本文件，写下**项目要求的具体版本、发行版、安装来源和实际缺项**。下面给安装动作与验证方法，不指定“所有新项目通用”的 JDK/Node 版本。公司软件中心或内部镜像优先；未经核实不要改全局镜像、代理和证书设置。

## Git 与仓库访问

1. 公司电脑没有 Git 时，从公司软件中心或 [Git 官方安装入口](https://git-scm.com/downloads)选择与 OS/CPU 对应的安装包。安装后新开终端验证 `git --version`。
2. 公司发放 SSH key、HTTPS 凭据或 SSO 时按其流程接入。先验证项目指定仓库的只读访问，再克隆；认证失败区分“无仓库权限”“VPN/代理不可达”“证书/密钥不匹配”。不要把私钥或带凭据的 URL 记进环境报告。
3. 仓库使用 Git LFS 才安装 LFS，并用 `git lfs version` 与目标文件验证；使用子模块则执行 [首日指南](day-one.md)中的固定提交初始化。

## JDK：macOS

1. 从 CI/POM/团队确认**主版本与发行版**，用公司渠道或发行方对应版本安装包安装；[Dev.java](https://dev.java/learn/getting-started/)和 [Temurin](https://adoptium.net/installation)可用来核对官方安装方式。Intel 与 Apple silicon 选择对应架构。
2. 安装后新开终端：

```sh
/usr/libexec/java_home -V
java -version
javac -version
```

3. 如果有多个 JDK，先用 `/usr/libexec/java_home -V` 确认项目版本真实存在，再为**当前终端**选它。下面的 `17` 仅示范替换位置，实际必须换为项目要求的版本：

```sh
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
"$JAVA_HOME/bin/java" -version
```

4. 在 IDE 设置同一个 Project SDK、Gradle JVM 或 Maven Runner JDK，并运行 `./mvnw -v` 或 `./gradlew --version` 核对构建进程。只有核对成功，才按团队方式将选择写入 shell 配置；不同项目可保留不同版本。

## JDK：Windows

1. 安装与项目版本、架构一致的公司批准 JDK；可用发行方 [Windows 安装说明](https://adoptium.net/installation/windows)核对安装包。
2. 新开 PowerShell，执行 `java -version`、`javac -version`、`where.exe java`。在 IDE 的 Project SDK 与构建器设置中选同一个 JDK。若终端和 IDE 不同，检查 `JAVA_HOME`、Path 顺序与 IDE Run Configuration。
3. 项目有 Maven/Gradle Wrapper 时从仓库根目录运行 `./mvnw.cmd -v` 或 `./gradlew.bat --version`；先确认脚本确实存在。不要仅因系统没有 `mvn`/`gradle` 就重复安装。

## Node 与前端包管理器

1. 先看 `.nvmrc`、`.node-version`、`package.json` 的 `engines`/`packageManager` 和锁文件，再从公司渠道或 [Node 官方下载](https://nodejs.org/en/download/)安装对应版本。多项目需要不同版本时用团队认可的版本管理器，不修改项目锁文件去适配本机。
2. 新开终端验证 `node --version` 与包管理器版本。`package-lock.json`、`pnpm-lock.yaml`、`yarn.lock` 是线索，若多个锁文件并存先看 CI 用哪一个。
3. 在确认私有包仓库/代理来源后，按 CI 的包管理器运行可复现安装命令，例如 `npm ci`、`pnpm install --frozen-lockfile` 或 `yarn install --immutable`；这些是**候选**，具体 flag 与版本以项目为准。遇 401/证书/包不存在先查内部仓库权限与配置，不临时改公共源掩盖问题。

## Maven、Gradle、IDE

- 有 `mvnw` / `gradlew` 时优先用它们；其配置固定构建工具版本，参考 [Maven Wrapper](https://maven.apache.org/tools/wrapper/) 和 [Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html)。缺 Wrapper 才安装团队指定版本的 Maven/Gradle。
- Maven 私服通常通过团队提供的 `settings.xml`、代理或登录流程接入；只记录文件位置与获取方式，不复制凭据。构建报依赖下载失败时先看认证、证书、镜像与 JDK，不盲目删除整个本地缓存。
- Lombok、MapStruct 或其他注解处理器存在时，核对 IDE annotation processing 与命令行构建结果。IDE 红线与命令行构建结果不一致时先比 JDK 和插件配置。

## Docker、数据库与其他中间件

先按[架构盘点](architecture-intake.md)确认服务是否需要本地实例。若公司给共享开发库、托管 Redis/MQ，本地不必另装同类服务；但必须记录环境边界。若使用 `compose.yaml`，先读服务与端口、Volume、初始化脚本和配置来源，确认不会意外连接或清理共享数据，再按团队命令启动。安装 Docker Desktop 参考 [macOS](https://docs.docker.com/desktop/setup/install/mac-install/)或 [Windows](https://docs.docker.com/desktop/setup/install/windows-install/) 官方说明，并确认公司许可与软件分发方式。

数据库安装或连接时分别核对：数据库**产品与方言**、版本、账号权限、Schema/迁移方式、字符集和时区、测试数据来源。启动成功后先做健康检查与只读请求；迁移、初始化数据、启动消费者或定时任务要按当前项目的授权与门禁执行。Redis/MQ/配置中心也先确认是本地、容器还是共享环境，不因为依赖文件出现名字就全装。

## 安装完成的判定

一项工具“装好”至少有：安装来源与版本、终端命令可用、IDE/构建器使用同一版本、目标仓库最小构建或启动成功。整个项目“能开发”还要有：目标服务依赖可达、一个只读 API/页面链路通过、相关测试命令已知、共享环境写入边界明确。把这些证据写进私有项目画像，而不是只保存安装截图。
