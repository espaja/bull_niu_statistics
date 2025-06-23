#!/usr/bin/env python3
"""
Universal Niu Niu Data Analyzer
Supports any time period: daily/weekly/monthly/quarterly/half-yearly/yearly/custom
"""
import json
import csv
import sys
import argparse
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
sys.path.append('src')
from niu_niu_engine import NiuNiuEngine
from optimized_chatlog_importer import OptimizedChatlogImporter

def calculate_score_points(result_type, result_value):
    """Score system: Baozi=5, NiuNiu=3, Niu7/8/9=2, NoNiu=0, Others=1"""
    if result_type == "豹子":
        return 5
    elif result_type == "牛牛":
        return 3
    elif result_type in ["牛7", "牛8", "牛9"]:
        return 2
    elif result_type == "没牛":
        return 0
    else:
        return 1

def parse_time_range(time_param):
    """Parse time parameter: 2025-06-23(day), 2025-06(month), 2025-Q2(quarter), 2025-H1(half), 2025(year), custom range"""
    if ',' in time_param:
        start_date, end_date = time_param.split(',')
        return 'custom', start_date.strip(), end_date.strip()
    
    if len(time_param) == 4:
        return 'year', time_param, time_param
    
    if len(time_param) == 7:
        return 'month', time_param, time_param
    
    if len(time_param) == 10:
        return 'day', time_param, time_param
    
    if 'Q' in time_param:
        year, quarter = time_param.split('-Q')
        return 'quarter', time_param, time_param
    
    if 'H' in time_param:
        year, half = time_param.split('-H')
        return 'half', time_param, time_param
    
    raise ValueError(f"Unsupported time format: {time_param}")

def get_filename_suffix(time_type, time_param):
    """Generate filename suffix"""
    if time_type == 'day':
        return time_param.replace('-', '_')
    elif time_type == 'month':
        return time_param.replace('-', '_')
    elif time_type == 'year':
        return time_param
    elif time_type == 'quarter':
        return time_param.replace('-', '_')
    elif time_type == 'half':
        return time_param.replace('-', '_')
    elif time_type == 'custom':
        start, end = time_param.split(',')
        return f"{start.strip().replace('-', '_')}_to_{end.strip().replace('-', '_')}"
    else:
        return time_param.replace('-', '_').replace(',', '_to_')

