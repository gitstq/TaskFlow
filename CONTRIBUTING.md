# Contributing to TaskFlow

首先，感谢您考虑为 TaskFlow 做出贡献！🎉

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 GitHub Issues 提交：

1. 检查是否已有类似的问题
2. 创建新 issue，详细描述：
   - 问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（操作系统、Python版本等）

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/gitstq/TaskFlow.git
   cd TaskFlow
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

4. **推送到 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**

### 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 最大行长度 100 字符
- 添加适当的注释和文档字符串

## 开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e .

# 运行测试
python -m pytest
```

## 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 关注对社区最有利的事情

再次感谢您的贡献！
