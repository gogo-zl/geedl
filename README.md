# GEEpy

**GEEpy** 是一个基于 Google Earth Engine (GEE) 的工具包，目前处于开发阶段。以下是工具包的主要功能规划：

## 功能规划

1. **GEE 基础函数的组合与本地环境的连接**  
   - 封装常用的 GEE 函数，简化遥感数据处理流程。
   - 支持 GEE 与本地环境的数据交互，集成并实现 ArcGIS 中的部分功能。

2. **GEE + PyTorch 深度学习支持**  
   - 集成深度学习功能，如CNN、DNN等。

3. **文献代码复现**  
   - 提供部分经典文献的代码复现和示例。

---

## 安装方法

使用以下命令从 GitHub 镜像安装：

```bash
pip install git+https://gitclone.com/github.com/gogo-zl/GEE_py.git
OR
pip install git+https://gitee.com/gogo-zl/gee_py.git@v0.1.2
```

---

## 更新方法

使用以下命令更新至最新版本：

```bash
pip install --upgrade git+https://gitclone.com/github.com/gogo-zl/GEE_py.git
OR
pip install --upgrade git+https://gitee.com/gogo-zl/gee_py.git@v0.1.2
```

---

## 当前状态

- **开发中**：
  - 当前版本仅实现部分基础功能，包括：
    - 计算任意年份、区域的Landsat和MOD09A1
    - 基础分块函数，如矩形、六边形
    - 其他简单有趣的小功能.
  - 更多高级功能（批量处理样本、高效大规模计算支持）将持续更新。
  
- **欢迎贡献**：
  - 欢迎社区开发者提交建议、功能需求或贡献代码。

**文档**：
  - [现有功能文档（zh-CN）](https://gee-py.readthedocs.io/zh_CN/latest/)。
---

## 联系方式

- **作者**：gogo-zl  
- **GitHub 仓库**：[GEE_py](https://github.com/gogo-zl/GEE_py.git)

---

> 如有问题或建议，欢迎在 GitHub 仓库提交 Issue 反馈。