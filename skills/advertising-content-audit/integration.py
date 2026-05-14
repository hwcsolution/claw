#!/usr/bin/env python3
"""
广告内容审核技能集成入口
OpenClaw会自动调用此文件中的handle_message函数
"""

import os
import sys
import re
import tempfile
import base64
from pathlib import Path
from typing import List, Dict, Any

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from advertising_audit import AdvertisingContentAudit
except ImportError:
    print("❌ 无法导入 advertising_audit 模块")
    sys.exit(1)

class OpenClawAdvertisingAudit:
    """OpenClaw广告内容审核集成类"""
    
    def __init__(self):
        """初始化"""
        self.api_key = os.getenv("MAAS_API_KEY")
        if not self.api_key:
            raise ValueError("请设置MAAS_API_KEY环境变量")
        
        self.auditor = AdvertisingContentAudit(self.api_key)
        
        # 触发关键词
        self.trigger_keywords = [
            "广告审核", "合规检查", "违禁词检测", "公关稿审核",
            "海报检查", "广告图合规", "广告法审核", "平台规则审核",
            "广告内容安全", "审核广告", "检查合规", "检测违禁词"
        ]
        
        # 支持的图片格式
        self.supported_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']
        
    def should_trigger(self, message: str, attachments: List[Dict] = None) -> bool:
        """判断是否应该触发技能"""
        # 检查消息是否包含触发关键词
        message_lower = message.lower()
        for keyword in self.trigger_keywords:
            if keyword in message_lower:
                return True
        
        # 检查是否有图片附件
        if attachments:
            for attachment in attachments:
                filename = attachment.get('filename', '').lower()
                if any(filename.endswith(ext) for ext in self.supported_extensions):
                    return True
        
        return False
    
    def extract_images(self, attachments: List[Dict]) -> List[str]:
        """从附件中提取图片路径"""
        image_paths = []
        
        if not attachments:
            return image_paths
        
        for attachment in attachments:
            content = attachment.get('content')
            if not content:
                continue
                
            # 如果是base64编码
            if isinstance(content, str) and content.startswith('data:'):
                try:
                    # 提取base64数据
                    header, data = content.split(',', 1)
                    if 'base64' in header:
                        image_data = base64.b64decode(data)
                        
                        # 确定扩展名
                        ext = '.png'  # 默认
                        if 'png' in header:
                            ext = '.png'
                        elif 'jpeg' in header or 'jpg' in header:
                            ext = '.jpg'
                        elif 'webp' in header:
                            ext = '.webp'
                        elif 'gif' in header:
                            ext = '.gif'
                        
                        # 保存为临时文件
                        temp_file = tempfile.NamedTemporaryFile(
                            suffix=ext, 
                            delete=False,
                            prefix='ad_audit_'
                        )
                        temp_file.write(image_data)
                        temp_file.close()
                        image_paths.append(temp_file.name)
                        
                except Exception as e:
                    print(f"❌ 处理base64图片失败: {e}")
                    
            # 如果是文件路径
            elif isinstance(content, str) and os.path.exists(content):
                image_paths.append(content)
        
        return image_paths
    
    def process(self, message: str, attachments: List[Dict] = None) -> str:
        """处理消息并返回审核结果"""
        print(f"🔍 开始处理广告审核请求")
        
        # 提取图片
        image_paths = self.extract_images(attachments or [])
        
        try:
            # 执行审核
            report = self.auditor.process(message, image_paths)
            
            # 清理临时文件
            for img_path in image_paths:
                if img_path.startswith(tempfile.gettempdir()):
                    try:
                        os.unlink(img_path)
                    except:
                        pass
            
            return report
            
        except Exception as e:
            error_msg = f"❌ 广告审核过程中出现错误: {str(e)}"
            print(error_msg)
            
            # 清理临时文件
            for img_path in image_paths:
                if img_path.startswith(tempfile.gettempdir()):
                    try:
                        os.unlink(img_path)
                    except:
                        pass
            
            return error_msg

def handle_message(message_data: Dict) -> str:
    """
    OpenClaw消息处理入口函数
    """
    # 提取消息内容
    message = message_data.get('text', '').strip()
    attachments = message_data.get('attachments', [])
    
    # 创建审核器实例
    try:
        auditor = OpenClawAdvertisingAudit()
    except ValueError as e:
        return f"❌ 初始化失败: {str(e)}\n请设置MAAS_API_KEY环境变量"
    
    # 检查是否应该触发
    if not auditor.should_trigger(message, attachments):
        return ""  # 空字符串表示不触发
    
    print(f"🎯 触发广告内容审核技能")
    
    # 处理消息
    result = auditor.process(message, attachments)
    
    return result

if __name__ == "__main__":
    # 命令行测试
    if len(sys.argv) > 1:
        message = sys.argv[1]
        attachments = sys.argv[2:] if len(sys.argv) > 2 else []
        
        attachment_dicts = []
        for att_path in attachments:
            if os.path.exists(att_path):
                attachment_dicts.append({
                    'filename': os.path.basename(att_path),
                    'content': att_path
                })
        
        result = handle_message({
            'text': message,
            'attachments': attachment_dicts
        })
        
        if result:
            print(result)
        else:
            print("未触发广告审核技能")
    else:
        print("用法: python integration.py '广告文案' [图片路径...]")