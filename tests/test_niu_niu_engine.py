#!/usr/bin/env python3
"""
测试用例：验证牛牛游戏规则引擎
"""
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from niu_niu_engine import NiuNiuEngine, GameResult


class TestNiuNiuEngine(unittest.TestCase):
    """测试牛牛游戏规则引擎"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = NiuNiuEngine()
        
    def test_baozi_recognition(self):
        """测试：豹子识别"""
        baozi_cases = [
            ([1, 1, 1, 1, 1], "豹子", 10),
            ([2, 2, 2, 2, 2], "豹子", 10),
            ([6, 6, 6, 6, 6], "豹子", 10),
        ]
        
        for dice, expected_type, expected_value in baozi_cases:
            with self.subTest(dice=dice):
                result = self.engine.calculate_result(dice)
                self.assertEqual(result.type, expected_type)
                self.assertEqual(result.value, expected_value)
                
    def test_niu_niu_recognition(self):
        """测试：牛牛识别（剩余两骰子和为10）"""
        niu_niu_cases = [
            ([3, 2, 5, 6, 4], "牛牛", 10),  # 3+2+5=10, 剩余6+4=10
            ([1, 3, 6, 5, 5], "牛牛", 10),  # 1+3+6=10, 剩余5+5=10
        ]
        
        for dice, expected_type, expected_value in niu_niu_cases:
            with self.subTest(dice=dice):
                result = self.engine.calculate_result(dice)
                self.assertEqual(result.type, expected_type, f"骰子{dice}应该是牛牛")
                self.assertEqual(result.value, expected_value)
                
    def test_regular_niu_recognition(self):
        """测试：普通牛X识别"""
        regular_niu_cases = [
            ([1, 4, 5, 2, 3], "牛5", 5),   # 1+4+5=10, 剩余2+3=5
            ([1, 6, 3, 2, 4], "牛6", 6),   # 1+6+3=10, 剩余2+4=6
            ([2, 2, 6, 1, 6], "牛7", 7),   # 2+2+6=10, 剩余1+6=7 
            ([1, 3, 6, 2, 6], "牛8", 8),   # 1+3+6=10, 剩余2+6=8
        ]
        
        for dice, expected_type, expected_value in regular_niu_cases:
            with self.subTest(dice=dice):
                result = self.engine.calculate_result(dice)
                self.assertEqual(result.type, expected_type, f"骰子{dice}结果错误")
                self.assertEqual(result.value, expected_value)
                
    def test_no_niu_recognition(self):
        """测试：没牛识别"""
        no_niu_cases = [
            ([1, 1, 2, 2, 3]),  # 任意三个都不能组成10的倍数
            ([6, 6, 6, 1, 2]),  # 6+6+6=18, 6+6+1=13, 6+6+2=14, 6+1+2=9, 都不是10的倍数
        ]
        
        for dice in no_niu_cases:
            with self.subTest(dice=dice):
                result = self.engine.calculate_result(dice)
                self.assertEqual(result.type, "没牛", f"骰子{dice}应该是没牛")
                self.assertEqual(result.value, 0)
                
    def test_niu_value_calculation_with_overflow(self):
        """测试：牛值计算（处理>10的情况）"""
        overflow_cases = [
            ([1, 3, 6, 5, 6], "牛1", 1),   # 1+3+6=10, 剩余5+6=11, 11-10=1
            ([1, 4, 5, 6, 6], "牛2", 2),   # 1+4+5=10, 剩余6+6=12, 12-10=2
            ([2, 2, 6, 3, 6], "牛9", 9),   # 2+2+6=10, 剩余3+6=9
        ]
        
        for dice, expected_type, expected_value in overflow_cases:
            with self.subTest(dice=dice):
                result = self.engine.calculate_result(dice)
                self.assertEqual(result.type, expected_type)
                self.assertEqual(result.value, expected_value)
                
    def test_multiple_niu_combinations(self):
        """测试：多种牛牛组合的情况，应选择最佳结果"""
        # 例如：[2, 4, 4, 3, 7] 可以有多种组合
        # 2+4+4=10, 剩余3+7=10 -> 牛牛
        # 其他组合可能产生更低的牛值
        test_dice = [2, 4, 4, 3, 7]
        result = self.engine.calculate_result(test_dice)
        
        # 应该选择最佳结果（牛牛）
        self.assertEqual(result.type, "牛牛")
        self.assertEqual(result.value, 10)
        
    def test_game_result_comparison(self):
        """测试：游戏结果比较"""
        # 豹子 > 牛牛 > 牛9 > ... > 牛1 > 没牛
        results = [
            self.engine.calculate_result([6, 6, 6, 6, 6]),  # 豹子
            self.engine.calculate_result([3, 2, 5, 6, 4]),  # 牛牛
            self.engine.calculate_result([2, 2, 6, 3, 6]),  # 牛9
            self.engine.calculate_result([1, 4, 5, 2, 3]),  # 牛5
            self.engine.calculate_result([1, 3, 6, 5, 6]),  # 牛1
            self.engine.calculate_result([6, 6, 6, 1, 2]),  # 没牛
        ]
        
        # 验证排序是否正确（豹子特殊处理）
        expected_order = ["豹子", "牛牛", "牛9", "牛5", "牛1", "没牛"]
        for i, result in enumerate(results):
            self.assertEqual(result.type, expected_order[i], 
                           f"位置{i}应该是{expected_order[i]}，实际是{result.type}")
            
        # 验证value比较逻辑（豹子和没牛特殊处理）
        self.assertEqual(results[0].value, 10)  # 豹子
        self.assertEqual(results[1].value, 10)  # 牛牛
        self.assertEqual(results[2].value, 9)   # 牛9
        self.assertEqual(results[3].value, 5)   # 牛5
        self.assertEqual(results[4].value, 1)   # 牛1
        self.assertEqual(results[5].value, 0)   # 没牛


if __name__ == '__main__':
    unittest.main(verbosity=2)