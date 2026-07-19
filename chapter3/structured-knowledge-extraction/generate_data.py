"""
合成一个小样本、多罪名的刑事判例数据集。

CAIL2018（真实目标数据集）体量太大（数百万条），不便随仓库分发；本实验自带一个
可离线运行的小样本，覆盖三类罪名：盗窃罪、故意伤害罪、诈骗罪。

每条案例包含：
  - `charge`  罪名（生成时已知，仅作参考；抽取阶段会由 LLM 自行判定）；
  - `fact`    一段自然语言判决书事实描述；
  - `gold`    生成时使用的因子真值（仅供人工核对，抽取不依赖它）；
  - `label_months` 刑期（月），由一个「已知」的量刑公式加噪声生成。

关键点：**因子在生成时被"写进"案情文本，发现阶段再从文本里把它们"读"回来**。
生成用的字段名（英文 key）只服务于本文件，下游的因子发现完全不依赖它——发现阶段
让 LLM 自由归纳因子，因此学到的模式来自数据本身，而非这里的先验字段列表。

真实迁移：把本文件替换为读取 CAIL2018 的 `data_*.json`（每行含 `fact` 与
`meta.term_of_imprisonment` 与 `meta.accusation`），产出同样结构的 `cases.jsonl` 即可。
"""
import json
import math
import os
import random

random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_PATH = os.path.join(DATA_DIR, "cases.jsonl")

NAMES = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹")
LOCATIONS = ["某小区", "某商场", "某写字楼", "某菜市场", "某手机专卖店", "某电动车棚", "某网吧"]


# ---------------------------------------------------------------------------
# 盗窃罪
# ---------------------------------------------------------------------------
def gen_theft(i: int) -> dict:
    amount = int(round(random.uniform(1500, 400000), -1))
    f = {
        "prior_record": random.random() < 0.5,
        "surrender": random.random() < 0.45,
        "restitution": random.random() < 0.5,
        "confession": random.random() < 0.6,
        "burglary": random.random() < 0.45,
        "carry_weapon": random.random() < 0.25,
        "gang": random.random() < 0.4,
    }
    m = -18 + 5.2 * math.log(amount)
    m += f["prior_record"] * 11 + f["burglary"] * 7 + f["carry_weapon"] * 5 + f["gang"] * 3
    m += -f["surrender"] * 9 - f["restitution"] * 6 - f["confession"] * 3
    m += random.gauss(0, 1.2)
    months = int(max(1, min(180, round(m))))

    name = "被告人" + random.choice(NAMES) + "某"
    prior = "曾因盗窃罪被判刑，刑满释放后再次作案，系累犯。" if f["prior_record"] else "此前无违法犯罪记录。"
    scene = f"翻窗入户进入被害人位于{random.choice(LOCATIONS)}的住宅内" if f["burglary"] else f"在{random.choice(LOCATIONS)}内"
    weapon = "，作案时随身携带匕首一把" if f["carry_weapon"] else ""
    gang = "伙同他人结伙" if f["gang"] else "单独"
    surrender = "案发后主动到公安机关投案自首，" if f["surrender"] else "后被公安机关抓获归案，"
    restitution = "已退赔全部赃款并取得谅解。" if f["restitution"] else "赃款已被挥霍，未退赔。"
    confession = "当庭认罪认罚。" if f["confession"] else "当庭对指控予以否认。"
    fact = (
        f"{name}，男。{prior}经审理查明：{name}{gang}{scene}{weapon}窃取他人财物，"
        f"经鉴定价值人民币{amount}元。{surrender}{restitution}{confession}"
    )
    return {"id": f"theft_{i:02d}", "charge": "盗窃罪", "fact": fact,
            "gold": {"amount": amount, **f}, "label_months": months}


# ---------------------------------------------------------------------------
# 故意伤害罪
# ---------------------------------------------------------------------------
_INJURY_BASE = {"轻微伤": 2.0, "轻伤": 12.0, "重伤": 40.0}


