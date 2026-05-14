#!/usr/bin/env python3
"""
华为云MaaS文生图脚本
使用Qwen-image模型生成图片
"""

import requests
import json
import base64
import os
import sys
from datetime import datetime
from pathlib import Path

# API配置
API_URL = "https://api.modelarts-maas.com/v1/images/generations"
MODEL_NAME = "qwen-image"

def get_api_key():
    """获取API Key，优先从环境变量，其次从配置文件"""
    # 尝试环境变量
    api_key = os.environ.get("MAAS_API_KEY")
    if api_key:
        return api_key
    
    # 尝试配置文件 config/config.json
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            maas_config = config.get("maas", {})
            api_key = maas_config.get("api_key")
            if api_key:
                return api_key
    
    raise ValueError("未找到API Key，请设置环境变量MAAS_API_KEY或配置config/config.json")

def generate_image(prompt, size="1024x1024", seed=1, output_dir=None, filename=None):
    """
    生成图片
    
    Args:
        prompt: 图片描述（中英文均可）
        size: 图片尺寸，如 "1024x1024", "768x1024"
        seed: 随机种子，范围[0, 2147483648]
        output_dir: 输出目录，默认为当前目录
        filename: 输出文件名，默认自动生成
    
    Returns:
        保存的图片路径
    """
    # 获取API Key
    api_key = get_api_key()
    
    # 构建请求
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "size": size,
        "response_format": "b64_json",
        "seed": seed
    }
    
    print(f"正在生成图片...")
    print(f"  Prompt: {prompt}")
    print(f"  尺寸: {size}")
    
    # 发送请求
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data), verify=False)
    except Exception as e:
        raise RuntimeError(f"请求失败: {e}")
    
    # 检查响应
    if response.status_code != 200:
        raise RuntimeError(f"API返回错误: {response.status_code} - {response.text}")
    
    # 解析响应
    result = response.json()
    
    # 获取base64图片数据
    if "data" not in result or len(result["data"]) == 0:
        raise RuntimeError(f"响应格式错误: {result}")
    
    b64_data = result["data"][0].get("b64_json")
    if not b64_data:
        raise RuntimeError(f"未找到图片数据: {result}")
    
    # 处理data URL前缀（如果有）
    if b64_data.startswith("data:"):
        # 格式: data:image/png;base64,xxxxx
        b64_data = b64_data.split(",", 1)[1]
    
    # 解码并保存
    image_data = base64.b64decode(b64_data)
    
    # 确定输出路径
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"maas_image_{timestamp}.png"
    
    output_path = output_dir / filename
    
    with open(output_path, 'wb') as f:
        f.write(image_data)
    
    print(f"图片已保存: {output_path}")
    
    return str(output_path)

def size_for_ratio(ratio):
    """
    根据比例返回合适的尺寸
    
    Args:
        ratio: 比例字符串，如 "3:4", "1:1", "4:3"
    
    Returns:
        尺寸字符串，如 "768x1024"
    """
    ratio_map = {
        "3:4": "768x1024",   # 小红书竖图
        "4:3": "1024x768",   # 横图
        "1:1": "1024x1024",  # 方图
        "16:9": "1024x576",  # 宽屏
        "9:16": "576x1024",  # 手机竖屏
    }
    return ratio_map.get(ratio, "1024x1024")

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="华为云MaaS文生图")
    parser.add_argument("prompt", help="图片描述")
    parser.add_argument("--size", default="1024x1024", help="图片尺寸")
    parser.add_argument("--ratio", help="图片比例(3:4, 1:1, 4:3等)，与size二选一")
    parser.add_argument("--seed", type=int, default=1, help="随机种子")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--filename", "-f", help="输出文件名")
    
    args = parser.parse_args()
    
    # 处理尺寸
    size = size_for_ratio(args.ratio) if args.ratio else args.size
    
    # 生成图片
    try:
        path = generate_image(
            prompt=args.prompt,
            size=size,
            seed=args.seed,
            output_dir=args.output,
            filename=args.filename
        )
        print(f"\n✅ 生成成功: {path}")
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
