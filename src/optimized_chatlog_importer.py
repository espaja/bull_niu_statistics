#!/usr/bin/env python3
"""
优化的Chatlog数据导入器
专门针对牛牛游戏数据进行精确获取和预过滤，减少误导性数据
"""
import json
import requests
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import re
from collections import defaultdict

from dice_parser import DiceParser
from niu_niu_engine import NiuNiuEngine


@dataclass
class FilteredDiceMessage:
    """预过滤的骰子消息"""
    seq: int
    timestamp: int
    datetime: str
    player_id: str
    player_name: str
    dice_values: List[int]
    dice_count: int
    msg_type: int
    content: str
    md5_value: str
    content_value: str
    confidence_score: float  # 置信度分数


class OptimizedChatlogImporter:
    """优化的Chatlog数据导入器"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5030"):
        """
        初始化导入器
        
        Args:
            api_base_url: chatlog HTTP API地址
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.dice_parser = DiceParser()
        self.niu_niu_engine = NiuNiuEngine()
        
        # 牛牛相关关键词（用于内容过滤）
        self.niu_niu_keywords = {
            '牛牛', '斗牛', '骰子', '🎲', '摇骰子', 
            '比大小', '对战', '来一局', '再来',
            'niu', 'bull'
        }
        
        # 测试性骰子模式（用于排除）
        self.test_patterns = {
            '测试', 'test', '试试', '练习', '试一下',
            '看看', '随便', '无聊', '玩玩'
        }
    
    def fetch_optimized_dice_data(self, 
                                 group_name: str,
                                 date: str,
                                 enable_smart_filter: bool = True,
                                 confidence_threshold: float = 0.7) -> List[FilteredDiceMessage]:
        """
        获取优化的骰子数据
        
        Args:
            group_name: 群聊名称
            date: 日期范围
            enable_smart_filter: 是否启用智能过滤
            confidence_threshold: 置信度阈值
            
        Returns:
            List[FilteredDiceMessage]: 过滤后的骰子消息列表
        """
        print(f"🎯 优化获取牛牛数据")
        print(f"=" * 50)
        print(f"群聊: {group_name}")
        print(f"日期: {date}")
        print(f"智能过滤: {'开启' if enable_smart_filter else '关闭'}")
        print(f"置信度阈值: {confidence_threshold}")
        print(f"=" * 50)
        
        # 1. 获取原始消息（使用优化的API参数）
        raw_messages = self._fetch_raw_messages_optimized(group_name, date)
        if not raw_messages:
            return []
        
        # 2. 预筛选骰子消息
        dice_messages = self._pre_filter_dice_messages(raw_messages)
        print(f"📊 预筛选: {len(raw_messages)} -> {len(dice_messages)} 条骰子消息")
        
        # 3. 应用智能过滤
        if enable_smart_filter:
            filtered_messages = self._apply_smart_filter(dice_messages, confidence_threshold)
            print(f"🧠 智能过滤: {len(dice_messages)} -> {len(filtered_messages)} 条高质量消息")
            return filtered_messages
        else:
            # 转换为FilteredDiceMessage格式
            return [self._convert_to_filtered_message(msg, 1.0) for msg in dice_messages]
    
    def _fetch_raw_messages_optimized(self, group_name: str, date: str) -> List[Dict]:
        """使用优化参数获取原始消息"""
        print(f"📡 连接chatlog API...")
        
        if not self.test_connection():
            print(f"❌ 无法连接到chatlog API")
            return []
        print(f"✅ API连接成功")
        
        # 优化的API参数
        url = f"{self.api_base_url}/api/v1/chatlog"
        base_params = {
            'talker': group_name,
            'time': date,
            'format': 'json',
            'limit': 2000,  # 每次获取2000条
            'offset': 0
        }
        
        all_messages = []
        current_offset = 0
        batch_size = 2000
        batch_count = 0
        
        print(f"📥 开始批量获取消息 (每批{batch_size}条)...")
        
        while True:
            batch_count += 1
            params = base_params.copy()
            params['limit'] = batch_size
            params['offset'] = current_offset
            
            try:
                response = requests.get(url, params=params, timeout=60)  # 增加超时时间
                response.raise_for_status()
                
                data = response.json()
                if isinstance(data, list):
                    message_data = data
                else:
                    message_data = data.get('data', [])
                
                if not message_data:
                    break
                
                # 转换为标准格式
                batch_messages = []
                for item in message_data:
                    msg = self._standardize_message(item)
                    if msg:
                        batch_messages.append(msg)
                
                all_messages.extend(batch_messages)
                print(f"  批次 {batch_count}: 获取第 {current_offset+1}-{current_offset+len(batch_messages)} 条消息")
                
                if len(message_data) < batch_size:
                    print(f"  📋 已获取所有数据 (最后一批获取了{len(message_data)}条)")
                    break
                
                current_offset += batch_size
                print(f"  🔄 准备获取下一批，offset: {current_offset}")
                time.sleep(0.2)  # 适当延迟避免请求过快
                
            except requests.RequestException as e:
                print(f"❌ API请求失败: {e}")
                break
            except Exception as e:
                print(f"❌ 数据处理失败: {e}")
                break
        
        print(f"✅ 总共获取 {len(all_messages)} 条原始消息")
        return all_messages
    
    def _standardize_message(self, item: Dict) -> Optional[Dict]:
        """标准化消息格式"""
        try:
            return {
                'seq': item.get('seq', 0),
                'time': item.get('time', ''),
                'timestamp': self._parse_timestamp(item.get('time', '')),
                'datetime': self._parse_datetime(item.get('time', '')),
                'talker': item.get('talker', ''),
                'talker_name': item.get('talkerName', ''),
                'sender': item.get('sender', ''),
                'sender_name': item.get('senderName', ''),
                'msg_type': item.get('type', 0),
                'sub_type': item.get('subType', 0),
                'content': item.get('content', ''),
                'contents': item.get('contents', {})
            }
        except Exception:
            return None
    
    def _parse_timestamp(self, time_str: str) -> int:
        """解析时间戳"""
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except:
            return 0
    
    def _parse_datetime(self, time_str: str) -> str:
        """解析为标准日期时间格式"""
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return time_str
    
    def _pre_filter_dice_messages(self, messages: List[Dict]) -> List[Dict]:
        """预筛选骰子消息"""
        dice_messages = []
        
        for msg in messages:
            # 1. 基本类型过滤
            if not self._is_potential_dice_message(msg):
                continue
            
            # 2. 解析骰子内容
            dice_values = self._extract_dice_values(msg)
            if not dice_values:
                continue
            
            # 3. 添加骰子信息
            msg['dice_values'] = dice_values
            msg['dice_count'] = len(dice_values)
            msg['md5_value'] = self._extract_md5_value(msg)
            msg['content_value'] = self._extract_content_value(msg)
            
            dice_messages.append(msg)
        
        return dice_messages
    
    def _is_potential_dice_message(self, msg: Dict) -> bool:
        """判断是否为潜在的骰子消息"""
        msg_type = msg.get('msg_type', 0)
        content = msg.get('content', '')
        
        # 关键条件：消息类型为47且包含gameext type="2"
        if msg_type == 47 and 'gameext' in content and 'type="2"' in content:
            return True
        
        # 检查内容中是否包含骰子相关信息
        if any(keyword in content.lower() for keyword in ['dice', '骰子', '🎲']):
            return True
        
        # 检查是否包含MD5格式的内容（骰子动画的特征）
        if re.search(r'[a-f0-9]{32}', content):
            return True
        
        return False
    
    def _extract_dice_values(self, msg: Dict) -> List[int]:
        """提取骰子数值"""
        try:
            return self.dice_parser.parse_dice_message(msg)
        except:
            return []
    
    def _extract_md5_value(self, msg: Dict) -> str:
        """提取MD5值"""
        content = msg.get('content', '')
        md5_match = re.search(r'([a-f0-9]{32})', content)
        return md5_match.group(1) if md5_match else ''
    
    def _extract_content_value(self, msg: Dict) -> str:
        """提取content值"""
        contents = msg.get('contents', {})
        if 'content' in contents:
            return str(contents['content'])
        return msg.get('content', '')
    
    def _apply_smart_filter(self, dice_messages: List[Dict], 
                          confidence_threshold: float) -> List[FilteredDiceMessage]:
        """应用智能过滤算法"""
        print(f"🧠 应用智能过滤算法...")
        
        # 按时间严格排序
        dice_messages.sort(key=lambda x: x['seq'])
        
        # 分析消息上下文，计算置信度
        filtered_messages = []
        
        for i, msg in enumerate(dice_messages):
            confidence = self._calculate_message_confidence(msg, dice_messages, i)
            
            if confidence >= confidence_threshold:
                filtered_msg = self._convert_to_filtered_message(msg, confidence)
                filtered_messages.append(filtered_msg)
        
        return filtered_messages
    
    def _calculate_message_confidence(self, msg: Dict, all_messages: List[Dict], index: int) -> float:
        """计算消息的置信度"""
        confidence = 0.8  # 基础置信度
        
        # 1. 检查消息内容特征
        content = msg.get('content', '').lower()
        
        # 降低置信度的因素
        for test_pattern in self.test_patterns:
            if test_pattern in content:
                confidence -= 0.3
                break
        
        # 提高置信度的因素
        for keyword in self.niu_niu_keywords:
            if keyword in content:
                confidence += 0.1
                break
        
        # 2. 检查时间上下文（前后消息）
        context_window = 5
        start_idx = max(0, index - context_window)
        end_idx = min(len(all_messages), index + context_window + 1)
        
        context_messages = all_messages[start_idx:end_idx]
        
        # 计算上下文中的骰子密度
        dice_count = sum(1 for m in context_messages if m.get('dice_count', 0) > 0)
        dice_density = dice_count / len(context_messages)
        
        if dice_density > 0.5:  # 高骰子密度
            confidence += 0.2
        elif dice_density < 0.1:  # 低骰子密度
            confidence -= 0.1
        
        # 3. 检查参与者模式
        context_players = set(m.get('sender', '') for m in context_messages)
        
        if len(context_players) >= 2:  # 多人参与
            confidence += 0.15
        
        # 4. 检查骰子数量模式
        dice_count = msg.get('dice_count', 0)
        
        if dice_count == 5:  # 完整5骰子
            confidence += 0.1
        elif dice_count == 1:  # 单个骰子（可能是连续投掷）
            # 检查前后是否有同一玩家的其他骰子
            player_id = msg.get('sender', '')
            nearby_dice = [m for m in context_messages 
                          if m.get('sender') == player_id and m.get('dice_count', 0) > 0]
            
            if len(nearby_dice) >= 3:  # 连续投掷模式
                confidence += 0.1
        
        # 5. 时间间隔检查
        if index > 0:
            prev_msg = all_messages[index - 1]
            time_gap = (msg['timestamp'] - prev_msg['timestamp']) / 1000
            
            if 1 <= time_gap <= 30:  # 合理的时间间隔
                confidence += 0.05
            elif time_gap > 300:  # 时间间隔过长
                confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _convert_to_filtered_message(self, msg: Dict, confidence: float) -> FilteredDiceMessage:
        """转换为过滤后的消息格式"""
        return FilteredDiceMessage(
            seq=msg['seq'],
            timestamp=msg['timestamp'],
            datetime=msg['datetime'],
            player_id=msg['sender'],
            player_name=msg['sender_name'],
            dice_values=msg['dice_values'],
            dice_count=msg['dice_count'],
            msg_type=msg['msg_type'],
            content=msg['content'],
            md5_value=msg['md5_value'],
            content_value=msg['content_value'],
            confidence_score=confidence
        )
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/contact", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_filter_stats(self, filtered_messages: List[FilteredDiceMessage]) -> Dict[str, Any]:
        """获取过滤统计信息"""
        if not filtered_messages:
            return {'total': 0}
        
        confidences = [msg.confidence_score for msg in filtered_messages]
        player_counts = defaultdict(int)
        
        for msg in filtered_messages:
            player_counts[msg.player_id] += 1
        
        return {
            'total_messages': len(filtered_messages),
            'avg_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'high_confidence_count': sum(1 for c in confidences if c >= 0.8),
            'player_distribution': dict(player_counts),
            'dice_count_distribution': {
                '1': sum(1 for msg in filtered_messages if msg.dice_count == 1),
                '5': sum(1 for msg in filtered_messages if msg.dice_count == 5),
                'other': sum(1 for msg in filtered_messages if msg.dice_count not in [1, 5])
            }
        }