#!/usr/bin/env python3
"""
错误签名提取器
从错误日志中提取唯一的错误签名，用于知识库匹配
"""

import re
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class ErrorSignature:
    """错误签名数据类"""
    original_error: str  # 原始错误信息
    signature: str       # 错误签名（用于匹配）
    error_type: str      # 错误类型
    error_code: str      # 错误代码
    error_message: str   # 错误消息
    stack_trace: str     # 堆栈跟踪（如果有）
    context: Dict[str, Any]  # 上下文信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class ErrorSignatureExtractor:
    """错误签名提取器"""
    
    # 常见错误模式正则表达式
    ERROR_PATTERNS = {
        # Java异常
        'java_exception': re.compile(r'([A-Za-z0-9_\.]+Exception):\s*(.*)'),
        'java_error': re.compile(r'([A-Za-z0-9_\.]+Error):\s*(.*)'),
        
        # Python异常
        'python_exception': re.compile(r'([A-Za-z0-9_\.]+Error):\s*(.*)'),
        'python_traceback': re.compile(r'Traceback \(most recent call last\):'),
        
        # 系统错误
        'system_error': re.compile(r'error:\s*(.*)', re.IGNORECASE),
        'system_failed': re.compile(r'failed:\s*(.*)', re.IGNORECASE),
        'system_crash': re.compile(r'crash(?:ed)?:\s*(.*)', re.IGNORECASE),
        
        # 网络错误
        'connection_error': re.compile(r'connection (?:refused|failed|timeout|reset)', re.IGNORECASE),
        'timeout_error': re.compile(r'timeout', re.IGNORECASE),
        
        # 数据库错误
        'sql_error': re.compile(r'SQL(?:STATE)?.*?error', re.IGNORECASE),
        'database_error': re.compile(r'database.*?error', re.IGNORECASE),
        
        # 服务错误
        'service_error': re.compile(r'service.*?(?:unavailable|failed|error)', re.IGNORECASE),
        'http_error': re.compile(r'HTTP/\d\.\d\s+(\d{3})\s+(.*)'),
        
        # 资源错误
        'memory_error': re.compile(r'out of memory|OOM|memory limit', re.IGNORECASE),
        'disk_error': re.compile(r'disk.*?(?:full|space|quota)', re.IGNORECASE),
        'cpu_error': re.compile(r'cpu.*?(?:limit|throttling)', re.IGNORECASE),
        
        # 权限错误
        'permission_error': re.compile(r'permission denied|access denied|forbidden', re.IGNORECASE),
        'authentication_error': re.compile(r'authentication failed|unauthorized', re.IGNORECASE),
        
        # 配置错误
        'config_error': re.compile(r'configuration.*?error|config.*?invalid', re.IGNORECASE),
        'syntax_error': re.compile(r'syntax error', re.IGNORECASE),
    }
    
    # 错误代码提取模式
    ERROR_CODE_PATTERNS = [
        re.compile(r'error\s+code\s*[:=]\s*(\S+)', re.IGNORECASE),
        re.compile(r'code\s*[:=]\s*(\d+)', re.IGNORECASE),
        re.compile(r'errno\s*[:=]\s*(\d+)', re.IGNORECASE),
        re.compile(r'status\s*[:=]\s*(\d+)', re.IGNORECASE),
        re.compile(r'HTTP\s+(\d{3})', re.IGNORECASE),
    ]
    
    def __init__(self):
        """初始化提取器"""
        pass
    
    def extract_signature(self, error_text: str, context: Dict[str, Any] = None) -> ErrorSignature:
        """
        从错误文本中提取签名
        
        Args:
            error_text: 错误文本
            context: 上下文信息（可选）
            
        Returns:
            ErrorSignature对象
        """
        if context is None:
            context = {}
        
        # 提取错误类型
        error_type = self._extract_error_type(error_text)
        
        # 提取错误代码
        error_code = self._extract_error_code(error_text)
        
        # 提取错误消息
        error_message = self._extract_error_message(error_text, error_type)
        
        # 提取堆栈跟踪
        stack_trace = self._extract_stack_trace(error_text)
        
        # 生成签名
        signature = self._generate_signature(error_type, error_code, error_message)
        
        return ErrorSignature(
            original_error=error_text,
            signature=signature,
            error_type=error_type,
            error_code=error_code,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context
        )
    
    def _extract_error_type(self, error_text: str) -> str:
        """提取错误类型"""
        for pattern_name, pattern in self.ERROR_PATTERNS.items():
            match = pattern.search(error_text)
            if match:
                if pattern_name in ['java_exception', 'java_error', 'python_exception']:
                    return match.group(1)  # 异常类名
                elif pattern_name == 'http_error':
                    return f"HTTP_{match.group(1)}"
                else:
                    # 返回模式名称作为错误类型
                    return pattern_name.replace('_', ' ').title()
        
        # 如果没有匹配到已知模式，尝试提取第一行作为错误类型
        first_line = error_text.strip().split('\n')[0]
        if len(first_line) > 100:
            first_line = first_line[:100] + "..."
        
        # 提取可能的关键词
        keywords = ['error', 'failed', 'exception', 'crash', 'timeout', 'denied']
        for keyword in keywords:
            if keyword in first_line.lower():
                return f"Generic {keyword.title()}"
        
        return "Unknown Error"
    
    def _extract_error_code(self, error_text: str) -> str:
        """提取错误代码"""
        for pattern in self.ERROR_CODE_PATTERNS:
            match = pattern.search(error_text)
            if match:
                return match.group(1)
        
        # 尝试从常见格式中提取
        # 如：ERROR 500, ErrorCode: 1001, Errno: 13
        code_patterns = [
            r'ERROR\s+(\d+)',
            r'ErrorCode\s*[:=]\s*(\S+)',
            r'Errno\s*[:=]\s*(\d+)',
            r'Code\s*[:=]\s*(\w+)',
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, error_text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_error_message(self, error_text: str, error_type: str) -> str:
        """提取错误消息"""
        # 如果是已知的异常类型，提取异常消息
        if 'Exception' in error_type or 'Error' in error_type:
            # 查找冒号后的消息
            lines = error_text.split('\n')
            for line in lines:
                if error_type in line and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        message = parts[1].strip()
                        if message:
                            # 截断过长的消息
                            if len(message) > 200:
                                message = message[:200] + "..."
                            return message
        
        # 否则提取第一行非空行
        lines = error_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(' ') and not line.startswith('\t'):
                # 截断过长的消息
                if len(line) > 200:
                    line = line[:200] + "..."
                return line
        
        return "No error message extracted"
    
    def _extract_stack_trace(self, error_text: str) -> str:
        """提取堆栈跟踪"""
        if 'Traceback' in error_text or 'at ' in error_text:
            # 提取堆栈跟踪部分
            lines = error_text.split('\n')
            stack_lines = []
            in_stack = False
            
            for line in lines:
                if 'Traceback' in line or ('at ' in line and ('/' in line or '\\' in line)):
                    in_stack = True
                
                if in_stack:
                    stack_lines.append(line)
                
                # 堆栈跟踪通常以空行或非堆栈行结束
                if in_stack and line.strip() == '' and len(stack_lines) > 3:
                    break
            
            if stack_lines:
                return '\n'.join(stack_lines[:20])  # 限制堆栈跟踪长度
        
        return ""
    
    def _generate_signature(self, error_type: str, error_code: str, error_message: str) -> str:
        """生成错误签名"""
        # 构建签名字符串
        signature_parts = []
        
        if error_type:
            signature_parts.append(error_type)
        
        if error_code:
            signature_parts.append(f"CODE:{error_code}")
        
        if error_message:
            # 提取消息中的关键部分（前几个单词）
            words = error_message.split()
            if len(words) > 5:
                key_message = ' '.join(words[:5])
                signature_parts.append(key_message)
            else:
                signature_parts.append(error_message)
        
        signature_str = '|'.join(signature_parts)
        
        # 生成MD5哈希作为唯一标识
        signature_hash = hashlib.md5(signature_str.encode('utf-8')).hexdigest()[:12]
        
        return signature_hash
    
    def extract_from_log_file(self, log_file_path: str, max_errors: int = 100) -> List[ErrorSignature]:
        """
        从日志文件中提取错误签名
        
        Args:
            log_file_path: 日志文件路径
            max_errors: 最大提取错误数
            
        Returns:
            错误签名列表
        """
        signatures = []
        
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                error_buffer = []
                in_error = False
                
                for line in f:
                    line = line.rstrip('\n')
                    
                    # 检查是否是错误行
                    is_error_line = self._is_error_line(line)
                    
                    if is_error_line and not in_error:
                        # 开始新的错误
                        if error_buffer:
                            # 处理之前的错误
                            error_text = '\n'.join(error_buffer)
                            signature = self.extract_signature(error_text, {'source': log_file_path})
                            signatures.append(signature)
                            
                            if len(signatures) >= max_errors:
                                break
                        
                        error_buffer = [line]
                        in_error = True
                    
                    elif in_error:
                        if is_error_line or self._is_continuation_line(line):
                            # 继续错误块
                            error_buffer.append(line)
                        else:
                            # 错误块结束
                            error_text = '\n'.join(error_buffer)
                            signature = self.extract_signature(error_text, {'source': log_file_path})
                            signatures.append(signature)
                            
                            if len(signatures) >= max_errors:
                                break
                            
                            error_buffer = []
                            in_error = False
                    
                    else:
                        # 非错误行，跳过
                        pass
                
                # 处理最后一个错误块
                if error_buffer and len(signatures) < max_errors:
                    error_text = '\n'.join(error_buffer)
                    signature = self.extract_signature(error_text, {'source': log_file_path})
                    signatures.append(signature)
        
        except Exception as e:
            print(f"读取日志文件失败: {log_file_path} - {e}")
        
        return signatures
    
    def _is_error_line(self, line: str) -> bool:
        """判断是否是错误行"""
        line_lower = line.lower()
        
        # 错误关键词
        error_keywords = [
            'error', 'exception', 'failed', 'failure', 'crash',
            'timeout', 'denied', 'rejected', 'invalid', 'illegal',
            'fatal', 'panic', 'segmentation fault', 'core dumped',
            'out of memory', 'oom', 'disk full', 'connection refused',
            'permission denied', 'access denied', 'forbidden',
            'unavailable', 'not found', 'bad request'
        ]
        
        # 错误级别
        error_levels = ['ERROR', 'FATAL', 'CRITICAL', 'SEVERE']
        
        # 检查错误关键词
        for keyword in error_keywords:
            if keyword in line_lower:
                return True
        
        # 检查错误级别（通常在日志开头）
        for level in error_levels:
            if line.startswith(level) or f'[{level}]' in line:
                return True
        
        # 检查常见的错误模式
        error_patterns = [
            r'^\d{4}-\d{2}-\d{2}.*ERROR',
            r'^\d{2}:\d{2}:\d{2}.*ERROR',
            r'\[ERROR\]',
            r'<ERROR>',
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _is_continuation_line(self, line: str) -> bool:
        """判断是否是错误续行（如堆栈跟踪）"""
        # 堆栈跟踪行通常以空格或制表符开头
        if line.startswith(' ') or line.startswith('\t'):
            return True
        
        # 包含 "at " 的行通常是堆栈跟踪
        if ' at ' in line and ('(' in line or ')' in line):
            return True
        
        # 包含文件路径的行
        if '/' in line or '\\' in line:
            return True
        
        return False
    
    def batch_extract(self, log_texts: List[str], contexts: List[Dict[str, Any]] = None) -> List[ErrorSignature]:
        """
        批量提取错误签名
        
        Args:
            log_texts: 日志文本列表
            contexts: 上下文信息列表（可选）
            
        Returns:
            错误签名列表
        """
        signatures = []
        
        if contexts is None:
            contexts = [{}] * len(log_texts)
        
        for i, (log_text, context) in enumerate(zip(log_texts, contexts)):
            try:
                signature = self.extract_signature(log_text, context)
                signatures.append(signature)
            except Exception as e:
                print(f"提取错误签名失败（索引 {i}）: {e}")
        
        return signatures


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='错误签名提取器')
    parser.add_argument('--input', help='输入文件或文本')
    parser.add_argument('--file', action='store_true', help='输入是文件')
    parser.add_argument('--output', help='输出文件（JSON格式）')
    parser.add_argument('--pretty', action='store_true', help='美化输出')
    
    args = parser.parse_args()
    
    extractor = ErrorSignatureExtractor()
    
    if args.input:
        if args.file:
            # 从文件提取
            signatures = extractor.extract_from_log_file(args.input)
        else:
            # 从文本提取
            signature = extractor.extract_signature(args.input)
            signatures = [signature]
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.pretty:
                    json.dump([s.to_dict() for s in signatures], f, ensure_ascii=False, indent=2)
                else:
                    json.dump([s.to_dict() for s in signatures], f, ensure_ascii=False)
            print(f"已保存到: {args.output}")
        else:
            for sig in signatures:
                print(f"签名: {sig.signature}")
                print(f"类型: {sig.error_type}")
                print(f"代码: {sig.error_code}")
                print(f"消息: {sig.error_message[:100]}...")
                print("-" * 50)
    else:
        # 示例
        example_errors = [
            "java.net.ConnectException: Connection refused",
            "ERROR 500: Internal Server Error",
            "Permission denied: /var/log/app.log",
            "OutOfMemoryError: Java heap space",
        ]
        
        print("示例错误签名提取:")
        for error in example_errors:
            signature = extractor.extract_signature(error)
            print(f"原始错误: {error}")
            print(f"提取签名: {signature.signature}")
            print(f"错误类型: {signature.error_type}")
            print(f"错误代码: {signature.error_code}")
            print(f"错误消息: {signature.error_message}")
            print()


if __name__ == '__main__':
    main()