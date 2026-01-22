#!/bin/bash
# 後端服務啟動腳本

export PYTHONPATH="/workspace/src:$PYTHONPATH"

cd /workspace

# 安裝缺失的依賴
pip install coze-workload-identity || echo "coze-workload-identity already installed"

# 運行後端服務
python -c "
import sys
import os
sys.path.insert(0, '/workspace/src')

try:
    from src.main import app
    import uvicorn
    print('後端服務啟動中...')
    print('訪問 http://localhost:8000/docs 查看API文檔')
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=False)
except ImportError as e:
    print(f'導入錯誤: {e}')
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'服務啟動錯誤: {e}')
    import traceback
    traceback.print_exc()
"