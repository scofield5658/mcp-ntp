# MCP-NTP 时间服务

这是一个基于MCP（Model Context Protocol）的NTP时间服务，为大模型提供准确的网络时间获取功能。

## 功能特性

- 从NTP服务器获取准确的网络时间
- 支持stdio和sse两种传输模式
- 提供`get_current_time`工具，方便大模型获取当前时间
- 支持环境变量和请求头两种配置NTP服务器的方式
- 返回详细的时间信息和NTP协议数据

## 安装

```bash
# 使用 uv 安装依赖
uv sync
```

## 配置

### 环境变量配置（stdio模式）

设置`NTP_DOMAIN_URL`环境变量：

```bash
export NTP_DOMAIN_URL="ntp.aliyun.com"
```

### 请求头配置（sse模式）

在请求头中包含`ntp_url`字段：

```
ntp_url: ntp.aliyun.com
```

## 使用方法

### stdio模式

```bash
# 设置环境变量
export NTP_DOMAIN_URL="ntp.aliyun.com"

# 启动服务
python -m app
```

### sse模式

```bash
# 启动服务
python -m app --transport sse --port 8080

# 使用curl测试
curl -H "ntp_url: ntp.aliyun.com" http://localhost:8080/sse
```

## 工具说明

### get_current_time

获取当前NTP服务器时间。

**参数：**
- `ntp_server` (可选): NTP服务器地址，如果不提供则使用环境变量或请求头中的配置

**返回数据：**
```json
{
  "ntp_server": "ntp.aliyun.com",
  "ntp_timestamp": 1703123456.789,
  "ntp_time": "2023-12-21T10:30:56.789",
  "local_system_time": "2023-12-21T10:30:56.789",
  "time_offset": 0.123,
  "response_delay": 0.045
}
```

## 调试

可以使用提供的测试NTP服务器进行调试：

```bash
export NTP_DOMAIN_URL="ntp.aliyun.com"
python -m app -v
```

## 开发

### 项目结构

```
mcp-ntp/
├── app/
│   ├── __init__.py      # 主入口
│   ├── server.py        # MCP服务器实现
│   ├── client.py        # NTP客户端
│   └── config.py        # 配置管理
├── pyproject.toml       # 项目配置
└── README.md           # 说明文档
```

### 添加新的NTP服务器

在`client.py`中的`get_current_time`函数可以轻松扩展支持更多NTP服务器配置。

## 许可证

MIT License
