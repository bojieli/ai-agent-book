"""
独立的 Python 参考实现：直接在种子数据（内存 list）上计算 10 个问题的期望答案。

这些函数刻意「不走 SQL」，用来校验 Agent 生成 SQL 的执行结果是否正确。
每个函数返回 list[tuple]，元组内的列顺序与 questions.py 里给 Agent 的
「列顺序提示」保持一致，便于逐行比对。
"""

from datetime import date
from statistics import mean

DEPT_A = "研发部"   # 题目里的「A 部门」
DEPT_B = "销售部"   # 题目里的「B 部门」


def _end_date(e, today):
    return e["leave_date"] if e["leave_date"] else today


def _ym(d: date):
    return (d.year, d.month)


def _latest_salary(emp_id, salaries):
    recs = [s for s in salaries if s["emp_id"] == emp_id]
    if not recs:
        return None
    return max(recs, key=lambda s: s["pay_date"])["salary"]


def q1_avg_tenure_days(emps, sals, today):
    days = [(_end_date(e, today) - e["hire_date"]).days for e in emps]
    return [(round(mean(days), 2),)]


def q2_active_by_dept(emps, sals, today):
    counts = {}
    for e in emps:
        if e["leave_date"] is None:
            counts[e["department"]] = counts.get(e["department"], 0) + 1
    return [(d, c) for d, c in counts.items()]


def q3_dept_highest_avg_level(emps, sals, today):
    by_dept = {}
    for e in emps:
        by_dept.setdefault(e["department"], []).append(e["level"])
    top = max(by_dept.items(), key=lambda kv: mean(kv[1]))
    return [(top[0],)]  # 只返回部门名称


def q4_hires_this_and_last_year(emps, sals, today):
    y = today.year
    agg = {}
    for e in emps:
        hy = e["hire_date"].year
        if hy not in (y, y - 1):
            continue
        ty, ly = agg.get(e["department"], (0, 0))
        if hy == y:
            ty += 1
        else:
            ly += 1
        agg[e["department"]] = (ty, ly)
    return [(d, ty, ly) for d, (ty, ly) in agg.items()]


def q5_deptA_avg_salary_range(emps, sals, today):
    y = today.year
    lo, hi = (y - 2, 3), (y - 1, 5)  # 前年3月 ~ 去年5月（含端点）
    dept = {e["emp_id"] for e in emps if e["department"] == DEPT_A}
    vals = [s["salary"] for s in sals
            if s["emp_id"] in dept and lo <= _ym(s["pay_date"]) <= hi]
    return [(round(mean(vals), 2),)]


def q6_deptAB_avg_salary_last_year(emps, sals, today):
    y = today.year - 1
    out = []
    for dept in (DEPT_A, DEPT_B):
        ids = {e["emp_id"] for e in emps if e["department"] == dept}
        vals = [s["salary"] for s in sals
                if s["emp_id"] in ids and s["pay_date"].year == y]
        out.append((dept, round(mean(vals), 2)))
    return out


def q7_avg_salary_by_level_this_year(emps, sals, today):
    y = today.year
    lvl = {e["emp_id"]: e["level"] for e in emps}
    by_level = {}
    for s in sals:
        if s["pay_date"].year == y:
            by_level.setdefault(lvl[s["emp_id"]], []).append(s["salary"])
    return [(l, round(mean(v), 2)) for l, v in by_level.items()]


def q8_avg_latest_salary_by_tenure(emps, sals, today):
    buckets = {"入职一年内": [], "一到两年": [], "两到三年": []}
    for e in emps:
        days = (today - e["hire_date"]).days
        if days < 365:
            b = "入职一年内"
        elif days < 730:
            b = "一到两年"
        elif days < 1095:
            b = "两到三年"
        else:
            continue
        last = _latest_salary(e["emp_id"], sals)
        if last is not None:
            buckets[b].append(last)
    return [(b, round(mean(v), 2)) for b, v in buckets.items() if v]


def q9_top10_raise(emps, sals, today):
    y = today.year
    name = {e["emp_id"]: e["name"] for e in emps}
    this_year, last_year = {}, {}
    for s in sals:
        if s["pay_date"].year == y:
            this_year.setdefault(s["emp_id"], []).append(s["salary"])
        elif s["pay_date"].year == y - 1:
            last_year.setdefault(s["emp_id"], []).append(s["salary"])
    rows = []
    for eid in set(this_year) & set(last_year):
        raise_amt = mean(this_year[eid]) - mean(last_year[eid])
        rows.append((name[eid], round(raise_amt, 2)))
    rows.sort(key=lambda r: r[1], reverse=True)
    return rows[:10]


def q10_owed_salary(emps, sals, today):
    cur = (today.year, today.month)
    by_emp = {}
    for s in sals:
        by_emp.setdefault(s["emp_id"], set()).add(_ym(s["pay_date"]))
    out = []
    for e in emps:
        start = _ym(e["hire_date"])
        end = _ym(e["leave_date"]) if e["leave_date"] else cur
        paid = by_emp.get(e["emp_id"], set())
        y, m = start
        while (y, m) <= end:
            if (y, m) not in paid:
                out.append((e["emp_id"], f"{y:04d}-{m:02d}"))
            m += 1
            if m == 13:
                y, m = y + 1, 1
    return out


# 题号 -> 参考实现
REFERENCE = {
    1: q1_avg_tenure_days,
    2: q2_active_by_dept,
    3: q3_dept_highest_avg_level,
    4: q4_hires_this_and_last_year,
    5: q5_deptA_avg_salary_range,
    6: q6_deptAB_avg_salary_last_year,
    7: q7_avg_salary_by_level_this_year,
    8: q8_avg_latest_salary_by_tenure,
    9: q9_top10_raise,
    10: q10_owed_salary,
}
