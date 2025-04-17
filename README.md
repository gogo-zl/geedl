# GEEdl

**GEEdl** 是一个基于 Google Earth Engine (GEE) 的工具包，目前处于开发阶段。以下是工具包的主要功能规划：

## 功能规划

1. **GEE 基础函数的组合与本地环境的连接**  
   - 封装常用的 GEE 函数，简化遥感数据处理流程。
   - 支持 GEE 与本地环境的数据交互，集成并实现 ArcGIS 中的部分功能。

2. **GEE + PyTorch 深度学习支持**  
   - 集成深度学习功能，如 CNN、DNN 等。

3. **文献代码复现**  
   - 提供部分经典文献的代码复现和示例。

---


## 当前状态

### 开发中：

当前版本已实现以下基础功能：

- 计算任意年份、区域的 Landsat 和 MOD09A1 数据。
- 提供基础的分块函数，如矩形、六边形等。
- 实现其他一些简单的遥感数据处理功能。

高级功能正在持续开发中，包括：

- 高效的大规模数据计算支持。
- 批量处理样本、深度学习相关支持等。

---

## 欢迎贡献

欢迎社区开发者提交建议、功能需求或贡献代码。

---

## 文档

[现有功能文档（zh-CN）](https://gee-py.readthedocs.io/zh_CN/latest/)

---

## 安装方法

使用以下命令从 PyPI 安装 GEEdl：

```bash
pip install geedl
```

或者从 GitHub 安装最新版本：

```bash
pip install git+https://gitclone.com/github.com/gogo-zl/geedl.git
```

[PyPI 上的 GEEdl 项目页面](https://pypi.org/project/geedl/)

---

## 注意

- **版本不一致**：由于 GitHub 和 PyPI 上的版本可能不同步，建议在 GitHub 上获取最新的开发版本。如果你需要稳定版本，请从 PyPI 安装。
- **GitHub 版本**：可以通过 `pip install git+https://github.com/gogo-zl/geedl.git` 获取 GitHub 上的最新代码。

---

## 联系方式

- **作者**：gogo-zl  
- **GitHub 仓库**：[geedl](https://github.com/gogo-zl/geedl.git)

---

> 如有问题或建议，欢迎在 GitHub 仓库提交 Issue 反馈。

