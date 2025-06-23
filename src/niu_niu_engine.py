#!/usr/bin/env python3
"""
牛牛游戏规则引擎
实现牛牛游戏的核心逻辑和规则计算
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
from itertools import combinations


@dataclass
class GameResult:
    """游戏结果数据类"""
    type: str           # 结果类型：豹子、牛牛、牛X、没牛
    value: int          # 数值大小，用于比较
    combination: Optional[List[int]] = None  # 组成牛的三个数字
    remaining: Optional[List[int]] = None    # 剩余的两个数字


class NiuNiuEngine:
    """牛牛游戏规则引擎"""
    
    def __init__(self):
        """初始化游戏引擎"""
        pass
    
    def calculate_result(self, dice: List[int]) -> GameResult:
        """
        计算骰子的牛牛结果
        
        Args:
            dice: 5个骰子的列表
            
        Returns:
            GameResult: 游戏结果
        """
        if len(dice) != 5:
            raise ValueError("骰子数量必须是5个")
            
        # 1. 检查是否为豹子
        if self._is_baozi(dice):
            return GameResult(type="豹子", value=10)
            
        # 2. 检查是否有牛
        niu_combinations = self._find_niu_combinations(dice)
        
        if not niu_combinations:
            return GameResult(type="没牛", value=0)
            
        # 3. 找到最佳的牛牛组合
        best_result = self._find_best_combination(niu_combinations)
        
        return best_result
    
    def _is_baozi(self, dice: List[int]) -> bool:
        """
        判断是否为豹子（五个相同数字）
        
        Args:
            dice: 骰子列表
            
        Returns:
            bool: 是否为豹子
        """
        return len(set(dice)) == 1
    
    def _find_niu_combinations(self, dice: List[int]) -> List[Tuple[List[int], List[int], int]]:
        """
        找出所有可能的牛牛组合
        
        Args:
            dice: 骰子列表
            
        Returns:
            List[Tuple]: 每个元组包含(三个数字组合, 剩余两个数字, 牛值)
        """
        combinations_found = []
        
        # 枚举所有3个数字的组合
        for three_dice in combinations(dice, 3):
            if sum(three_dice) % 10 == 0:
                # 找到剩余的两个数字
                remaining_dice = []
                dice_copy = dice.copy()
                
                for num in three_dice:
                    dice_copy.remove(num)
                    
                remaining_dice = dice_copy
                
                # 计算牛值
                niu_value = sum(remaining_dice) % 10
                if niu_value == 0:
                    niu_value = 10  # 牛牛
                    
                combinations_found.append((list(three_dice), remaining_dice, niu_value))
                
        return combinations_found
    
    def _find_best_combination(self, combinations: List[Tuple[List[int], List[int], int]]) -> GameResult:
        """
        从多个牛牛组合中找到最佳结果
        
        Args:
            combinations: 所有可能的组合列表
            
        Returns:
            GameResult: 最佳结果
        """
        if not combinations:
            return GameResult(type="没牛", value=0)
            
        # 找到牛值最大的组合
        best_combination = max(combinations, key=lambda x: x[2])
        three_dice, remaining_dice, niu_value = best_combination
        
        # 生成结果类型描述
        if niu_value == 10:
            result_type = "牛牛"
        else:
            result_type = f"牛{niu_value}"
            
        return GameResult(
            type=result_type,
            value=niu_value,
            combination=three_dice,
            remaining=remaining_dice
        )
    
    def compare_results(self, result1: GameResult, result2: GameResult) -> int:
        """
        比较两个游戏结果
        
        Args:
            result1: 第一个结果
            result2: 第二个结果
            
        Returns:
            int: 1表示result1胜, -1表示result2胜, 0表示平局
        """
        # 豹子特殊处理
        if result1.type == "豹子" and result2.type != "豹子":
            return 1
        elif result2.type == "豹子" and result1.type != "豹子":
            return -1
        elif result1.type == "豹子" and result2.type == "豹子":
            return 0  # 都是豹子，平局
            
        # 比较牛值
        if result1.value > result2.value:
            return 1
        elif result1.value < result2.value:
            return -1
        else:
            return 0
    
    def get_winner(self, player1_dice: List[int], player2_dice: List[int]) -> Optional[str]:
        """
        判断两个玩家谁获胜
        
        Args:
            player1_dice: 玩家1的骰子
            player2_dice: 玩家2的骰子
            
        Returns:
            str: "player1", "player2", 或 None(平局)
        """
        result1 = self.calculate_result(player1_dice)
        result2 = self.calculate_result(player2_dice)
        
        comparison = self.compare_results(result1, result2)
        
        if comparison > 0:
            return "player1"
        elif comparison < 0:
            return "player2"
        else:
            return None  # 平局