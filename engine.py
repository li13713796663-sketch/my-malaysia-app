"""年级、年龄、学期等动态计算引擎（结果不写库）"""

from datetime import date

from constants import DUZHONG_GRADES, INTL_GRADES, OTHER_GRADES, grades_for_school_type


def calculate_age(birth_date: date, today: date | None = None) -> int:
    today = today or date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def get_semester_label(today: date | None = None) -> str:
    today = today or date.today()
    if 1 <= today.month <= 6:
        return "当前处于：上半学年"
    return "当前处于：下半学年"


def birthday_this_month(students: list[dict], today: date | None = None) -> list[dict]:
    today = today or date.today()
    result = []
    for s in students:
        birth = date.fromisoformat(s["birth_date"])
        if birth.month == today.month:
            enriched = dict(s)
            enriched["_age"] = calculate_age(birth, today)
            enriched["_birth_day"] = birth.day
            result.append(enriched)
    return sorted(result, key=lambda x: x["_birth_day"])


def _grade_index(grade: str, options: list[str]) -> int | None:
    try:
        return options.index(grade)
    except ValueError:
        return None


def calculate_current_grade(student: dict, today: date | None = None) -> dict:
    """返回当前年级及提示信息（不写入数据库）。"""
    today = today or date.today()
    school_type = student["school_type"]
    initial = student["initial_grade"]
    enroll_year = int(student["enrollment_year"])

    if school_type == "其他/预科":
        return {
            "grade": initial,
            "warning": "该生为预科/其他类型，请手动确认当前年级。",
            "suggest_graduated": False,
        }

    options = grades_for_school_type(school_type)
    idx = _grade_index(initial, options)
    if idx is None:
        return {
            "grade": initial,
            "warning": "初始年级无法识别，请核对档案。",
            "suggest_graduated": False,
        }

    if school_type == "华文独中":
        year_diff = today.year - enroll_year
        new_idx = idx + year_diff
    else:
        if today.month >= 9:
            year_diff = today.year - enroll_year
        else:
            year_diff = today.year - enroll_year - 1
        new_idx = idx + year_diff

    if new_idx >= len(options):
        return {
            "grade": options[-1],
            "warning": f"按入学时间推算已超过最高年级（{options[-1]}），建议将状态更新为「已毕业」。",
            "suggest_graduated": True,
        }

    if new_idx < 0:
        return {
            "grade": options[0],
            "warning": "按入学时间推算尚未到入学年级，请核对入学年份。",
            "suggest_graduated": False,
        }

    return {
        "grade": options[new_idx],
        "warning": "",
        "suggest_graduated": False,
    }


def enrich_student(student: dict, today: date | None = None) -> dict:
    """为学生记录附加运行时计算字段。"""
    today = today or date.today()
    birth = date.fromisoformat(student["birth_date"])
    grade_info = calculate_current_grade(student, today)
    enriched = dict(student)
    enriched["_age"] = calculate_age(birth, today)
    enriched["_current_grade"] = grade_info["grade"]
    enriched["_grade_warning"] = grade_info["warning"]
    enriched["_suggest_graduated"] = grade_info["suggest_graduated"]
    enriched["_enrollment_label"] = f"{student['enrollment_year']}年{student['enrollment_month']}月"
    return enriched


def enrich_all(students: list[dict], today: date | None = None) -> list[dict]:
    return [enrich_student(s, today) for s in students]
