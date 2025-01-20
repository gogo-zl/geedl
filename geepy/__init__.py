import importlib
import pkgutil


__version__ = "0.1.1"

__all__ = []  # 汇总所有模块导出的内容

# 遍历当前包下的所有模块
for _, module_name, _ in pkgutil.iter_modules(__path__):
    # 动态导入模块
    module = importlib.import_module(f".{module_name}", package=__name__)
    if hasattr(module, "__all__"):  # 检查模块是否定义了 __all__
        # 将模块中定义的 __all__ 导出的对象添加到当前命名空间
        for attr_name in module.__all__:
            globals()[attr_name] = getattr(module, attr_name)
        __all__.extend(module.__all__)  # 添加到包的 __all__