def universal_niu_niu_analyzer():
    parser = argparse.ArgumentParser(description="Universal Niu Niu Data Analyzer")
    parser.add_argument("--time", required=True, help="Time range (2025-06-23, 2025-06, 2025-Q2, 2025-H1, 2025, 2025-06-01,2025-06-30)")
    parser.add_argument("--group", default="21998085218@chatroom", help="Group chat ID")
    parser.add_argument("--api-ip", default="127.0.0.1", help="Chatlog API IP address")
    parser.add_argument("--mode", choices=['fetch', 'analyze', 'all'], default='all', help="Mode: fetch=data only, analyze=analysis only, all=both")
    
    args = parser.parse_args()
    
    time_type, start_time, end_time = parse_time_range(args.time)
    file_suffix = get_filename_suffix(time_type, args.time)
    
    print(f'🎯 Universal Niu Niu Data Analyzer')
    print(f'📅 Time: {args.time} ({time_type})')
    print(f'👥 Group: {args.group}')
    print(f'🌐 API: {args.api_ip}:5030')
    print('=' * 80)
    
    # File definitions
    raw_filename = f'raw_messages_{file_suffix}.json'
    dice_filename = f'dice_data_{file_suffix}.csv'
    games_filename = f'games_{file_suffix}.csv'
    battles_filename = f'battles_{file_suffix}.csv'
    stats_filename = f'stats_{file_suffix}.csv'
    
    # 1. Data fetching
    if args.mode in ['fetch', 'all']:
        print(f'📡 Fetching data...')
        
        api_url = f"http://{args.api_ip}:5030"
        importer = OptimizedChatlogImporter(api_base_url=api_url)
        all_messages = importer._fetch_raw_messages_optimized(args.group, args.time)
        
        if not all_messages:
            print("❌ No messages found")
            return
        
        with open(raw_filename, 'w', encoding='utf-8') as f:
            json.dump(all_messages, f, ensure_ascii=False, indent=2)
        
        print(f'📁 Raw data saved: {raw_filename} ({len(all_messages)} messages)')
    
    # 2. Data analysis
    if args.mode in ['analyze', 'all']:
        print(f'🔍 Analyzing data...')
        
        try:
            with open(raw_filename, 'r', encoding='utf-8') as f:
                all_messages = json.load(f)
        except FileNotFoundError:
            print(f"❌ Raw data not found: {raw_filename}")
            print(f"Run with: --mode fetch")
            return
        
        print(f'📖 Processing {len(all_messages)} messages')
        
        niu_niu_engine = NiuNiuEngine()
        importer = OptimizedChatlogImporter()
        content_to_dice_map = {'4': 1, '5': 2, '6': 3, '7': 4, '8': 5, '9': 6}
        
        # 提取骰子数据
        dice_records = []
        for msg in all_messages:
            if msg.get('msg_type') == 47:
                content = msg.get('content', '')
                if 'gameext' in content and 'type="2"' in content:
                    # 提取content值
                    pattern = r'<gameext[^>]*type="2"[^>]*content="([^"]*)"[^>]*></gameext>'
                    matches = re.findall(pattern, content)
                    
                    if matches:
                        content_value = matches[0]
                        dice_value = content_to_dice_map.get(content_value)
                        
                        if dice_value:
                            # 解析时间
                            time_str = msg.get('time', '')
                            try:
                                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                                date_only = dt.strftime('%Y-%m-%d')
                                time_only = dt.strftime('%H:%M:%S')
                                timestamp = int(dt.timestamp())
                            except:
                                date_only = ''
                                time_only = time_str
                                timestamp = 0
                            
                            dice_records.append({
                                'seq': msg.get('seq', 0),
                                'date': date_only,
                                'time': time_only,
                                'timestamp': timestamp,
                                'player_name': msg.get('sender_name', '未知'),
                                'content_value': content_value,
                                'dice_value': dice_value
                            })
        
        # 保存骰子数据
        with open(dice_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['seq', 'date', 'time', 'timestamp', 'player_name', 'content_value', 'dice_value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in dice_records:
                writer.writerow(record)
        
        print(f'🎲 骰子数据: {len(dice_records)}条 → {dice_filename}')
        
        # 组合有效游戏
        def group_dice_to_games(records):
            player_dice = defaultdict(list)
            for record in records:
                player_dice[record['player_name']].append(record)
            
            valid_games = []
            for player, dice_list in player_dice.items():
                dice_list.sort(key=lambda x: x['seq'])
                
                i = 0
                while i + 4 < len(dice_list):
                    time_gap = dice_list[i + 4]['timestamp'] - dice_list[i]['timestamp']
                    if time_gap <= 30:  # 30秒内
                        dice_values = [dice_list[j]['dice_value'] for j in range(i, i + 5)]
                        result = niu_niu_engine.calculate_result(dice_values)
                        
                        valid_games.append({
                            'player_name': player,
                            'date': dice_list[i]['date'],
                            'start_time': dice_list[i]['time'],
                            'end_time': dice_list[i + 4]['time'],
                            'dice_values': dice_values,
                            'result_type': result.type,
                            'result_value': result.value,
                            'score_points': calculate_score_points(result.type, result.value)
                        })
                        i += 5
                    else:
                        i += 1
            
            return valid_games
        
        valid_games = group_dice_to_games(dice_records)
        valid_games.sort(key=lambda x: x['start_time'])
        
        # 保存游戏数据
        with open(games_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['player_name', 'date', 'start_time', 'dice_values', 'result_type', 'result_value', 'score_points']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for game in valid_games:
                writer.writerow({
                    'player_name': game['player_name'],
                    'date': game['date'],
                    'start_time': game['start_time'],
                    'dice_values': ','.join(map(str, game['dice_values'])),
                    'result_type': game['result_type'],
                    'result_value': game['result_value'],
                    'score_points': game['score_points']
                })
        
        print(f'🎮 有效游戏: {len(valid_games)}局 → {games_filename}')
        
        # 分析对战
        battles = []
        for i in range(len(valid_games) - 1):
            current = valid_games[i]
            next_game = valid_games[i + 1]
            
            if current['player_name'] != next_game['player_name']:
                # 简单时间差计算
                def time_to_seconds(time_str):
                    try:
                        h, m, s = map(int, time_str.split(':'))
                        return h * 3600 + m * 60 + s
                    except:
                        return 0
                
                time_gap = time_to_seconds(next_game['start_time']) - time_to_seconds(current['start_time'])
                
                if 0 <= time_gap <= 300:  # 5分钟内
                    winner = 'draw'
                    if current['score_points'] > next_game['score_points']:
                        winner = current['player_name']
                    elif next_game['score_points'] > current['score_points']:
                        winner = next_game['player_name']
                    
                    battles.append({
                        'player1': current['player_name'],
                        'player2': next_game['player_name'],
                        'player1_result': current['result_type'],
                        'player2_result': next_game['result_type'],
                        'player1_points': current['score_points'],
                        'player2_points': next_game['score_points'],
                        'winner': winner,
                        'date': current['date']
                    })
        
        # 保存对战数据
        with open(battles_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['player1', 'player2', 'player1_result', 'player2_result', 'player1_points', 'player2_points', 'winner', 'date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for battle in battles:
                writer.writerow(battle)
        
        print(f'⚔️  对战记录: {len(battles)}轮 → {battles_filename}')
        
        # 3. 生成统计报告
        print(f'\n📊 生成统计报告...')
        
        player_stats = defaultdict(lambda: {
            'total_games': 0, 'total_points': 0, 'avg_points': 0,
            'battles_won': 0, 'battles_lost': 0, 'battles_draw': 0,
            'win_rate': 0, 'result_counts': Counter()
        })
        
        # 游戏统计
        for game in valid_games:
            player = game['player_name']
            player_stats[player]['total_games'] += 1
            player_stats[player]['total_points'] += game['score_points']
            player_stats[player]['result_counts'][game['result_type']] += 1
        
        # 对战统计
        for battle in battles:
            p1, p2 = battle['player1'], battle['player2']
            winner = battle['winner']
            
            if winner == p1:
                player_stats[p1]['battles_won'] += 1
                player_stats[p2]['battles_lost'] += 1
            elif winner == p2:
                player_stats[p2]['battles_won'] += 1
                player_stats[p1]['battles_lost'] += 1
            else:
                player_stats[p1]['battles_draw'] += 1
                player_stats[p2]['battles_draw'] += 1
        
        # 计算统计值
        for player, stats in player_stats.items():
            if stats['total_games'] > 0:
                stats['avg_points'] = stats['total_points'] / stats['total_games']
            
            total_decisive = stats['battles_won'] + stats['battles_lost']
            if total_decisive > 0:
                stats['win_rate'] = stats['battles_won'] / total_decisive * 100
        
        # 保存统计数据
        with open(stats_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['player_name', 'total_games', 'avg_points', 'win_rate', 'battles_won', 'battles_lost', 
                         'niu_niu_count', 'baozi_count', 'no_niu_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # 按平均得分排序
            sorted_players = sorted(player_stats.items(), key=lambda x: x[1]['avg_points'], reverse=True)
            
            for player, stats in sorted_players:
                writer.writerow({
                    'player_name': player,
                    'total_games': stats['total_games'],
                    'avg_points': round(stats['avg_points'], 2),
                    'win_rate': round(stats['win_rate'], 1),
                    'battles_won': stats['battles_won'],
                    'battles_lost': stats['battles_lost'],
                    'niu_niu_count': stats['result_counts']['牛牛'],
                    'baozi_count': stats['result_counts']['豹子'],
                    'no_niu_count': stats['result_counts']['没牛']
                })
        
        print(f'📈 统计报告: {stats_filename}')
        
        # 4. 详细控制台报告
        print(f'\n🏆 {args.time} 牛牛游戏详细统计报告')
        print('=' * 80)
        
        # 基础数据概览
        print(f'📊 数据概览:')
        print(f'  总消息数: {len(all_messages)}')
        print(f'  骰子投掷: {len(dice_records)}次')
        print(f'  有效游戏: {len(valid_games)}局')
        print(f'  对战轮次: {len(battles)}轮')
        
        if not sorted_players:
            print('\n❌ 没有找到有效的游戏数据')
            return
        
        # 各种排行榜
        print(f'\n🏆 排行榜统计:')
        print('=' * 50)
        
        # 胜率最高（至少5场对战）
        qualified = [(p, s) for p, s in sorted_players if s['battles_won'] + s['battles_lost'] >= 5]
        if qualified:
            highest_wr = max(qualified, key=lambda x: x[1]['win_rate'])
            lowest_wr = min(qualified, key=lambda x: x[1]['win_rate'])
            print(f'🥇 胜率最高: {highest_wr[0]}')
            print(f'   胜率: {highest_wr[1]["win_rate"]:.1f}%')
            print(f'   战绩: {highest_wr[1]["battles_won"]}胜{highest_wr[1]["battles_lost"]}负{highest_wr[1]["battles_draw"]}平')
            
            print(f'🔻 胜率最低: {lowest_wr[0]}')
            print(f'   胜率: {lowest_wr[1]["win_rate"]:.1f}%')
            print(f'   战绩: {lowest_wr[1]["battles_won"]}胜{lowest_wr[1]["battles_lost"]}负{lowest_wr[1]["battles_draw"]}平')
        
        # 牛牛最多
        niu_niu_ranking = sorted(sorted_players, key=lambda x: x[1]['result_counts']['牛牛'], reverse=True)
        if niu_niu_ranking[0][1]['result_counts']['牛牛'] > 0:
            print(f'\n🎯 牛牛排行榜:')
            for i, (player, stats) in enumerate(niu_niu_ranking[:3]):
                count = stats['result_counts']['牛牛']
                if count > 0:
                    print(f'  {i+1}. {player}: {count}次牛牛')
        
        # 豹子统计
        baozi_ranking = sorted(sorted_players, key=lambda x: x[1]['result_counts']['豹子'], reverse=True)
        if baozi_ranking[0][1]['result_counts']['豹子'] > 0:
            print(f'\n💎 豹子统计:')
            for player, stats in baozi_ranking:
                count = stats['result_counts']['豹子']
                if count > 0:
                    print(f'  {player}: {count}次豹子')
        
        # 平均得分排行
        avg_qualified = [(p, s) for p, s in sorted_players if s['total_games'] >= 10]
        if avg_qualified:
            print(f'\n📊 平均得分最高: {avg_qualified[0][0]} ({avg_qualified[0][1]["avg_points"]:.2f}分)')
            print(f'   总游戏数: {avg_qualified[0][1]["total_games"]}局')
        
        # 详细玩家统计表
        print(f'\n📋 详细玩家统计表:')
        print('=' * 100)
        print(f'{"玩家":12} {"游戏数":>6} {"平均分":>7} {"胜率":>6} {"牛牛":>4} {"豹子":>4} {"没牛":>4} {"最佳成绩":10}')
        print('-' * 100)
        
        for player, stats in sorted_players:
            wr_str = f"{stats['win_rate']:.1f}%" if stats['battles_won'] + stats['battles_lost'] > 0 else "N/A"
            niu_niu_count = stats['result_counts']['牛牛']
            baozi_count = stats['result_counts']['豹子']
            no_niu_count = stats['result_counts']['没牛']
            
            # 找最佳成绩
            best_result = "没牛"
            for result_type in ["豹子", "牛牛", "牛9", "牛8", "牛7", "牛6", "牛5", "牛3", "牛2", "牛1"]:
                if stats['result_counts'][result_type] > 0:
                    best_result = result_type
                    break
            
            print(f'{player:12} {stats["total_games"]:6d} {stats["avg_points"]:7.2f} {wr_str:6} '
                  f'{niu_niu_count:4d} {baozi_count:4d} {no_niu_count:4d} {best_result:10}')
        
        # 结果分布统计
        print(f'\n✨ 结果分布统计:')
        print('=' * 40)
        
        all_results = Counter()
        for game in valid_games:
            all_results[game['result_type']] += 1
        
        total_games = len(valid_games)
        print(f'📊 各种结果出现次数:')
        for result_type in ['豹子', '牛牛', '牛9', '牛8', '牛7', '牛6', '牛5', '牛3', '牛2', '牛1', '没牛']:
            if result_type in all_results:
                count = all_results[result_type]
                percentage = count / total_games * 100
                print(f'  {result_type:4}: {count:3d}次 ({percentage:4.1f}%)')
        
        # 最激烈的对战组合
        print(f'\n⚔️  最激烈的对战组合:')
        battle_pairs = defaultdict(int)
        battle_results = defaultdict(lambda: {'p1_wins': 0, 'p2_wins': 0, 'draws': 0})
        
        for battle in battles:
            p1, p2 = battle['player1'], battle['player2']
            key = f"{min(p1, p2)} vs {max(p1, p2)}"
            battle_pairs[key] += 1
            
            winner = battle['winner']
            if winner == p1:
                battle_results[key]['p1_wins'] += 1
            elif winner == p2:
                battle_results[key]['p2_wins'] += 1
            else:
                battle_results[key]['draws'] += 1
        
        top_pairs = sorted(battle_pairs.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (pair, count) in enumerate(top_pairs):
            results = battle_results[pair]
            print(f'  {i+1}. {pair}: {count}轮对战 ({results["p1_wins"]}-{results["p2_wins"]}-{results["draws"]})')
        
        # 按日期统计（如果跨越多天）
        daily_stats = defaultdict(int)
        for game in valid_games:
            if game['date']:
                daily_stats[game['date']] += 1
        
        if len(daily_stats) > 1:
            print(f'\n📅 每日游戏数量:')
            for date in sorted(daily_stats.keys()):
                print(f'  {date}: {daily_stats[date]}局')
        
        # 活跃度统计
        print(f'\n👥 玩家活跃度排行:')
        activity_ranking = sorted(sorted_players, key=lambda x: x[1]['total_games'], reverse=True)
        for i, (player, stats) in enumerate(activity_ranking):
            print(f'  {i+1}. {player}: {stats["total_games"]}局游戏')
        
        print(f'\n✅ 详细分析完成！所有数据文件已生成：')
        print(f'  📁 {dice_filename} - 骰子数据')
        print(f'  📁 {games_filename} - 游戏记录')
        print(f'  📁 {battles_filename} - 对战详情')
        print(f'  📁 {stats_filename} - 统计汇总')

if __name__ == "__main__":
    universal_niu_niu_analyzer()