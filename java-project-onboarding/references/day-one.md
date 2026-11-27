# 第一天：新电脑到第一个可运行服务

这是操作顺序，不是预装所有工具的清单。电脑由公司管理时，先看其软件中心、VPN、证书和仓库接入文档；安装权限与内部镜像由团队提供。**版本以目标项目与 CI 为准**，不要用“最新版”替代项目要求。

## A. 拉仓之前确认

| 要拿到的信息 | 为什么需要 | 验证结果 |
| --- | --- | --- |
| 操作系统与 CPU 架构 | 选择 JDK/Node/容器安装包 | `uname -m`（macOS/Linux）或系统信息 |
| Git 主机、账号权限、VPN/代理、证书 | 区分认证失败与网络失败 | 能访问仓库网页和项目指定的 Git 协议 |
| 仓库列表、主仓库、目标分支 | 防止拉错旧仓或只拉前端 | 与团队给出的仓库清单核对 |
| Git LFS/子模块要求 | 防止代码齐了但资源或服务缺失 | `.gitattributes`、`.gitmodules`、README |
| IDE 与插件约定 | 确认项目 SDK、注解处理、格式化 | 与仓库/团队约定一致 |

只读检查（macOS/Linux；Windows 可用 PowerShell 的 `git --version`、`java -version` 等同名命令）：

```sh
uname -s
uname -m
git --version
java -version
node --version
docker --version
```

命令不存在就记“未安装”，不需要因此立即装 Docker 或本地数据库。`workstation_doctor.py` 会批量给出这类结果，且不会检查网络连通性或凭据值。

## B. 拉取并固定代码基线

```sh
git clone <团队提供的仓库地址> <目标目录>
cd <目标目录>
git status --short --branch
git rev-parse HEAD
git submodule status --recursive
```

如果项目明确使用子模块，可在克隆时用 `git clone --recurse-submodules`，或在已克隆目录执行 `git submodule update --init --recursive`。这会检出主仓库固定的子模块提交；`git submodule update --remote` 会按远端分支更新，入职盘点时不要当成等价命令。Git LFS 仅在仓库使用时再按团队方式配置并核对目标文件。多仓库项目分别记录每个仓库的分支、提交与未提交改动。参考 [Git 子模块官方文档](https://git-scm.com/docs/gitsubmodules)。

认证失败先区分：仓库权限、VPN/代理、SSH key/HTTPS 凭据、主机证书。不要把私钥、Token 或带凭据的 URL 粘到聊天、日志或公开 Skill。不要自动修改全局 Git 认证配置。

## C. 从仓库确定版本，再安装

| 组件 | 去哪里看要求 | 安装与验证 |
| --- | --- | --- |
| JDK | CI、`pom.xml` 的 `maven.compiler.release`/`source`、Gradle Toolchain、`.java-version`、团队文档 | 按版本与发行版安装；`java -version`、`./mvnw -v`/`./gradlew --version`、IDE SDK 三处核对 |
| Maven/Gradle | `mvnw`/`gradlew` 与 wrapper 配置 | 有 Wrapper 用项目脚本；没有才核对团队要求的系统版本，参考 [Maven Wrapper](https://maven.apache.org/tools/wrapper/) 或 [Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html) |
| Node 与包管理器 | `.nvmrc`、`.node-version`、`package.json` engines、`packageManager`、锁文件 | 安装指定 Node；按 `package-lock.json`/`pnpm-lock.yaml`/`yarn.lock` 选团队命令，参考 [Node 官方下载](https://nodejs.org/en/download/) |
| 容器工具 | `compose.yaml`、Dockerfile、开发文档 | 仅本地运行确需容器时安装并验证 daemon；参考 [Docker macOS](https://docs.docker.com/desktop/setup/install/mac-install/) 或 [Windows](https://docs.docker.com/desktop/setup/install/windows-install/) 指南，并遵循公司软件许可 |
| 数据库/Redis/MQ | README、容器编排、配置模板、服务依赖 | 先确认使用本地实例、远端开发实例还是 Mock；不要根据依赖名就安装或启动写数据的服务 |

JDK 下载渠道由团队决定，可用 [Dev.java 入门](https://dev.java/learn/getting-started/) 与 [Eclipse Temurin 安装页](https://adoptium.net/installation)核对安装方式。不要把本机同时存在多个 JDK 当作失败；关键是终端、构建器和 IDE 对当前项目使用同一目标版本。

## D. 配置、构建、运行

1. 查配置来源及覆盖顺序：环境变量、`application-*.yml`、配置中心、IDE Run Configuration、容器参数。只记录**键名和来源**，不复制值。确认启动时连接的是本地、开发还是共享数据库/MQ，并查是否会自动迁移、跑定时任务或消费消息。
2. 按仓库提供的命令安装依赖。Maven/Gradle 先用 Wrapper 的版本命令，前端按锁文件与团队约定使用对应安装命令；私有仓库失败时先看 VPN/证书/镜像配置，而不是随意换公共源。
3. 执行目标模块最小构建或相关测试。多模块项目按仓库说明选 `-pl` 或 Gradle 任务；不要在陌生仓库直接跑全量集成测试。
4. 启动后核对进程监听、健康检查、一次只读 API、浏览器网络请求与日志请求 ID。缺前端或下游时分开记录“后端可启动”与“全链路未验证”。

## E. 交付给自己的环境记录

```md
电脑：OS/CPU 架构；工具与版本；安装来源
仓库：主仓及子仓的分支/提交；是否有本地改动
配置：获取渠道、Profile、依赖所处环境（不写密钥/连接串）
命令：依赖安装、最小构建、启动、健康检查、停止
结果：每个命令实际结果与时间；第一个页面/API 证据
阻塞：缺少的权限、版本、配置或服务；负责人/文档入口
```
