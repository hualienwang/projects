#!/usr/bin/env python
"""
後端服務啟動腳本
"""

import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn
import logging

def run_server():
    # 設置日誌級別
    logging.basicConfig(level=logging.INFO)
    
    # 延遲導入以避免初始化問題
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), "src", "main.py"))
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    app = main_module.app
    
    # 啟動 uvicorn 服務器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )

if __name__ == "__main__":
    run_server()