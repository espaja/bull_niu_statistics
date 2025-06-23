#!/usr/bin/env python3
"""
测试用例：验证骰子识别和解析功能
"""
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from dice_parser import DiceParser


class TestDiceParser(unittest.TestCase):
    """测试骰子解析功能"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = DiceParser()
        
    def test_unicode_dice_recognition(self):
        """测试：Unicode骰子符号识别"""
        test_cases = [
            ("⚀⚁⚂⚃⚄", [1, 2, 3, 4, 5]),  # 标准5个骰子
            ("⚅⚄⚃⚂⚁", [6, 5, 4, 3, 2]),  # 反序骰子
            ("⚀⚀⚀⚀⚀", [1, 1, 1, 1, 1]),  # 豹子
            ("⚅⚅⚅⚅⚅", [6, 6, 6, 6, 6]),  # 6的豹子
        ]
        
        for content, expected in test_cases:
            with self.subTest(content=content):
                result = self.parser.extract_dice(content)
                self.assertEqual(result, expected, f"解析失败: {content}")
                
    def test_mixed_content_dice_extraction(self):
        """测试：混合内容中的骰子提取"""
        test_cases = [
            ("来玩牛牛 ⚀⚁⚂⚃⚄", [1, 2, 3, 4, 5]),
            ("⚀⚁⚂⚃⚄ 我的骰子", [1, 2, 3, 4, 5]),
            ("哈哈 ⚀⚁⚂⚃⚄ 太好了", [1, 2, 3, 4, 5]),
            ("等等⚀⚁⚂⚃⚄继续", [1, 2, 3, 4, 5]),
        ]
        
        for content, expected in test_cases:
            with self.subTest(content=content):
                result = self.parser.extract_dice(content)
                self.assertEqual(result, expected, f"混合内容解析失败: {content}")
                
    def test_invalid_dice_content(self):
        """测试：无效骰子内容"""
        invalid_cases = [
            "没有骰子",
            "⚀⚁⚂⚃",  # 少于5个
            "⚀⚁⚂",    # 只有3个
            "普通文字内容",
            "",
            "数字12345",  # 普通数字
        ]
        
        for content in invalid_cases:
            with self.subTest(content=content):
                result = self.parser.extract_dice(content)
                self.assertIsNone(result, f"应该返回None: {content}")
                
    def test_excess_dice_handling(self):
        """测试：超过5个骰子的处理"""
        test_cases = [
            ("⚀⚁⚂⚃⚄⚅", [1, 2, 3, 4, 5]),  # 6个取前5个
            ("⚀⚁⚂⚃⚄⚅⚀⚁", [1, 2, 3, 4, 5]),  # 8个取前5个
        ]
        
        for content, expected in test_cases:
            with self.subTest(content=content):
                result = self.parser.extract_dice(content)
                self.assertEqual(result, expected, f"多骰子处理失败: {content}")
                
    def test_dice_validation(self):
        """测试：骰子有效性验证"""
        valid_sequences = [
            [1, 2, 3, 4, 5],
            [6, 6, 6, 6, 6],
            [1, 1, 1, 1, 1],
            [3, 1, 4, 1, 5],
        ]
        
        for sequence in valid_sequences:
            with self.subTest(sequence=sequence):
                self.assertTrue(self.parser.is_valid_dice_sequence(sequence))
                
        invalid_sequences = [
            [1, 2, 3, 4],     # 少于5个
            [1, 2, 3, 4, 7],  # 包含无效数字
            [0, 1, 2, 3, 4],  # 包含0
            [1, 2, 3, 4, 5, 6],  # 多于5个
            [],               # 空序列
            None,             # None值
        ]
        
        for sequence in invalid_sequences:
            with self.subTest(sequence=sequence):
                self.assertFalse(self.parser.is_valid_dice_sequence(sequence))


if __name__ == '__main__':
    unittest.main(verbosity=2)