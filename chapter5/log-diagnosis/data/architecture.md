# 订单退款 Agent 系统架构

本系统是一个电商客服场景下的多模块 Agent，负责处理用户的订单查询与退款请求。

## 模块划分

- **intent_parser（意图识别）**：解析用户自然语言，判断意图（`refund` / `order_status` / `chitchat`），抽取订单号等实体。
- **order_service（订单服务）**：负责订单相关的读写。
  - 工具 `query_order(order_id)`：查询订单状态与金额。
  - 工具 `verify_refund_eligibility(order_id)`：校验订单是否满足退款条件（是否已支付、是否在退款时限内、是否已退过款）。**退款流程中此步骤为强制前置校验。**
- **payment_service（支付服务）**：对接第三方支付网关。
  - 工具 `process_refund(order_id, amount)`：发起退款。第三方网关偶发不稳定，要求实现**重试 + 退避**并在最终失败时上报，不得静默丢弃。
- **inventory_service（库存服务）**：查询与回补库存。
  - 工具 `check_stock(sku)`：查询库存。**要求单次调用延迟不超过 5000ms**，超时应走降级路径而非阻塞主流程。
- **notification_service（通知服务）**：向用户发送结果通知。

## 关键调用链（退款）

```
user -> intent_parser -> order_service.query_order
      -> order_service.verify_refund_eligibility   # 强制前置校验
      -> payment_service.process_refund            # 需重试+退避
      -> notification_service.notify_user
```

## 可观测性

系统为每次任务落一条 trajectory（轨迹）日志，记录每一交互轮次（turn）的模块、工具、输入输出、状态与延迟（latency_ms）。轨迹用于线上问题诊断与回归测试重放。
