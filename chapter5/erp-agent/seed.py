"""
生成可复现的 ERP 种子数据（员工表 + 工资表）。

设计要点（保证 10 个问题都有确定答案）：
- 约 40 名员工，跨 5 个部门、多个级别；
- 工龄刻意覆盖「入职一年内 / 一到两年 / 两到三年 / 三年以上」四档（供问题 8）；
- 若干已离职员工（leave_date 非空，供问题 2/6 等）；
- 工资按「入职当年基准 + 每年固定涨薪额」逐月生成，
  每位员工的年度涨薪额互不相同，从而问题 9「涨薪最大 10 人」排名唯一；
- 刻意为一名在职员工删掉某个月的工资记录（供问题 10「拖欠工资」）；
- 所有日期以「今天」为基准相对生成，固定随机种子 42，可复现。

reference.py 直接在这些内存结构上计算期望答案，
与 Agent 生成 SQL 的执行结果比对，保证语义一致。
"""

import random
from datetime import date, timedelta

# ---- 业务常量 ----
DEPARTMENTS = ["研发部", "销售部", "市场部", "财务部", "人力资源部"]
# 各部门基准工资
DEPT_BASE = {"研发部": 15000, "销售部": 12000, "市场部": 11000, "财务部": 12000, "人力资源部": 10000}

_SURNAMES = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜")
_GIVEN = list("伟芳娜秀英敏静丽强磊军洋勇艳杰娟涛明超霞平刚桂香建华志强晓东春梅国栋雪松")


def _first_of_month(d: date) -> date:
    return date(d.year, d.month, 1)


def _add_month(d: date) -> date:
    """返回下个月的 1 号（d 需为某月 1 号）。"""
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def _month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def generate(today: date | None = None):
    """生成并返回 (employees, salaries) 两个 list[dict]。"""
    if today is None:
        today = date.today()
    rng = random.Random(42)

    cur_month = _first_of_month(today)

    # 工龄分档（相对今天的天数区间），保证问题 8 各档都有人
    # bucket: (人数, 最小天数, 最大天数)
    tenure_plan = [
        (8, 30, 360),      # 入职一年内
        (8, 370, 720),     # 一到两年
        (8, 740, 1080),    # 两到三年
        (16, 1100, 1900),  # 三年以上
    ]

    employees = []
    emp_id = 0
    for count, dmin, dmax in tenure_plan:
        for _ in range(count):
            emp_id += 1
            days = rng.randint(dmin, dmax)
            hire_date = today - timedelta(days=days)
            dept = rng.choice(DEPARTMENTS)
            level = rng.randint(3, 9)
            name = rng.choice(_SURNAMES) + rng.choice(_GIVEN)
            employees.append({
                "emp_id": emp_id,
                "name": name,
                "department": dept,
                "level": level,
                "hire_date": hire_date,
                "leave_date": None,  # 先全部在职，稍后挑一部分离职
            })

    # 挑选约 6 名「三年以上」员工设为离职，离职日期落在过去 ~2 年内
    senior = [e for e in employees if (today - e["hire_date"]).days > 1100]
    for e in rng.sample(senior, 6):
        # 离职日期 = 今天前 60~700 天，且晚于入职至少 200 天
        leave = today - timedelta(days=rng.randint(60, 700))
        if (leave - e["hire_date"]).days < 200:
            leave = e["hire_date"] + timedelta(days=200)
        # 落到月末，便于按月发薪对齐
        e["leave_date"] = leave

    # 为每位员工设定「入职当年基准工资」与「每年固定涨薪额」（互不相同）
    for e in employees:
        e["_start_base"] = (
            DEPT_BASE[e["department"]] + e["level"] * 2000 + (e["emp_id"] % 7) * 300
        )
        # 涨薪额随 emp_id 严格递增，保证问题 9 排名唯一（无并列）
        e["_annual_raise"] = 400 + e["emp_id"] * 45

    # 指定一名在职、工龄较长的员工为「明显涨薪王」（问题 9 榜首）
    big_raiser = next(
        e for e in employees
        if e["leave_date"] is None and (today - e["hire_date"]).days > 700
    )
    big_raiser["_annual_raise"] = 12000  # 远高于其他人
    big_raiser["_is_big_raiser"] = True

    # ---- 逐月生成工资 ----
    salaries = []
    for e in employees:
        hire_m = _first_of_month(e["hire_date"])
        end_m = _first_of_month(e["leave_date"]) if e["leave_date"] else cur_month
        m = hire_m
        while m <= end_m:
            salary = e["_start_base"] + e["_annual_raise"] * (m.year - e["hire_date"].year)
            salaries.append({
                "emp_id": e["emp_id"],
                "pay_date": m,          # 每月 1 号代表当月发薪
                "salary": int(salary),
            })
            m = _add_month(m)

    # ---- 刻意制造一条「拖欠工资」：某在职员工某个过去月份缺发薪（问题 10）----
    target = next(
        e for e in employees
        if e["leave_date"] is None and (today - e["hire_date"]).days > 800
    )
    # 删除「6 个月前」那条记录（确保它存在且不是当月）
    missing_month = cur_month
    for _ in range(6):
        # 往前推 6 个月
        y, mo = missing_month.year, missing_month.month - 1
        if mo == 0:
            y, mo = y - 1, 12
        missing_month = date(y, mo, 1)
    before = len(salaries)
    salaries = [
        s for s in salaries
        if not (s["emp_id"] == target["emp_id"] and s["pay_date"] == missing_month)
    ]
    assert len(salaries) == before - 1, "未能删除目标发薪记录，请检查种子逻辑"
    target["_owed_month"] = _month_key(missing_month)

    return employees, salaries


def create_db(conn, employees, salaries):
    """在给定 sqlite 连接上建表并灌入数据。"""
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS salaries;
        CREATE TABLE employees (
            emp_id      INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL,
            department  TEXT    NOT NULL,
            level       INTEGER NOT NULL,   -- 级别，数字越大越高
            hire_date   TEXT    NOT NULL,   -- 入职日期 YYYY-MM-DD
            leave_date  TEXT               -- 离职日期，NULL = 在职
        );
        CREATE TABLE salaries (
            emp_id      INTEGER NOT NULL,   -- 关联 employees.emp_id
            pay_date    TEXT    NOT NULL,   -- 发薪日期 YYYY-MM-01（每月一条）
            salary      INTEGER NOT NULL,   -- 当月工资
            PRIMARY KEY (emp_id, pay_date)
        );
        """
    )
    cur.executemany(
        "INSERT INTO employees VALUES (?,?,?,?,?,?)",
        [
            (
                e["emp_id"], e["name"], e["department"], e["level"],
                e["hire_date"].isoformat(),
                e["leave_date"].isoformat() if e["leave_date"] else None,
            )
            for e in employees
        ],
    )
    cur.executemany(
        "INSERT INTO salaries VALUES (?,?,?)",
        [(s["emp_id"], s["pay_date"].isoformat(), s["salary"]) for s in salaries],
    )
    conn.commit()
