import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("drama-script-manager")

DATA_FILE = Path("drama_data.json")


def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"characters": {}, "episodes": {}}


def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@mcp.tool()
def save_character(name: str, appearance: str, personality: str, prompt: str = "") -> str:
    """保存或更新一个角色设定。prompt 是用于视频生成的固定角色提示词，保证角色形象一致。"""
    data = load_data()
    data["characters"][name] = {
        "appearance": appearance,
        "personality": personality,
        "prompt": prompt,
    }
    save_data(data)
    return f"角色「{name}」已保存。"


@mcp.tool()
def save_shot(episode: int, shot_number: int, visual: str, dialogue: str = "", duration_seconds: int = 5) -> str:
    """保存或更新某一集的一个分镜。visual 是画面描述，dialogue 是台词。"""
    data = load_data()
    ep_key = str(episode)
    shots = data["episodes"].setdefault(ep_key, {})
    shots[str(shot_number)] = {
        "visual": visual,
        "dialogue": dialogue,
        "duration_seconds": duration_seconds,
    }
    save_data(data)
    return f"第{episode}集 第{shot_number}镜 已保存。"


@mcp.tool()
def get_episode(episode: int) -> str:
    """查看某一集的全部内容：所有角色设定加按顺序排列的分镜。"""
    data = load_data()
    shots = data["episodes"].get(str(episode), {})
    ordered = {k: shots[k] for k in sorted(shots, key=int)}
    result = {
        "episode": episode,
        "characters": data["characters"],
        "shots": ordered,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http")
