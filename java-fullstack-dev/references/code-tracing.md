# 从页面操作追到 Java 写入：实操路线

收到需求时，先固定一个可观察的入口，例如“点击取消订单后，页面应显示已取消”。不要一开始搜索整个业务名词并阅读所有命中；从页面、请求路径或日志中的一个稳定线索追一条链。下面命令是候选写法，先在目标仓库根目录确认工具与目录。

## 1. 从前端确定真实请求

浏览器 DevTools 的 Network 记录方法、URL、请求体、响应、状态码和请求 ID；若页面还未能启动，就在源码找文案、按钮事件和 API 函数：

```sh
rg -n '取消订单|cancelOrder|order/cancel' . -g '*.{vue,js,ts,tsx}'
rg -n 'request\(|axios\.|fetch\(' . -g '*.{js,ts}'
```

大型仓库先用 `rg --files | rg 'src/(api|views|pages)/'` 定位目录，再缩小搜索范围。记录页面条件、参数怎么组装、前端是否只隐藏按钮、是否有重复点击保护。然后核对网关前缀、Vite 代理或 BFF：浏览器看到的 URL 未必等于服务上的 `@RequestMapping`。

## 2. 在 Java 中找到入口与下一跳

先搜路径末段、HTTP 注解和实现类，不要假定类名与 URL 相同：

```sh
rg -n 'order/cancel|@(?:Post|Put|Delete|Request)Mapping|@RestController' --glob '*.java'
rg -n 'interface .*Client|@FeignClient|@Service|implements .*Service' --glob '*.java'
```

读类级与方法级映射的组合、请求 DTO、`@Validated`/`@Valid`、默认值、返回包装和异常处理。若当前 Controller 只转发给 Feign/BFF，继续跟到提供方；若经过消息队列，找生产者、消费者和重试/去重逻辑。接口声明不等于实际实现，必要时按具体类型查 `implements` 与 Spring Bean 条件。

## 3. 核对业务修改落在哪里

沿方法调用读 Service、领域服务、Mapper/Repository 与 SQL。常用检索：

```sh
rg -n 'cancelOrder|updateStatus|@Transactional|@Async|@Scheduled' --glob '*.java'
rg -n 'UPDATE |INSERT |DELETE |<update|<insert|<delete' --glob '*.xml' --glob '*.java'
rg -n 'CREATE TABLE|ALTER TABLE|liquibase|flyway' --glob '*.{sql,xml,yml,yaml}'
```

把状态流转条件、对象归属或租户过滤、唯一约束、乐观锁、软删除、缓存更新、消息发送列出来。对自定义 SQL，读真实条件和参数绑定，不能假设 ORM 插件会自动加权限或逻辑删除。对跨仓调用，分别记录消费方和提供方的分支/提交。

## 4. 回头核对测试和反向影响

找目标方法的直接测试，再找其他调用方：

```sh
rg -n 'cancelOrder|order/cancel' --glob '*Test.java' --glob '*Tests.java' --glob '*.{vue,js,ts,tsx}'
rg -n 'cancelOrder\(' --glob '*.java'
```

至少看正常输入、无权限、对象不属于当前用户、已取消再取消、下游失败时结果如何。若是新增字段，还要搜序列化、映射、导出、导入、批任务和旧客户端消费位置。测试名称和注解只能提示位置，是否断言到真实行为要看断言内容。

## 交给开发者的一页链路图

| 环节 | 证据文件/行号 | 输入与输出 | 关键规则或副作用 | 状态 |
| --- | --- | --- | --- | --- |
| 页面/客户端 | 待填 | 待填 | 按钮条件、错误展示 | 已验证/推断 |
| API/BFF | 待填 | 待填 | 鉴权、校验、转换 | 已验证/推断 |
| 业务服务 | 待填 | 待填 | 状态、事务、幂等 | 已验证/推断 |
| DB/外部系统 | 待填 | 待填 | SQL、消息、缓存 | 已验证/推断 |
| 测试/运行证据 | 待填 | 待填 | 已覆盖与缺口 | 已验证/待确认 |

只填写当前任务相关的环节。对没有运行过的链路标“源码推断”，不要写成联调通过。发现知识库路径失效时搜索源码，并在报告中记录文档版本差异。
