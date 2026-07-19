"""
10 道题的「标准 SQL」（gold SQL），SQLite 方言，人工编写并逐题核对过。

用途：
  - 离线演示（`python demo.py gold`）：不调用任何 API，直接执行这些 SQL，
    证明 schema + 种子数据这套数据模型本身是自洽、可查询的；
  - 作为 Agent 生成 SQL 的「参考写法」：与 reference.py（纯 Python 参考实现）
    语义一致，`demo.py` 会把执行结果与 reference.py 比对，逐题打印 通过/不通过。

约定：
  - 日期一律用 date('now','localtime') / strftime(...,'now','localtime') 取「今天」，
    与 seed.py 里以本地 date.today() 生成的数据对齐（避免 UTC 与本地相差一天）；
  - **不硬编码年份**，一律从数据库当前日期用修饰符推导（'-1 year' / 'start of year' 等）；
  - 「A部门」= 研发部，「B部门」= 销售部；「在职」= leave_date IS NULL。
"""

GOLD = {
    # 1. 平均每个员工在职多久（天）。离职用 leave_date，在职用今天。
    1: """
SELECT ROUND(AVG(
         julianday(COALESCE(leave_date, date('now','localtime')))
         - julianday(hire_date)
       ), 2) AS avg_tenure_days
FROM employees;
""".strip(),

    # 2. 每个部门有多少在职员工。
    2: """
SELECT department, COUNT(*) AS active_count
FROM employees
WHERE leave_date IS NULL
GROUP BY department;
""".strip(),

    # 3. 哪个部门（含离职）平均级别最高，只返回部门名。
    3: """
SELECT department
FROM employees
GROUP BY department
ORDER BY AVG(level) DESC
LIMIT 1;
""".strip(),

    # 4. 每个部门今年 / 去年各新入职多少人（按 hire_date 年份）。
    4: """
SELECT department,
       SUM(CASE WHEN strftime('%Y', hire_date)
                   = strftime('%Y','now','localtime')          THEN 1 ELSE 0 END) AS this_year,
       SUM(CASE WHEN strftime('%Y', hire_date)
                   = strftime('%Y','now','localtime','-1 year') THEN 1 ELSE 0 END) AS last_year
FROM employees
GROUP BY department
HAVING this_year > 0 OR last_year > 0;
""".strip(),

    # 5. 前年3月 ~ 去年5月（含两端），研发部（A部门）平均工资。
    5: """
SELECT ROUND(AVG(s.salary), 2) AS avg_salary
FROM salaries s
JOIN employees e ON e.emp_id = s.emp_id
WHERE e.department = '研发部'
  AND strftime('%Y-%m', s.pay_date) BETWEEN
        strftime('%Y-%m','now','localtime','start of year','-2 years','+2 months')
    AND strftime('%Y-%m','now','localtime','start of year','-1 year','+4 months');
""".strip(),

    # 6. 去年研发部（A）与销售部（B）平均工资，两行（含已离职员工）。
    6: """
SELECT e.department, ROUND(AVG(s.salary), 2) AS avg_salary
FROM salaries s
JOIN employees e ON e.emp_id = s.emp_id
WHERE e.department IN ('研发部','销售部')
  AND strftime('%Y', s.pay_date) = strftime('%Y','now','localtime','-1 year')
GROUP BY e.department;
""".strip(),

    # 7. 今年每个级别的员工平均工资。
    7: """
SELECT e.level, ROUND(AVG(s.salary), 2) AS avg_salary
FROM salaries s
JOIN employees e ON e.emp_id = s.emp_id
WHERE strftime('%Y', s.pay_date) = strftime('%Y','now','localtime')
GROUP BY e.level;
""".strip(),

    # 8. 工龄分档（入职一年内 / 一到两年 / 两到三年，三年以上不计），各档最近一月工资的平均。
    8: """
WITH latest AS (          -- 每位员工「最近一个月」的工资
  SELECT s.emp_id, s.salary
  FROM salaries s
  JOIN (SELECT emp_id, MAX(pay_date) AS mp FROM salaries GROUP BY emp_id) m
    ON m.emp_id = s.emp_id AND m.mp = s.pay_date
),
bucketed AS (             -- 给每位员工打上工龄档位
  SELECT e.emp_id,
         CASE
           WHEN julianday(date('now','localtime')) - julianday(e.hire_date) < 365  THEN '入职一年内'
           WHEN julianday(date('now','localtime')) - julianday(e.hire_date) < 730  THEN '一到两年'
           WHEN julianday(date('now','localtime')) - julianday(e.hire_date) < 1095 THEN '两到三年'
           ELSE NULL
         END AS bucket
  FROM employees e
)
SELECT b.bucket, ROUND(AVG(l.salary), 2) AS avg_salary
FROM bucketed b
JOIN latest l ON l.emp_id = b.emp_id
WHERE b.bucket IS NOT NULL
GROUP BY b.bucket;
""".strip(),

    # 9. 去年到今年涨薪额（今年均薪 - 去年均薪）最大的 10 人，只算两年都有工资的。
    9: """
WITH ty AS (
  SELECT emp_id, AVG(salary) AS a FROM salaries
  WHERE strftime('%Y', pay_date) = strftime('%Y','now','localtime')          GROUP BY emp_id),
ly AS (
  SELECT emp_id, AVG(salary) AS a FROM salaries
  WHERE strftime('%Y', pay_date) = strftime('%Y','now','localtime','-1 year') GROUP BY emp_id)
SELECT e.name, ROUND(ty.a - ly.a, 2) AS raise_amt
FROM ty
JOIN ly ON ty.emp_id = ly.emp_id
JOIN employees e ON e.emp_id = ty.emp_id
ORDER BY raise_amt DESC
LIMIT 10;
""".strip(),

    # 10. 拖欠工资：某月在职却没有发薪记录。递归展开每人的在职月份再左连接工资表。
    10: """
WITH RECURSIVE em(emp_id, m, end_m) AS (
  SELECT emp_id,
         strftime('%Y-%m', hire_date),
         COALESCE(strftime('%Y-%m', leave_date), strftime('%Y-%m','now','localtime'))
  FROM employees
  UNION ALL
  SELECT emp_id, strftime('%Y-%m', date(m || '-01', '+1 month')), end_m
  FROM em WHERE m < end_m)
SELECT em.emp_id, em.m
FROM em
LEFT JOIN salaries s
       ON s.emp_id = em.emp_id AND strftime('%Y-%m', s.pay_date) = em.m
WHERE s.emp_id IS NULL;
""".strip(),
}
