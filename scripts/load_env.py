#!/usr/bin/env python3
"""
加载 .env 文件中的环境变量
支持从多个位置查找 .env 文件
"""
import os
from pathlib import Path


def load_env_file(env_path=None):
    """
    加载 .env 文件到环境变量
    
    参数:
        env_path: .env 文件路径（可选）
    """
    if env_path and Path(env_path).exists():
        env_file = Path(env_path)
    else:
        # 多个候选位置
        candidates = [
            # 1. 当前工作目录
            Path.cwd() / '.env',
            # 2. 用户主目录下的 vault 根目录（常见位置）
            Path.home() / '乔木新知识库' / '.env',
            # 3. 从当前脚本向上查找
            Path(__file__).resolve().parent / '.env',
        ]
        
        # 向上查找（最多10层）
        current = Path(__file__).resolve().parent
        for _ in range(10):
            candidates.append(current / '.env')
            current = current.parent
        
        # 找到第一个存在的 .env 文件
        env_file = None
        for candidate in candidates:
            if candidate.exists():
                env_file = candidate
                break
        
        if env_file is None:
            return False
    
    # 读取并加载环境变量
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 解析 KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # 设置环境变量（如果还未设置）
                if key and not os.environ.get(key):
                    os.environ[key] = value
    
    return True


# 自动加载
load_env_file()
