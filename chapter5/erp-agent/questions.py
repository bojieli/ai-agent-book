"""
10 个自然语言问题，以及给 Agent 的「输出列」提示。

hint 里只补充「业务口径 + 期望返回哪些列、什么顺序」这类 schema 级提示，
不泄露具体数值答案。列顺序与 reference.py 的返回一致，便于逐行比对。
"""

QUESTIONS = [
    {
        "id": 1,
        "nl": "平均每个员工在职多久？",
        "hint": "在职时长按天计：离职员工用 leave_date，在职员工用今天 date('now')，"
                "对全部员工求平均。只返回一列：平均在职天数。",
    },
    {
        "id": 2,
        "nl": "每个部门有多少在职员工？",
        "hint": "在职指 leave_date 为空。返回两列：部门, 在职人数。",
    },
    {
        "id": 3,
        "nl": "哪个部门员工平均级别最高？",
        "hint": "按所有员工（含离职）的 level 求各部门平均，取最高的那个部门。"
                "只返回一列：部门名称。",
    },
    {
        "id": 4,
        "nl": "每个部门今年和去年各新入职多少人？",
        "hint": "按 hire_date 的年份统计。返回三列：部门, 今年入职人数, 去年入职人数；"
                "只保留今年或去年至少有一人入职的部门。",
    },
    {
        "id": 5,
        "nl": "前年3月到去年5月，A部门平均工资是多少？",
        "hint": "A部门=研发部；时间范围指发薪月份从『前年3月』到『去年5月』（含两端）。"
                "禁止硬编码年份，时间范围可写成："
                "strftime('%Y-%m',pay_date) BETWEEN "
                "strftime('%Y-%m','now','-2 years','start of year','+2 months') AND "
                "strftime('%Y-%m','now','-1 year','start of year','+4 months')。"
                "只返回一列：平均工资。",
    },
    {
        "id": 6,
        "nl": "去年A部门和B部门平均工资哪个高？",
        "hint": "A部门=研发部，B部门=销售部；只统计去年发薪记录"
                "（strftime('%Y',pay_date)=strftime('%Y','now','-1 year')）。"
                "统计部门内所有员工（含已离职），不要按 leave_date 过滤。"
                "返回两列：部门, 平均工资（两行，分别对应研发部和销售部）。",
    },
    {
        "id": 7,
        "nl": "今年每个级别的员工平均工资是多少？",
        "hint": "只统计今年发薪记录，按 level 分组。返回两列：级别, 平均工资。",
    },
    {
        "id": 8,
        "nl": "入职一年内、一到两年、两到三年的员工，最近一个月平均工资是多少？",
        "hint": "工龄按 date('now')-hire_date 的天数分档：<365 天为『入职一年内』，"
                "365~730 天为『一到两年』，730~1095 天为『两到三年』，三年以上不统计。"
                "『最近一个月工资』指该员工发薪日期最大的那条工资。按档位求平均。"
                "返回两列：档位（值必须正好是『入职一年内』/『一到两年』/『两到三年』）, 平均工资。",
    },
    {
        "id": 9,
        "nl": "去年到今年涨薪幅度最大的10位员工是谁？",
        "hint": "对每位员工，涨薪额 = 今年平均工资 - 去年平均工资，只统计去年和今年都有工资的员工，"
                "按涨薪额从高到低取前 10。返回两列：姓名, 涨薪额。",
    },
    {
        "id": 10,
        "nl": "有没有拖欠工资的情况（某个月还在职却没有发薪）？",
        "hint": "对每位员工，其在职月份从入职月份到（离职员工用离职月份、在职员工用当前月份），"
                "逐月检查是否有对应的发薪记录，找出缺失的（员工, 月份）。"
                "返回两列：emp_id, 月份（格式 YYYY-MM）。"
                "推荐写法（递归 CTE 里把『结束月份』一并带进去，避免相关子查询）：\n"
                "WITH RECURSIVE em(emp_id, m, end_m) AS (\n"
                "  SELECT emp_id, strftime('%Y-%m', hire_date),\n"
                "         COALESCE(strftime('%Y-%m', leave_date), strftime('%Y-%m','now'))\n"
                "  FROM employees\n"
                "  UNION ALL\n"
                "  SELECT emp_id, strftime('%Y-%m', date(m || '-01', '+1 month')), end_m\n"
                "  FROM em WHERE m < end_m)\n"
                "SELECT em.emp_id, em.m FROM em\n"
                "LEFT JOIN salaries s ON s.emp_id = em.emp_id "
                "AND strftime('%Y-%m', s.pay_date) = em.m\n"
                "WHERE s.emp_id IS NULL;",
    },
]

# 需要「按顺序」呈现的题目（校验时其实按集合比对内容即可，这里仅用于展示）
ORDERED = {9}