def gen_assault(i: int) -> dict:
    injury = random.choice(["轻微伤", "轻微伤", "轻伤", "轻伤", "重伤"])
    f = {
        "prior_record": random.random() < 0.35,
        "surrender": random.random() < 0.4,
        "restitution": random.random() < 0.55,  # 赔偿谅解在伤害案中权重很大
        "confession": random.random() < 0.6,
        "injury_level": injury,
        "armed": random.random() < 0.45,
        "premeditated": random.random() < 0.3,
        "gang": random.random() < 0.35,
    }
    m = _INJURY_BASE[injury]
    m += f["prior_record"] * 8 + f["armed"] * 10 + f["premeditated"] * 8 + f["gang"] * 4
    m += -f["surrender"] * 6 - f["restitution"] * 10 - f["confession"] * 3
    m += random.gauss(0, 1.0)
    months = int(max(1, min(180, round(m))))

    name = "被告人" + random.choice(NAMES) + "某"
    prior = "曾因寻衅滋事被判刑，系累犯。" if f["prior_record"] else "平时表现尚可，无前科。"
    plan = "因积怨已久、事先预谋，" if f["premeditated"] else "因琐事发生口角后，"
    gang = "纠集多人" if f["gang"] else "持"
    weapon = ("持械（砍刀）" if f["armed"] else "赤手空拳") if not f["gang"] else ("并持械" if f["armed"] else "")
    injury_desc = {"轻微伤": "经鉴定为轻微伤", "轻伤": "经鉴定为轻伤二级", "重伤": "经鉴定为重伤二级"}[injury]
    surrender = "案发后主动投案自首，" if f["surrender"] else "作案后逃离现场，后被抓获，"
    restitution = "已赔偿被害人损失并取得谅解。" if f["restitution"] else "未赔偿被害人损失。"
    confession = "当庭认罪认罚。" if f["confession"] else "当庭辩称系正当防卫。"
    fact = (
        f"{name}，男。{prior}经审理查明：{name}{plan}{gang}{weapon}殴打被害人，"
        f"致其{injury_desc}。{surrender}{restitution}{confession}"
    )
    return {"id": f"assault_{i:02d}", "charge": "故意伤害罪", "fact": fact,
            "gold": f, "label_months": months}


# ---------------------------------------------------------------------------
# 诈骗罪
# ---------------------------------------------------------------------------
def gen_fraud(i: int) -> dict:
    amount = int(round(random.uniform(8000, 800000), -1))
    scam = random.choice(["电信网络", "电信网络", "合同", "普通"])
    victims = random.randint(1, 40) if scam == "电信网络" else random.randint(1, 5)
    f = {
        "prior_record": random.random() < 0.35,
        "surrender": random.random() < 0.4,
        "restitution": random.random() < 0.45,
        "confession": random.random() < 0.6,
        "scam_type": scam,
        "victim_count": victims,
        "gang": random.random() < 0.5,
    }
    m = -22 + 6.0 * math.log(amount)
    m += f["prior_record"] * 10 + f["gang"] * 4
    m += {"电信网络": 8.0, "合同": 3.0, "普通": 0.0}[scam]
    m += math.log(victims + 1) * 3.0
    m += -f["surrender"] * 8 - f["restitution"] * 7 - f["confession"] * 3
    m += random.gauss(0, 1.2)
    months = int(max(1, min(180, round(m))))

    name = "被告人" + random.choice(NAMES) + "某"
    prior = "曾因诈骗被判刑，系累犯。" if f["prior_record"] else "此前无犯罪记录。"
    method = {
        "电信网络": f"通过拨打电话、发送短信等电信网络手段，虚构投资项目骗取{victims}名被害人",
        "合同": "在签订、履行合同过程中，以虚假身份和虚构履约能力骗取被害人",
        "普通": "以帮忙办事为由，虚构事实骗取被害人",
    }[scam]
    gang = "伙同他人组成团伙，" if f["gang"] else ""
    surrender = "案发后主动投案自首，" if f["surrender"] else "后被公安机关抓获，"
    restitution = "已退赔全部赃款。" if f["restitution"] else "赃款未追回。"
    confession = "当庭认罪认罚。" if f["confession"] else "当庭否认诈骗故意。"
    fact = (
        f"{name}，男。{prior}经审理查明：{name}{gang}{method}钱财，"
        f"骗取财物共计人民币{amount}元。{surrender}{restitution}{confession}"
    )
    return {"id": f"fraud_{i:02d}", "charge": "诈骗罪", "fact": fact,
            "gold": {"amount": amount, **f}, "label_months": months}


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    cases = []
    for i in range(1, 25):   # 24 盗窃
        cases.append(gen_theft(i))
    for i in range(1, 23):   # 22 故意伤害
        cases.append(gen_assault(i))
    for i in range(1, 21):   # 20 诈骗  -> 共 66 条
        cases.append(gen_fraud(i))
    random.shuffle(cases)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        for c in cases:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    months = [c["label_months"] for c in cases]
    print(f"已生成 {len(cases)} 条案例（盗窃/故意伤害/诈骗）-> {OUT_PATH}")
    print(f"刑期范围: {min(months)}~{max(months)} 个月，均值 {sum(months)/len(months):.1f}")


if __name__ == "__main__":
    main()
