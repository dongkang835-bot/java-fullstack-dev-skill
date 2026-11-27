# 公开资料索引与来源说明

核对日期：2026-11-27。下面链接指向原始维护方；使用时选择与目标项目版本相符的文档。此仓库只归纳工作方法，不转载原文或 PDF。

## Java 与编码规范

- [Dev.java 官方学习入口](https://dev.java/learn/)：Java 语法、API、工具和现代特性。先按项目 JDK 版本选内容。
- [阿里巴巴 p3c 官方仓库](https://github.com/alibaba/p3c)：《Java 开发手册》及静态检查工具入口。适合核对常见编码风险；不是新公司的强制标准。
- [阿里巴巴 Java Coding Guidelines 官方 GitBook 仓库](https://github.com/alibaba/Alibaba-Java-Coding-Guidelines)：可在线查阅规则与说明。不要把整本手册复制进本仓库。

## 构建、Spring 和持久化

- [Apache Maven 入门](https://maven.apache.org/guides/getting-started/) 与 [Maven Wrapper](https://maven.apache.org/tools/wrapper/)：理解构建生命周期并优先使用项目 Wrapper。
- [Spring Boot 官方文档](https://docs.spring.io/spring-boot/reference/)：按实际 Spring Boot 版本切换文档。
- [Spring Framework 事务回滚规则](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html)：理解默认规则与 `rollbackFor` 等配置。
- [Spring Boot 测试](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)：根据测试范围选择上下文测试方式。
- [MyBatis-Plus 逻辑删除](https://baomidou.com/en/guides/logic-delete/)：仅在项目实际使用该框架时参考；自定义 SQL 行为需在项目中验证。
- [OWASP API Security Top 10](https://api-security.owasp.org/editions/2023/en/0x00-header/)：特别关注对象级与功能级授权。

## 本机资料的借鉴范围

制作时定向阅读了本机多个项目的入口约束、知识索引、工程规范与任务工作流，也对相关源码做了文件与注解标记扫描、追查代表性前后端调用链。扫描不等于逐文件理解业务实现，也未运行系统验证。这里只提炼通用方法；原项目的名称、类名、代码、环境地址、权限码、业务规则和原文均未纳入公开成品。

若以后要加新公司的具体规范，请保存在该公司的私有仓库或文档中，并把其优先级写清楚。公开仓库只保留可以跨项目复用的做法。
