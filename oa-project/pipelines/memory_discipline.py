from oa import Pipeline, Metric
from pathlib import Path
from datetime import datetime

class MemoryDiscipline(Pipeline):
    """虾老板记忆纪律检测"""
    goal_id = "team_health"
    
    def collect(self, date: str) -> list[Metric]:
        # 读取 memory 目录
        memory_dir = Path("/home/terrence/.openclaw/workspace/memory")
        
        # 检查今日记忆文件
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = memory_dir / f"{today}.md"
        
        # 检查记忆保存文件 (每 3 小时)
        preservation_count = 0
        for f in memory_dir.glob(f"{today}-*memory-preservation.md"):
            preservation_count += 1
        
        # 检查其他记忆文件 (日记、学习笔记等)
        other_memory_count = 0
        for f in memory_dir.glob(f"日记-{today}-*.md"):
            other_memory_count += 1
        for f in memory_dir.glob(f"learning-{today}.md"):
            other_memory_count += 1
        for f in memory_dir.glob(f"world-{today}.md"):
            other_memory_count += 1
        
        # 计算记忆纪律分数
        # 预期：每 3 小时 1 次保存 = 8 次/天
        expected_preservations = 8
        preservation_rate = (preservation_count / expected_preservations * 100) if expected_preservations > 0 else 0
        
        # 今日记忆文件存在 +10 分
        today_file_bonus = 10 if today_file.exists() else 0
        
        # 其他记忆文件 (日记/学习/新闻) 每个 +5 分，上限 30 分
        other_bonus = min(other_memory_count * 5, 30)
        
        # 总分 = 保存率 (60 分) + 今日文件 (10 分) + 其他记忆 (30 分)
        total_score = (preservation_rate * 0.6) + today_file_bonus + other_bonus
        
        return [
            Metric("memory_discipline", round(total_score, 1), unit="%"),
            Metric("preservation_count", preservation_count, unit="count"),
            Metric("other_memory_count", other_memory_count, unit="count"),
        ]
