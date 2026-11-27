# 从前端到 Java / Spring：最小知识地图

先确认目标项目版本。Java 8 + Spring Boot 2 项目可能使用 `javax.*`；Spring Boot 3+ / Spring Framework 6+ 常见 `jakarta.*`。写代码时跟随仓库实际依赖和风格，不把新教程的语法直接塞进老项目。

| 熟悉的前端概念 | Java 后端对应点 | 容易踩的差异 |
| --- | --- | --- |
| TypeScript 类型 | Java 类、接口、泛型 | 泛型有类型擦除；`null` 仍需显式处理 |
| `package.json` / lockfile | `pom.xml` / `build.gradle`、Wrapper | 编译、测试和打包是不同生命周期/任务 |
| 路由处理函数 | Spring `@RestController` | DTO 校验、认证授权、响应契约需要后端承担 |
| API service / store action | Service / 业务服务 | 事务通常放在业务边界，调用可能涉及 DB、缓存和 MQ |
| fetch 拦截器 | Servlet Filter / Spring Interceptor / Security Filter Chain | 先核实真实执行顺序和例外配置 |
| ORM client / SQL | JPA / MyBatis / MyBatis-Plus | 自定义 SQL 是否自动应用软删除、租户条件，必须看实际 SQL |
| Promise 异步任务 | Executor / `@Async` / 消息消费 | 线程上下文、事务和异常处理不会自动按预期传播 |

## 看到这些注解时，下一步查什么

| 代码线索 | 先确认 | 容易误判的地方 |
| --- | --- | --- |
| `@RequestMapping` / `@PostMapping` | 类级与方法级路径、HTTP 方法、网关前缀 | 搜到方法路径不代表浏览器的完整 URL |
| `@RequestBody` / `@Valid` | DTO 字段、校验注解、全局异常映射 | Java 类型非空不等于运行时参数必填 |
| `@Secured` / `@PreAuthorize` | 表达式/权限码、对象或租户范围、例外路径 | 有功能权限不等于能操作任意 ID |
| `@Service` / `@Component` | 接口实现、Bean 条件、调用方 | 同名实现可能由 Profile 或配置选择 |
| `@Transactional` | 事务管理器、代理调用、回滚规则、外部副作用 | 同类自调用、异步和远程服务可能不在该事务里 |
| `@FeignClient` / HTTP 客户端 | 服务名、请求契约、超时/重试/降级 | 客户端接口不是提供方实现 |
| `@Mapper` / `Repository` | 最终 SQL、索引、软删除和数据范围 | 自定义 SQL 未必继承框架默认过滤 |
| `@Async` / MQ 监听器 | 线程池、消息确认、重试、幂等 | 原请求返回成功不等于后台任务成功 |

## 改 Java 代码时的几个细节

- `BigDecimal` 的值比较通常看 `compareTo`，`equals` 还比较 scale；金额/数量的精度与舍入规则要跟业务和数据库字段核对。
- `Integer`、`Long` 等包装类型可能为 `null`；用 `==` 比较对象可能只是在比引用。状态和 ID 的比较要看项目类型与空值约定。
- `Stream` 适合清晰的转换，不要把数据库调用藏在 `map` 中造成 N+1，也不要在 `parallelStream` 里依赖请求上下文或事务。
- DTO、Entity、VO、Feign 对象常有转换层。新增字段时逐层检查转换器和序列化命名，避免后端字段存在而接口丢失。
- `LocalDateTime` 没有时区信息；时间在浏览器、服务和数据库之间传递时，核对项目的时区、序列化格式与存储约定。
- 捕获异常后返回成功对象或吞掉异常，可能阻止事务按预期回滚；先看项目的异常处理链和业务错误码。

这些是定位线索，不是要求所有项目采用相同注解或写法。拿到具体类时，请 AI 解释“这个方法谁调用、参数从哪里来、修改了什么、异常后会留下什么”，比背注解列表更有用。

## 读懂一个 Java 服务的顺序

1. `pom.xml` 或 Gradle 文件：JDK 目标、Spring 版本、依赖、模块与插件。
2. 启动类和 `application*.yml`：配置来源、Profile、端口和外部依赖。
3. 一个已有功能：Controller → 请求/响应 DTO → Service → Mapper/Repository → 表、外部服务。
4. 对应测试：看项目如何构造依赖、断言错误、启动上下文。

## 优先掌握的 Java 知识

- **值与对象**：基本类型和包装类型、`String` 不可变、`equals` 与 `==`、`BigDecimal` 金额/数量、日期时间与时区。
- **集合与泛型**：`List`、`Map`、`Set`、空集合与 `null`、`Stream` 的适用边界。
- **异常**：checked/unchecked；在哪里转换成 API 错误；不吞异常、不泄露敏感信息。
- **并发与副作用**：请求会并发执行；“先查再写”不天然安全；关注唯一约束、乐观锁、幂等键和重复消息。
- **Spring**：依赖注入、Bean 生命周期、配置绑定、MVC 校验、事务代理。`@Transactional` 的回滚规则和同类方法自调用行为应按项目 Spring 版本核对。
- **SQL**：索引、事务隔离、分页、批量操作、执行计划。数据库正确性不能只靠前端限制。

## 阿里巴巴《Java 开发手册》怎么用

把它当作**候选检查清单**：命名、集合、异常、并发、日志、数据库与工程结构。每遇到一条规则，先问：项目是否使用同一 Java/框架版本？团队是否已有相反约定？这条规则解决什么真实风险？项目的 linter/静态检查是否已经覆盖？只采用适用于当前代码库的结论。原手册与 p3c 工具见[资料索引](sources.md)，不要将 PDF 直接复制进公开仓库。
