#!/usr/bin/env python3
"""
AI解决方案生成器
调用AI接口（如OpenAI API或本地模型）生成解决方案
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AISolution:
    """AI生成的解决方案"""
    signature: str           # 错误签名
    error_summary: str       # 错误摘要
    solution: str            # 解决方案
    confidence: float        # 置信度 (0.0-1.0)
    reasoning: str           # 推理过程
    category: str            # 分类
    severity: str            # 严重级别
    tags: List[str]          # 标签
    model: str               # 使用的模型
    timestamp: str           # 生成时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class AISolutionGenerator:
    """AI解决方案生成器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化AI生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config.get('api_key')
        self.base_url = self.config.get('base_url', 'https://api.openai.com/v1')
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = self.config.get('max_tokens', 2000)
        self.temperature = self.config.get('temperature', 0.7)
        
        # 本地模型配置
        self.local_model_enabled = self.config.get('local_model_enabled', False)
        self.local_model_url = self.config.get('local_model_url', 'http://localhost:8000/v1')
        self.local_model_name = self.config.get('local_model_name', 'local-llm')
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            'api_key': os.environ.get('OPENAI_API_KEY', ''),
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo',
            'max_tokens': 2000,
            'temperature': 0.7,
            'local_model_enabled': False,
            'local_model_url': 'http://localhost:8000/v1',
            'local_model_name': 'local-llm',
            'categories': ['system', 'network', 'database', 'application', 'security', 'performance'],
            'severities': ['CRITICAL', 'ERROR', 'WARNING', 'INFO'],
            'default_tags': ['ai-generated', 'needs-review']
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"加载配置文件失败: {config_path} - {e}")
        
        return default_config
    
    def generate_solution(self, error_signature: str, error_context: Dict[str, Any]) -> AISolution:
        """
        生成解决方案
        
        Args:
            error_signature: 错误签名
            error_context: 错误上下文信息
            
        Returns:
            AISolution对象
        """
        # 构建提示词
        prompt = self._build_prompt(error_signature, error_context)
        
        # 调用AI接口
        response = self._call_ai_api(prompt)
        
        # 解析响应
        solution_data = self._parse_response(response, error_signature, error_context)
        
        return solution_data
    
    def _build_prompt(self, error_signature: str, error_context: Dict[str, Any]) -> str:
        """构建提示词"""
        error_text = error_context.get('error_text', '')
        error_type = error_context.get('error_type', '')
        error_code = error_context.get('error_code', '')
        system_info = error_context.get('system_info', {})
        log_source = error_context.get('log_source', '')
        
        prompt = f"""你是一个经验丰富的运维工程师。请根据以下错误信息，提供专业的解决方案。

错误签名: {error_signature}
错误类型: {error_type}
错误代码: {error_code}
日志来源: {log_source}

错误详情:
{error_text}

系统信息:
{json.dumps(system_info, ensure_ascii=False, indent=2) if system_info else '无'}

请按照以下格式提供解决方案:

## 错误摘要
[用一句话概括错误]

## 根本原因分析
[分析错误的根本原因，包括可能的技术原因、配置问题、资源限制等]

## 解决方案

### 紧急处理步骤
1. [第一步]
2. [第二步]
3. [第三步]

### 根本解决方案
1. [长期解决方案1]
2. [长期解决方案2]

### 验证方法
1. [如何验证问题已解决]
2. [监控指标]

## 预防措施
1. [预防措施1]
2. [预防措施2]

## 分类
[从以下分类中选择: {', '.join(self.config['categories'])}]

## 严重级别
[从以下级别中选择: {', '.join(self.config['severities'])}]

## 标签
[相关标签，用逗号分隔]

请确保解决方案:
1. 具体可行，有明确的步骤
2. 包含命令、配置示例等具体内容
3. 考虑生产环境的稳定性
4. 提供验证方法
5. 包含预防措施

现在请提供解决方案:"""
        
        return prompt
    
    def _call_ai_api(self, prompt: str) -> Dict[str, Any]:
        """调用AI API"""
        if self.local_model_enabled:
            return self._call_local_model(prompt)
        else:
            return self._call_openai_api(prompt)
    
    def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """调用OpenAI API"""
        if not self.api_key:
            raise ValueError("OpenAI API密钥未设置，请设置OPENAI_API_KEY环境变量或配置文件中设置api_key")
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的运维工程师，擅长解决各种系统、网络、数据库和应用问题。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': 0.9,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"调用OpenAI API失败: {e}")
    
    def _call_local_model(self, prompt: str) -> Dict[str, Any]:
        """调用本地模型"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.local_model_name,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的运维工程师，擅长解决各种系统、网络、数据库和应用问题。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }
        
        try:
            response = requests.post(
                f'{self.local_model_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"调用本地模型失败: {e}")
    
    def _parse_response(self, response: Dict[str, Any], error_signature: str, 
                       error_context: Dict[str, Any]) -> AISolution:
        """解析AI响应"""
        try:
            # 提取响应文本
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
            else:
                content = str(response)
            
            # 解析响应内容
            parsed_data = self._parse_solution_content(content)
            
            # 构建解决方案对象
            solution = AISolution(
                signature=error_signature,
                error_summary=parsed_data.get('error_summary', ''),
                solution=content,  # 保留原始内容
                confidence=parsed_data.get('confidence', 0.8),
                reasoning=parsed_data.get('reasoning', ''),
                category=parsed_data.get('category', 'unknown'),
                severity=parsed_data.get('severity', 'ERROR'),
                tags=parsed_data.get('tags', []) + self.config['default_tags'],
                model=self.model if not self.local_model_enabled else self.local_model_name,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return solution
            
        except Exception as e:
            # 如果解析失败，返回默认解决方案
            return AISolution(
                signature=error_signature,
                error_summary=f"自动生成的解决方案（解析失败: {str(e)}）",
                solution=content if 'content' in locals() else "AI响应解析失败，请人工处理。",
                confidence=0.3,
                reasoning="解析AI响应时出错",
                category='unknown',
                severity='ERROR',
                tags=['ai-generated', 'needs-review', 'parse-error'],
                model=self.model if not self.local_model_enabled else self.local_model_name,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
    
    def _parse_solution_content(self, content: str) -> Dict[str, Any]:
        """解析解决方案内容"""
        parsed = {
            'error_summary': '',
            'confidence': 0.8,
            'reasoning': '',
            'category': 'unknown',
            'severity': 'ERROR',
            'tags': []
        }
        
        lines = content.split('\n')
        
        # 提取错误摘要
        for i, line in enumerate(lines):
            if line.strip().startswith('## 错误摘要'):
                if i + 1 < len(lines):
                    parsed['error_summary'] = lines[i + 1].strip()
                break
        
        # 提取分类
        for i, line in enumerate(lines):
            if line.strip().startswith('## 分类'):
                if i + 1 < len(lines):
                    category = lines[i + 1].strip().strip('[]')
                    if category in self.config['categories']:
                        parsed['category'] = category
                break
        
        # 提取严重级别
        for i, line in enumerate(lines):
            if line.strip().startswith('## 严重级别'):
                if i + 1 < len(lines):
                    severity = lines[i + 1].strip().strip('[]')
                    if severity in self.config['severities']:
                        parsed['severity'] = severity
                break
        
        # 提取标签
        for i, line in enumerate(lines):
            if line.strip().startswith('## 标签'):
                if i + 1 < len(lines):
                    tags_text = lines[i + 1].strip().strip('[]')
                    parsed['tags'] = [tag.strip() for tag in tags_text.split(',')]
                break
        
        # 提取推理过程（从根本原因分析中）
        reasoning_lines = []
        in_reasoning = False
        for line in lines:
            if line.strip().startswith('## 根本原因分析'):
                in_reasoning = True
                continue
            elif in_reasoning and line.strip().startswith('##'):
                break
            elif in_reasoning:
                reasoning_lines.append(line.strip())
        
        if reasoning_lines:
            parsed['reasoning'] = ' '.join(reasoning_lines)
        
        return parsed
    
    def batch_generate(self, error_signatures: List[str], 
                      error_contexts: List[Dict[str, Any]]) -> List[AISolution]:
        """
        批量生成解决方案
        
        Args:
            error_signatures: 错误签名列表
            error_contexts: 错误上下文列表
            
        Returns:
            AISolution对象列表
        """
        solutions = []
        
        for signature, context in zip(error_signatures, error_contexts):
            try:
                solution = self.generate_solution(signature, context)
                solutions.append(solution)
                print(f"已生成解决方案: {signature}")
                
                # 避免频繁调用API
                time.sleep(1)
                
            except Exception as e:
                print(f"生成解决方案失败: {signature} - {e}")
                # 创建失败的占位符
                failed_solution = AISolution(
                    signature=signature,
                    error_summary=f"生成失败: {str(e)}",
                    solution="AI生成失败，请人工处理。",
                    confidence=0.0,
                    reasoning=str(e),
                    category='unknown',
                    severity='ERROR',
                    tags=['ai-generated', 'needs-review', 'generation-failed'],
                    model=self.model if not self.local_model_enabled else self.local_model_name,
                    timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                )
                solutions.append(failed_solution)
        
        return solutions
    
    def save_solutions(self, solutions: List[AISolution], output_dir: str):
        """
        保存解决方案到文件
        
        Args:
            solutions: 解决方案列表
            output_dir: 输出目录
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # 保存为JSON文件
        output_file = output_dir / f"ai_solutions_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([s.to_dict() for s in solutions], f, ensure_ascii=False, indent=2)
        
        # 保存为文本文件（便于阅读）
        text_file = output_dir / f"ai_solutions_{timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            for solution in solutions:
                f.write(f"=== 解决方案: {solution.signature} ===\n")
                f.write(f"错误摘要: {solution.error_summary}\n")
                f.write(f"分类: {solution.category}\n")
                f.write(f"严重级别: {solution.severity}\n")
                f.write(f"置信度: {solution.confidence:.2f}\n")
                f.write(f"标签: {', '.join(solution.tags)}\n")
                f.write(f"生成时间: {solution.timestamp}\n")
                f.write(f"模型: {solution.model}\n")
                f.write(f"\n解决方案:\n{solution.solution}\n")
                f.write(f"\n推理过程:\n{solution.reasoning}\n")
                f.write("\n" + "="*50 + "\n\n")
        
        return output_file, text_file


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI解决方案生成器')
    parser.add_argument('--config', help='配置文件路径', default='config/ai-config.yaml')
    parser.add_argument('--error', help='错误文本')
    parser.add_argument('--signature', help='错误签名')
    parser.add_argument('--type', help='错误类型', default='')
    parser.add_argument('--code', help='错误代码', default='')
    parser.add_argument('--source', help='日志来源', default='')
    parser.add_argument('--output', help='输出目录', default='./ai_solutions')
    parser.add_argument('--batch', help='批量处理文件（JSON格式）')
    
    args = parser.parse_args()
    
    generator = AISolutionGenerator(args.config)
    
    if args.batch:
        # 批量处理
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            error_signatures = []
            error_contexts = []
            
            for item in batch_data:
                error_signatures.append(item.get('signature', ''))
                error_contexts.append({
                    'error_text': item.get('error_text', ''),
                    'error_type': item.get('error_type', ''),
                    'error_code': item.get('error_code', ''),
                    'log_source': item.get('log_source', ''),
                    'system_info': item.get('system_info', {})
                })
            
            solutions = generator.batch_generate(error_signatures, error_contexts)
            
            # 保存结果
            json_file, text_file = generator.save_solutions(solutions, args.output)
            print(f"批量处理完成，生成 {len(solutions)} 个解决方案")
            print(f"JSON文件: {json_file}")
            print(f"文本文件: {text_file}")
            
        except Exception as e:
            print(f"批量处理失败: {e}")
    
    elif args.error:
        # 单个错误处理
        error_context = {
            'error_text': args.error,
            'error_type': args.type,
            'error_code': args.code,
            'log_source': args.source,
            'system_info': {}
        }
        
        signature = args.signature
        if not signature:
            # 如果没有提供签名，使用错误文本的前50个字符作为签名
            signature = args.error[:50].replace('\n', ' ').replace('\r', '')
        
        try:
            solution = generator.generate_solution(signature, error_context)
            
            print(f"=== AI生成的解决方案 ===\n")
            print(f"错误签名: {solution.signature}")
            print(f"错误摘要: {solution.error_summary}")
            print(f"分类: {solution.category}")
            print(f"严重级别: {solution.severity}")
            print(f"置信度: {solution.confidence:.2f}")
            print(f"标签: {', '.join(solution.tags)}")
            print(f"生成时间: {solution.timestamp}")
            print(f"模型: {solution.model}")
            print(f"\n解决方案:\n{solution.solution}")
            
            # 保存到文件
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f"solution_{signature[:20]}_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(solution.to_json())
            
            print(f"\n解决方案已保存到: {output_file}")
            
        except Exception as e:
            print(f"生成解决方案失败: {e}")
    
    else:
        # 示例
        print("AI解决方案生成器")
        print("用法:")
        print("  单个错误: python ai_solution_generator.py --error \"错误文本\" --type \"错误类型\"")
        print("  批量处理: python ai_solution_generator.py --batch errors.json")
        print("\n示例:")
        print('  python ai_solution_generator.py --error "java.net.ConnectException: Connection refused" --type "ConnectionException" --code "CONN_REFUSED"')


if __name__ == '__main__':
    main()