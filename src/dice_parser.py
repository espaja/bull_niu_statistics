#!/usr/bin/env python3
"""
骰子解析器
负责从聊天内容中识别和提取骰子序列
"""
import re
from typing import List, Optional


class DiceParser:
    """骰子解析器类"""
    
    def __init__(self):
        """初始化解析器"""
        # Unicode骰子符号映射
        self.dice_unicode_map = {
            '⚀': 1, '⚁': 2, '⚂': 3, 
            '⚃': 4, '⚄': 5, '⚅': 6
        }
        
        # 骰子Unicode范围正则表达式
        self.dice_pattern = r'[⚀-⚅]'
        
    def extract_dice(self, content: str) -> Optional[List[int]]:
        """
        从文本内容中提取骰子序列
        
        Args:
            content: 包含骰子的文本内容
            
        Returns:
            List[int]: 包含5个骰子值的列表，如果无效则返回None
        """
        if not content:
            return None
            
        # 使用正则表达式查找所有骰子符号
        dice_matches = re.findall(self.dice_pattern, content)
        
        if len(dice_matches) < 5:
            return None
            
        # 转换为数字，只取前5个
        dice_sequence = []
        for dice_char in dice_matches[:5]:
            if dice_char in self.dice_unicode_map:
                dice_sequence.append(self.dice_unicode_map[dice_char])
            else:
                return None  # 发现无效字符
                
        return dice_sequence if len(dice_sequence) == 5 else None
    
    def is_valid_dice_sequence(self, sequence: Optional[List[int]]) -> bool:
        """
        验证骰子序列是否有效
        
        Args:
            sequence: 要验证的骰子序列
            
        Returns:
            bool: 序列是否有效
        """
        if sequence is None:
            return False
            
        if not isinstance(sequence, list):
            return False
            
        if len(sequence) != 5:
            return False
            
        # 检查每个骰子值是否在1-6范围内
        for dice_value in sequence:
            if not isinstance(dice_value, int) or dice_value < 1 or dice_value > 6:
                return False
                
        return True
    
    def extract_dice_robust(self, content: str) -> Optional[List[int]]:
        """
        鲁棒的骰子提取方法，支持多种格式
        
        Args:
            content: 输入文本内容
            
        Returns:
            List[int]: 骰子序列或None
        """
        if not content:
            return None
            
        # 方法1：标准Unicode骰子
        result = self.extract_dice(content)
        if result:
            return result
            
        # 方法2：尝试其他可能的格式（为未来扩展预留）
        # 例如：[骰子:1][骰子:2]... 或 🎲1🎲2... 等格式
        
        return None
    
    def parse_dice_message(self, msg: dict) -> List[int]:
        """
        从消息中解析骰子数据
        支持微信的XML gameext格式
        
        Args:
            msg: 消息字典，包含content和其他信息
            
        Returns:
            List[int]: 解析出的骰子数值列表
        """
        content = msg.get('content', '')
        
        # 方法1: 解析XML gameext格式 <gameext type="2" content="X"></gameext>
        dice_values = self._parse_gameext_dice(content)
        if dice_values:
            return dice_values
            
        # 方法2: 尝试Unicode骰子符号
        dice_values = self.extract_dice(content)
        if dice_values:
            return dice_values
            
        # 方法3: 从contents字段解析
        contents = msg.get('contents', {})
        if isinstance(contents, dict) and 'content' in contents:
            content_value = str(contents['content'])
            # 如果content值直接是数字且在1-6范围内，可能就是骰子值
            try:
                dice_value = int(content_value)
                if 1 <= dice_value <= 6:
                    return [dice_value]
            except (ValueError, TypeError):
                pass
        
        return []
    
    def _parse_gameext_dice(self, content: str) -> List[int]:
        """
        解析XML gameext格式的骰子数据
        格式: <gameext type="2" content="X"></gameext>
        
        Args:
            content: 包含XML的内容字符串
            
        Returns:
            List[int]: 解析出的骰子数值列表
        """
        if not content:
            return []
            
        # 查找所有gameext type="2"的标签
        pattern = r'<gameext[^>]*type="2"[^>]*content="([^"]*)"[^>]*></gameext>'
        matches = re.findall(pattern, content)
        
        dice_values = []
        for match in matches:
            try:
                # 尝试直接转换为整数
                dice_value = int(match)
                if 1 <= dice_value <= 6:
                    dice_values.append(dice_value)
                else:
                    # 如果不在1-6范围内，可能需要映射
                    mapped_value = self._map_content_to_dice(match)
                    if mapped_value:
                        dice_values.append(mapped_value)
            except (ValueError, TypeError):
                # 如果不是直接的数字，尝试映射
                mapped_value = self._map_content_to_dice(match)
                if mapped_value:
                    dice_values.append(mapped_value)
        
        return dice_values
    
    def _map_content_to_dice(self, content_value: str) -> Optional[int]:
        """
        将content值映射到骰子数值
        
        Args:
            content_value: gameext中的content值
            
        Returns:
            int: 对应的骰子数值(1-6)，如果无法映射则返回None
        """
        # 微信骰子的content值到实际骰子值的映射关系
        content_to_dice_map = {
            '4': 1,
            '5': 2, 
            '6': 3,
            '7': 4,
            '8': 5,
            '9': 6
        }
        
        # 如果是字符串格式的content值
        if content_value in content_to_dice_map:
            return content_to_dice_map[content_value]
        
        # 如果是数字格式，先转换为字符串再映射
        try:
            content_str = str(int(content_value))
            if content_str in content_to_dice_map:
                return content_to_dice_map[content_str]
        except (ValueError, TypeError):
            pass
        
        # 如果是直接的骰子数值(1-6)，直接返回
        try:
            dice_value = int(content_value)
            if 1 <= dice_value <= 6:
                return dice_value
        except (ValueError, TypeError):
            pass
        
        return None