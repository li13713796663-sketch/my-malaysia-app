"""马来西亚行政常量 — 供 engine 等模块引用（主逻辑已合并至 app.py）"""

ENROLLMENT_YEARS = list(range(2020, 2036))

DUZHONG_GRADES = ["初一", "初二", "初三", "高一", "高二", "高三"]
INTL_GRADES = [f"Year {i}" for i in range(1, 14)]
OTHER_GRADES = ["预科", "其他"]

ROLE_SUPER = "super_admin"
ROLE_ADMIN = "admin"


def grades_for_school_type(school_type: str) -> list[str]:
    if school_type == "华文独中":
        return DUZHONG_GRADES
    if school_type == "国际学校":
        return INTL_GRADES
    return OTHER_GRADES
