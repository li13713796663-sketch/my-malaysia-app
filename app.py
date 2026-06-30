"""
留学生档案管理系统 — 云端重构全量合一控制中心
数据层：PostgreSQL | 交互：无 st.form 联动表单 | 三语 | 全状态检索
"""

from __future__ import annotations

import uuid
import calendar
from datetime import date, datetime
from html import escape

import auth
import db
import pandas as pd
import streamlit as st

# ══════════════════════════════════════════════════════════════════
# 页面配置（必须是第一个 Streamlit 命令）
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="留学生档案管理系统",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="auto",
)

# ══════════════════════════════════════════════════════════════════
# 全局常量
# ══════════════════════════════════════════════════════════════════

ENROLLMENT_YEARS = list(range(2020, 2036))

STATUS_ACTIVE = "在读"
STATUS_GRADUATED = "已毕业"
STATUS_TRANSFER = "已转学（异地就读）"
STATUS_RETURNED = "已回国"
STATUS_OPTIONS = [STATUS_ACTIVE, STATUS_GRADUATED, STATUS_TRANSFER, STATUS_RETURNED]

DUZHONG_GRADES = ["初一", "初二", "初三", "高一", "高二", "高三"]
INTL_GRADES = [f"Year {i}" for i in range(1, 14)]
OTHER_GRADES = ["预科", "其他"]

GRADE_OPTIONS = ["— 请选择年级 —"] + DUZHONG_GRADES + INTL_GRADES + OTHER_GRADES

STATE_CITY_MAPPING = {
    "霹雳州 (Perak)": [
        "怡保 (Ipoh)", "太平 (Taiping)", "金宝 (Kampar)",
        "安顺 (Teluk Intan)", "红土坎 (Lumut)", "实兆远 (Sitiawan)",
    ],
    "吉隆坡 (Kuala Lumpur)": ["吉隆坡市区 (Kuala Lumpur City)"],
    "雪兰莪 (Selangor)": [
        "梳邦再也 (Subang Jaya)", "八打灵再也 (Petaling Jaya)",
        "莎阿南 (Shah Alam)", "巴生 (Klang)", "加影 (Kajang)",
        "赛城 (Cyberjaya)", "万挠 (Rawang)", "士毛月 (Semenyih)",
        "沙叻秀 (Cheras)", "蒲种 (Puchong)",
    ],
    "槟城 (Pulau Pinang)": [
        "乔治市 (George Town)", "北海 (Butterworth)", "大山脚 (Bukit Mertajam)",
        "峇都加湾 (Batu Kawan)", "威南 (Seberang Perai Selatan)",
    ],
    "柔佛 (Johor)": [
        "新山 (Johor Bahru)", "峇株巴辖 (Batu Pahat)", "居銮 (Kluang)",
        "麻坡 (Muar)", "昔加末 (Segamat)", "古来 (Kulai)", "依斯干达公主城 (Iskandar Puteri)",
    ],
    "马六甲 (Melaka)": [
        "马六甲市 (Melaka City)", "亚罗牙也 (Alor Gajah)", "马接 (Masjid Tanah)",
    ],
    "森美兰 (Negeri Sembilan)": [
        "芙蓉 (Seremban)", "波德申 (Port Dickson)", "仁保 (Jempol)",
    ],
    "布城 (Putrajaya)": ["布城直辖区 (Putrajaya Central)"],
    "彭亨 (Pahang)": [
        "关丹 (Kuantan)", "云顶高原 (Genting Highlands)", "文冬 (Bentong)",
        "淡马鲁 (Temerloh)", "金马仑高原 (Cameron Highlands)",
    ],
    "沙巴 (Sabah)": [
        "亚庇 (Kota Kinabalu)", "山打根 (Sandakan)", "斗湖 (Tawau)",
        "根地咬 (Keningau)", "仙本那 (Semporna)",
    ],
    "砂拉越 (Sarawak)": [
        "古晋 (Kuching)", "美里 (Miri)", "诗巫 (Sibu)",
        "民都鲁 (Bintulu)", "林梦 (Limbang)",
    ],
    "吉打 (Kedah)": [
        "亚罗士打 (Alor Setar)", "双溪大年 (Sungai Petani)", "浮罗交怡 (Langkawi)", "居林 (Kulim)",
    ],
    "登嘉楼 (Terengganu)": [
        "瓜拉登嘉楼 (Kuala Terengganu)", "甘马挽 (Kemaman)", "龙运 (Dungun)",
    ],
    "吉兰丹 (Kelantan)": ["哥打巴鲁 (Kota Bharu)", "话望生 (Gua Musang)"],
    "玻璃市 (Perlis)": ["加央 (Kangar)", "阿罗牙也 (Arau)"],
    "纳闽 (Labuan)": ["纳闽直辖区 (Labuan Victoria)"],
    "其他 (Others)": ["其他城市 (Other City)"],
}

LANG_DICT = {
    "简体中文": {
        "login_title": "留学生档案管理系统<br>请登录后使用",
        "username": "账号",
        "password": "密码",
        "login_btn": "登录系统",
        "login_err": "账号或密码错误，请重新输入。",
        "logout_btn": "退出登录",
        "curr_user": "当前用户",
        "role_super": "超级管理员",
        "role_admin": "普通管理员",
        "menu_home": "首页名册与精确检索",
        "menu_add": "新增留学生档案",
        "menu_timeline": "入学时间轴与档案回顾",
        "menu_password": "安全中心与密码修改",
        "menu_accounts": "账号管理",
        "search_name": "按名字/拼音找人（全状态）",
        "search_city": "中国居住地",
        "filter_region": "按大马就读州属筛选",
        "total_students": "共找到 {} 位学生（含在读/转学/毕业/回国）",
        "no_data": "暂无符合条件的学生档案。",
        "edit_title": "修改已有档案",
        "del_btn": "删除此学生档案",
        "step1": "第一步：基本隐私信息",
        "step2": "第二步：中国背景与关怀",
        "step3": "第三步：留学信息追踪",
        "step4": "第四步：状态与联系人",
        "state_banner_1": "上半学年",
        "state_banner_2": "下半学年",
        "hint_departure": "如：成都、深圳",
        "hint_hobbies": "特长、喜好、饮食习惯…",
        "save_new": "确认保存档案",
        "save_edit": "确认保存修改",
        "urgent_birthday_title": "紧急生日预警（未来7天）",
        "monthly_birthday_title": "本月寿星提醒",
    },
    "English": {
        "login_title": "Student Archive System<br>Please Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "login_err": "Invalid username or password.",
        "logout_btn": "Logout",
        "curr_user": "User",
        "role_super": "Super Admin",
        "role_admin": "Admin",
        "menu_home": "Roster & Search",
        "menu_add": "New Student",
        "menu_timeline": "Enrollment Timeline",
        "menu_password": "Change Password",
        "menu_accounts": "Account Management",
        "search_name": "Name/Pinyin (All Status)",
        "search_city": "China Departure City",
        "filter_region": "Filter by MY State",
        "total_students": "{} students found (all statuses)",
        "no_data": "No matching records.",
        "edit_title": "Edit Profile",
        "del_btn": "Delete Profile",
        "step1": "Step 1: Basic Info",
        "step2": "Step 2: Background & Care",
        "step3": "Step 3: Study Tracking",
        "step4": "Step 4: Status & Contacts",
        "state_banner_1": "First Half of Academic Year",
        "state_banner_2": "Second Half of Academic Year",
        "hint_departure": "e.g. Chengdu, Shenzhen",
        "hint_hobbies": "Talents, hobbies, diet…",
        "save_new": "Save Profile",
        "save_edit": "Save Changes",
        "urgent_birthday_title": "Urgent Birthday Alert (Next 7 Days)",
        "monthly_birthday_title": "Monthly Birthday Care",
    },
    "Bahasa Melayu": {
        "login_title": "Sistem Arkib Pelajar<br>Sila Log Masuk",
        "username": "Nama Pengguna",
        "password": "Kata Laluan",
        "login_btn": "Log Masuk",
        "login_err": "Nama pengguna atau kata laluan salah.",
        "logout_btn": "Log Keluar",
        "curr_user": "Pengguna",
        "role_super": "Pentadbir Utama",
        "role_admin": "Pentadbir Biasa",
        "menu_home": "Senarai & Carian",
        "menu_add": "Tambah Pelajar",
        "menu_timeline": "Garis Masa Kemasukan",
        "menu_password": "Tukar Kata Laluan",
        "menu_accounts": "Pengurusan Akaun",
        "search_name": "Cari Nama/Pinyin",
        "search_city": "Bandar Asal China",
        "filter_region": "Tapis Negeri MY",
        "total_students": "{} pelajar dijumpai",
        "no_data": "Tiada rekod sepadan.",
        "edit_title": "Kemas Kini Profil",
        "del_btn": "Padam Profil",
        "step1": "Langkah 1: Maklumat Asas",
        "step2": "Langkah 2: Latar & Penjagaan",
        "step3": "Langkah 3: Pengajian",
        "step4": "Langkah 4: Status & Hubungan",
        "state_banner_1": "Separuh Pertama Tahun Akademik",
        "state_banner_2": "Separuh Kedua Tahun Akademik",
        "hint_departure": "cth. Chengdu, Shenzhen",
        "hint_hobbies": "Bakat, hobi, diet…",
        "save_new": "Simpan Profil",
        "save_edit": "Simpan Perubahan",
        "urgent_birthday_title": "Peringatan Hari Lahir Segera (7 Hari)",
        "monthly_birthday_title": "Penjagaan Hari Lahir Bulanan",
    },
}

STUDENT_COLS = [
    "id", "name", "pinyin", "gender", "birth_date", "passport_no",
    "departure_city", "hobbies", "enrollment_year", "enrollment_month",
    "state", "city_my", "region", "school_type", "initial_grade",
    "status", "transfer_note", "emergency_phone_cn", "guardian_my",
    "created_by", "created_at", "updated_at",
]

SENIOR_CSS = """
<style>
    /* 保持顶部背景透明，允许侧边栏开关按钮正常显示 */
    header {
        background-color: transparent !important;
    }
    /* 精准隐藏顶部右侧的工具栏、分享按钮和主菜单 */
    [data-testid="stHeaderToolbar"] {
        display: none !important;
    }
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    /* 隐藏右下角官方头像、皇冠/纸船管理卡片及页脚 */
    footer {display: none !important;}
    #viewer-badge, .viewerBadge, [data-testid="stViewerBadge"] {
        display: none !important;
    }
    /* 针对外部注入的平台管理面板浮窗进行强制压制 */
    iframe[title="Manage app"] {
        display: none !important;
    }
    div.block-container {padding-top: 2rem !important;}
    html, body, [class*="css"] {
        font-size: 20px !important;
        color: #475569 !important;
    }
    .stApp {
        background: #F8FAFC;
    }
    h1, h2, h3 {
        color: #1E293B !important;
        letter-spacing: -0.01em;
    }
    h1 { font-size: 2.4rem !important; font-weight: 760 !important; }
    h2 { font-size: 2rem !important; font-weight: 720 !important; }
    h3 { font-size: 1.55rem !important; font-weight: 700 !important; }
    p, label, .stMarkdown, [data-testid="stText"] {
        color: #475569 !important;
    }
    small, caption, .stCaption, [data-testid="stCaptionContainer"] {
        color: #94A3B8 !important;
    }
    .big-label { font-size: 1.35rem !important; font-weight: 700 !important; color: #475569 !important; }
    .step-title {
        font-size: 1.5rem !important; font-weight: 700 !important; color: #1E293B !important;
        border-left: 6px solid #1E40AF; padding-left: 12px; margin: 1.2rem 0 0.8rem 0;
    }
    .semester-banner {
        background: linear-gradient(90deg, #1E40AF, #3B82F6); color: white;
        font-size: 1.4rem !important; font-weight: 700; text-align: center;
        padding: 14px 20px; border-radius: 10px; margin-bottom: 1rem;
    }
    .birthday-card {
        background: #fff8e1; border: 2px solid #ffb300;
        border-radius: 12px; padding: 16px 20px; margin-bottom: 1rem;
    }
    .login-title {
        font-size: 2rem !important; font-weight: 800 !important;
        text-align: center; color: #1E293B; margin-bottom: 0.35rem;
        line-height: 1.28;
    }
    .login-subtitle {
        text-align: center;
        color: #64748B !important;
        font-size: 1rem !important;
        margin: 0 0 1.4rem 0;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border-color: rgba(148, 163, 184, 0.28) !important;
        border-radius: 16px !important;
        box-shadow: 0 14px 34px rgba(30, 41, 59, 0.06);
    }
    div.stButton > button {
        font-size: 1.2rem !important; padding: 0.65rem 1.4rem !important;
        min-height: 3rem !important; border-radius: 10px !important;
    }
    div.stButton > button[kind="primary"] {
        font-size: 18px !important; font-weight: 800 !important; min-height: 3.5rem !important;
        background: #1E40AF !important;
        color: #FFFFFF !important;
        border: 1px solid #1E40AF !important;
        box-shadow: 0 12px 26px rgba(30, 64, 175, 0.22);
    }
    div.stButton > button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] *,
    [data-testid="stFormSubmitButton"] button[kind="primary"] * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 18px !important;
    }
    [data-testid="stSidebar"] { min-width: 280px !important; }
</style>
"""

st.markdown(SENIOR_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# UI 工具
# ══════════════════════════════════════════════════════════════════

def t(key: str) -> str:
    lang = st.session_state.get("language", "简体中文")
    return LANG_DICT[lang].get(key, key)


def big_label(text: str) -> None:
    st.markdown(f'<p class="big-label">{text}</p>', unsafe_allow_html=True)


def step_title(text: str) -> None:
    st.markdown(f'<p class="step-title">{text}</p>', unsafe_allow_html=True)


def _idx(options: list, value: str, default: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return default


# ══════════════════════════════════════════════════════════════════
# 年级 / 年龄引擎（运行时计算，不写库）
# ══════════════════════════════════════════════════════════════════

def _grades_for_type(school_type: str) -> list[str]:
    if school_type == "华文独中":
        return DUZHONG_GRADES
    if school_type == "国际学校":
        return INTL_GRADES
    if school_type == "其他/预科":
        return OTHER_GRADES
    return []


def calculate_age(birth: date, today: date | None = None) -> int:
    today = today or date.today()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age


def get_semester_label(today: date | None = None) -> str:
    today = today or date.today()
    return "上半学年" if today.month <= 6 else "下半学年"


def calculate_current_grade(student: dict, today: date | None = None) -> str:
    today = today or date.today()
    school_type = str(student.get("school_type", ""))
    initial = str(student.get("initial_grade", ""))
    try:
        enroll_year = int(str(student.get("enrollment_year", "0")).strip())
    except ValueError:
        return initial or "—"

    if initial.startswith("—") or not initial:
        return "—"

    if school_type == "其他/预科":
        return initial

    options = _grades_for_type(school_type)
    if initial not in options:
        return initial

    idx = options.index(initial)
    if school_type == "华文独中":
        diff = today.year - enroll_year
    elif school_type == "国际学校":
        diff = today.year - enroll_year if today.month >= 9 else today.year - enroll_year - 1
    else:
        return initial

    new_idx = idx + diff
    if new_idx >= len(options):
        return f"{options[-1]}（建议归档为已毕业）"
    if new_idx < 0:
        return options[0]
    return options[new_idx]


def enrich_student(student: dict, today: date | None = None) -> dict:
    today = today or date.today()
    out = dict(student)
    try:
        birth = date.fromisoformat(str(student.get("birth_date", ""))[:10])
        out["_age"] = calculate_age(birth, today)
    except ValueError:
        out["_age"] = "—"
    out["_current_grade"] = calculate_current_grade(student, today)
    ey = student.get("enrollment_year", "")
    em = student.get("enrollment_month", "")
    out["_enrollment_label"] = f"{ey}年{em}月" if ey and em else "—"
    return out


def enrich_all(students: list[dict]) -> list[dict]:
    return [enrich_student(s) for s in students]


def _student_is_active_visible(student: dict) -> bool:
    deleted_raw = str(student.get("is_deleted", "false")).strip().lower()
    is_deleted = deleted_raw in {"1", "true", "t", "yes", "y"}
    return not is_deleted and student.get("status", STATUS_ACTIVE) == STATUS_ACTIVE


def _parse_birth_date(student: dict) -> date | None:
    try:
        return date.fromisoformat(str(student.get("birth_date", ""))[:10])
    except ValueError:
        return None


def _birthday_in_year(birth: date, year: int) -> date:
    try:
        return birth.replace(year=year)
    except ValueError:
        return date(year, 2, 28)


def _birthday_label(birth: date) -> str:
    return f"{birth.month}月{birth.day}日"


def birthday_next_days(students: list[dict], days: int = 7, today: date | None = None) -> list[dict]:
    today = today or date.today()
    result = []
    for s in students:
        if not _student_is_active_visible(s):
            continue
        birth = _parse_birth_date(s)
        if not birth:
            continue
        next_birthday = _birthday_in_year(birth, today.year)
        if next_birthday < today:
            next_birthday = _birthday_in_year(birth, today.year + 1)
        days_until = (next_birthday - today).days
        if 0 <= days_until <= days:
            item = enrich_student(s, today)
            item["_birthday_label"] = _birthday_label(birth)
            item["_days_until"] = days_until
            result.append(item)
    return sorted(result, key=lambda x: (x.get("_days_until", 999), x.get("name", "")))


def birthday_this_month(students: list[dict], today: date | None = None) -> list[dict]:
    today = today or date.today()
    result = []
    for s in students:
        if not _student_is_active_visible(s):
            continue
        birth = _parse_birth_date(s)
        if birth and birth.month == today.month:
            item = enrich_student(s, today)
            item["_birth_day"] = birth.day
            item["_birthday_label"] = _birthday_label(birth)
            result.append(item)
    return sorted(result, key=lambda x: x.get("_birth_day", 0))


# ══════════════════════════════════════════════════════════════════
# 学生数据层 — PostgreSQL students 表
# ══════════════════════════════════════════════════════════════════

_INSERT_STUDENT_SQL = """
INSERT INTO students (
    id, name, pinyin, gender, birth_date, passport_no,
    departure_city, hobbies, enrollment_year, enrollment_month,
    state, city_my, region, school_type, initial_grade,
    status, transfer_note, emergency_phone_cn, guardian_my,
    created_by, created_at, updated_at
) VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s
)
"""

_UPDATE_STUDENT_SQL = """
UPDATE students SET
    name = %s, pinyin = %s, gender = %s, birth_date = %s, passport_no = %s,
    departure_city = %s, hobbies = %s, enrollment_year = %s, enrollment_month = %s,
    state = %s, city_my = %s, region = %s, school_type = %s, initial_grade = %s,
    status = %s, transfer_note = %s, emergency_phone_cn = %s, guardian_my = %s,
    created_by = %s, created_at = %s, updated_at = %s
WHERE id = %s
"""


def _record_to_params(record: dict) -> tuple:
    return tuple(str(record.get(c, "")) for c in STUDENT_COLS)


def load_students() -> list[dict]:
    db.ensure_schema()
    return db.fetch_all("SELECT * FROM students ORDER BY created_at DESC, name ASC")


def add_student(record: dict) -> None:
    db.execute(_INSERT_STUDENT_SQL, _record_to_params(record))


def update_student(student_id: str, record: dict) -> bool:
    exists = db.fetch_one("SELECT id FROM students WHERE id = %s", (str(student_id),))
    if not exists:
        return False
    record["id"] = str(student_id)
    params = _record_to_params(record)
    db.execute(_UPDATE_STUDENT_SQL, params[1:] + (params[0],))
    return True


def delete_student(student_id: str) -> bool:
    exists = db.fetch_one("SELECT id FROM students WHERE id = %s", (str(student_id),))
    if not exists:
        return False
    db.execute("DELETE FROM students WHERE id = %s", (str(student_id),))
    return True


def build_record(form: dict, created_by: str, student_id: str | None = None, created_at: str | None = None) -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    status = form["status"]
    return {
        "id": student_id or str(uuid.uuid4())[:8],
        "name": form["name"],
        "pinyin": form["pinyin"],
        "gender": form["gender"],
        "birth_date": form["birth_date"],
        "passport_no": form["passport_no"],
        "departure_city": form["departure_city"],
        "hobbies": form["hobbies"],
        "enrollment_year": form["enrollment_year"],
        "enrollment_month": form["enrollment_month"],
        "state": form["state"],
        "city_my": form["city_my"],
        "region": f"{form['state']} - {form['city_my']}",
        "school_type": form["school_type"],
        "initial_grade": form["initial_grade"],
        "status": status,
        "transfer_note": form["transfer_note"] if STATUS_TRANSFER in status else "",
        "emergency_phone_cn": form["emergency_phone_cn"],
        "guardian_my": form["guardian_my"],
        "created_by": created_by,
        "created_at": created_at or now,
        "updated_at": now,
    }


# ══════════════════════════════════════════════════════════════════
# 响应式联动表单（无 st.form）
# ══════════════════════════════════════════════════════════════════

def render_student_form(form_key: str, created_by: str, defaults: dict | None = None, is_edit: bool = False) -> dict | None:
    defaults = defaults or {}
    today = date.today()

    birth_val = defaults.get("birth_date", "")
    birth_default = date.fromisoformat(str(birth_val)[:10]) if birth_val else today
    birth_year_opts = list(range(today.year - 40, today.year + 1))
    birth_month_opts = list(range(1, 13))
    birth_day_opts = list(range(1, 32))
    year_opts = [" "] + [str(y) for y in ENROLLMENT_YEARS]
    month_opts = [" "] + [f"{m}月" for m in range(1, 13)]
    state_opts = ["— 请选择就读州属 —"] + list(STATE_CITY_MAPPING.keys())
    school_opts = ["— 请选择学制 —", "华文独中", "国际学校", "其他/预科"]
    gender_opts = ["— 请选择性别 —", "男", "女"]
    status_opts = ["— 请选择就读状态 —"] + STATUS_OPTIONS

    with st.form(key="student_entry_form", clear_on_submit=True):
        step_title(t("step1"))
        c1, c2 = st.columns(2)
        with c1:
            big_label("中文姓名")
            name = st.text_input(f"{form_key}_name", value=defaults.get("name", ""), label_visibility="collapsed", placeholder="请输入中文姓名")
            big_label("护照号码")
            passport_no = st.text_input(f"{form_key}_pass", value=defaults.get("passport_no", ""), label_visibility="collapsed", placeholder="请输入护照号")
        with c2:
            big_label("大写护照拼音")
            pinyin = st.text_input(f"{form_key}_py", value=defaults.get("pinyin", ""), label_visibility="collapsed", placeholder="如 ZHANG SAN")
            big_label("性别")
            gender = st.selectbox(f"{form_key}_gen", gender_opts, index=_idx(gender_opts, defaults.get("gender", gender_opts[0])), label_visibility="collapsed")

        big_label("出生日期")
        by_col, bm_col, bd_col = st.columns(3)
        with by_col:
            birth_year = st.selectbox(
                "出生年份",
                birth_year_opts,
                index=_idx(birth_year_opts, birth_default.year),
                key=f"{form_key}_birth_year",
                label_visibility="collapsed",
                format_func=lambda y: f"{y} 年",
            )
        with bm_col:
            birth_month = st.selectbox(
                "出生月份",
                birth_month_opts,
                index=_idx(birth_month_opts, birth_default.month),
                key=f"{form_key}_birth_month",
                label_visibility="collapsed",
                format_func=lambda m: f"{m} 月",
            )
        with bd_col:
            birth_day = st.selectbox(
                "出生日期",
                birth_day_opts,
                index=_idx(birth_day_opts, birth_default.day),
                key=f"{form_key}_birth_day",
                label_visibility="collapsed",
                format_func=lambda d: f"{d} 日",
            )

        step_title(t("step2"))
        big_label("中国居住地")
        departure_city = st.text_input("中国居住地", value=defaults.get("departure_city", ""), key=f"{form_key}_dep", label_visibility="collapsed", placeholder=t("hint_departure"))
        big_label("兴趣爱好 / 饮食习惯")
        hobbies = st.text_area(f"{form_key}_hob", value=defaults.get("hobbies", ""), label_visibility="collapsed", placeholder=t("hint_hobbies"), height=90)

        step_title(t("step3"))
        c3, c4 = st.columns(2)
        with c3:
            big_label("入学年份")
            ey_raw = str(defaults.get("enrollment_year", " ")).strip() or " "
            enrollment_year = st.selectbox(f"{form_key}_ey", year_opts, index=_idx(year_opts, ey_raw), label_visibility="collapsed")
        with c4:
            big_label("入学月份")
            em_raw = defaults.get("enrollment_month", "")
            em_label = f"{em_raw}月" if str(em_raw).strip() and str(em_raw).strip() != " " else " "
            enrollment_month = st.selectbox(f"{form_key}_em", month_opts, index=_idx(month_opts, em_label), label_visibility="collapsed")

        big_label("大马就读州属 → 城市")
        sc1, sc2 = st.columns(2)
        with sc1:
            selected_state = st.selectbox(
                f"{form_key}_state", state_opts,
                index=_idx(state_opts, defaults.get("state", state_opts[0])),
                label_visibility="collapsed",
            )
        if selected_state in STATE_CITY_MAPPING:
            city_opts = ["— 请选择就读城市 —"] + STATE_CITY_MAPPING[selected_state]
        else:
            city_opts = ["— 请选择就读城市 —"]
        city_default = defaults.get("city_my", city_opts[0])
        if defaults.get("state") != selected_state or city_default not in city_opts:
            city_default = city_opts[0]
        with sc2:
            selected_city = st.selectbox(
                f"{form_key}_city_{selected_state}",
                city_opts, index=_idx(city_opts, city_default),
                label_visibility="collapsed",
            )

        c5, c6 = st.columns(2)
        with c5:
            big_label("当前学制")
            school_type = st.selectbox(f"{form_key}_stype", school_opts, index=_idx(school_opts, defaults.get("school_type", school_opts[0])), label_visibility="collapsed")
        with c6:
            big_label("入学初始年级")
            ig = defaults.get("initial_grade", GRADE_OPTIONS[0])
            initial_grade = st.selectbox(f"{form_key}_ig", GRADE_OPTIONS, index=_idx(GRADE_OPTIONS, ig if ig in GRADE_OPTIONS else GRADE_OPTIONS[0]), label_visibility="collapsed")

        step_title(t("step4"))
        c7, c8 = st.columns(2)
        with c7:
            big_label("就读状态")
            status = st.selectbox(f"{form_key}_stat", status_opts, index=_idx(status_opts, defaults.get("status", status_opts[0])), label_visibility="collapsed")
        with c8:
            big_label("中国紧急联系电话")
            emergency_phone_cn = st.text_input(f"{form_key}_phone", value=defaults.get("emergency_phone_cn", ""), label_visibility="collapsed", placeholder="国内紧急联系人电话")

        transfer_note = ""
        if status == STATUS_TRANSFER:
            big_label("转学去向备注（必填）")
            transfer_note = st.text_input(f"{form_key}_trans", value=defaults.get("transfer_note", ""), label_visibility="collapsed", placeholder="新学校名称 + 州属 + 城市")

        big_label("大马本地监护人 / 宿舍信息")
        guardian_my = st.text_area(f"{form_key}_guard", value=defaults.get("guardian_my", ""), label_visibility="collapsed", height=90)

        btn = t("save_edit") if is_edit else t("save_new")
        submitted = st.form_submit_button(btn, type="primary", use_container_width=True)

    if not submitted:
        return None

    if not name.strip():
        st.error("请填写中文姓名。"); return None
    if gender == "— 请选择性别 —":
        st.error("请选择性别。"); return None
    if enrollment_year.strip() in ("", " "):
        st.error("请选择入学年份。"); return None
    if enrollment_month.strip() in ("", " "):
        st.error("请选择入学月份。"); return None
    if selected_state == "— 请选择就读州属 —":
        st.error("请选择就读州属。"); return None
    if selected_city == "— 请选择就读城市 —":
        st.error("请选择就读城市。"); return None
    if school_type == "— 请选择学制 —":
        st.error("请选择学制。"); return None
    if initial_grade == "— 请选择年级 —":
        st.error("请选择入学初始年级。"); return None
    if status == "— 请选择就读状态 —":
        st.error("请选择就读状态。"); return None
    if status == STATUS_TRANSFER and not transfer_note.strip():
        st.error("已转学须填写转学去向备注。"); return None
    if birth_day > calendar.monthrange(birth_year, birth_month)[1]:
        st.error("请选择有效的出生日期。"); return None

    birth_date = date(birth_year, birth_month, birth_day)

    return {
        "name": name.strip(),
        "pinyin": pinyin.strip().upper(),
        "gender": gender,
        "passport_no": passport_no.strip(),
        "birth_date": birth_date.isoformat(),
        "departure_city": departure_city.strip(),
        "hobbies": hobbies.strip(),
        "enrollment_year": enrollment_year.strip(),
        "enrollment_month": enrollment_month.replace("月", "").strip(),
        "state": selected_state,
        "city_my": selected_city,
        "school_type": school_type,
        "initial_grade": initial_grade,
        "status": status,
        "transfer_note": transfer_note.strip(),
        "emergency_phone_cn": emergency_phone_cn.strip(),
        "guardian_my": guardian_my.strip(),
    }


# ══════════════════════════════════════════════════════════════════
# Session / 登录
# ══════════════════════════════════════════════════════════════════

def init_session() -> None:
    for key, val in {
        "authenticated": False,
        "username": "",
        "role": "",
        "language": "简体中文",
        "home_state_filter": "全部地区",
        "home_search_name": "",
        "home_search_city": "",
        "login_user_buf": "",
        "login_pass_buf": "",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_login() -> None:
    lang_col1, lang_col2 = st.columns([4, 1])
    with lang_col2:
        st.selectbox("Language", list(LANG_DICT.keys()), key="language", label_visibility="collapsed")

    spacer_left, login_col, spacer_right = st.columns([1, 1.28, 1])
    with login_col:
        with st.container(border=True):
            st.markdown(f'<p class="login-title">{t("login_title")}</p>', unsafe_allow_html=True)
            st.markdown(
                '<p class="login-subtitle">请使用管理员账号登录，数据将安全同步至云端。</p>',
                unsafe_allow_html=True,
            )

            big_label(t("username"))
            st.text_input(
                "login_user_pure_v9",
                value="",
                key="login_user_buf",
                label_visibility="collapsed",
                placeholder="请输入管理员账号",
                autocomplete="off",
            )
            big_label(t("password"))
            st.text_input(
                "login_pass_pure_v9",
                value="",
                key="login_pass_buf",
                type="password",
                label_visibility="collapsed",
                placeholder="请输入登录密码",
                autocomplete="new-password",
            )

            if st.button(t("login_btn"), type="primary", use_container_width=True, key="login_submit_v9"):
                user = auth.verify_login(st.session_state.login_user_buf, st.session_state.login_pass_buf)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user["username"]
                    st.session_state.role = user["role"]
                    st.rerun()
                st.error(t("login_err"))


def require_auth() -> None:
    init_session()
    auth.load_users()
    if not st.session_state.authenticated:
        render_login()
        st.stop()


def render_sidebar_styles() -> None:
    st.sidebar.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
            }
            [data-testid="stSidebar"] h1 {
                font-size: 1.45rem !important;
                letter-spacing: 0.02em;
                margin-bottom: 1rem;
                color: #1E293B !important;
            }
            [data-testid="stSidebar"] [role="radiogroup"] {
                display: flex;
                flex-direction: column;
                gap: 0.38rem;
            }
            [data-testid="stSidebar"] [role="radio"] {
                min-height: 2.65rem;
                padding: 0.36rem 0.52rem;
                border-radius: 12px;
                white-space: nowrap;
                transition: background-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
            }
            [data-testid="stSidebar"] [role="radio"]:hover {
                background: rgba(30, 64, 175, 0.09);
                box-shadow: 0 6px 18px rgba(30, 41, 59, 0.08);
                transform: translateX(2px);
            }
            [data-testid="stSidebar"] [role="radio"] p {
                font-size: 1.02rem !important;
                line-height: 1.35 !important;
                white-space: nowrap !important;
                margin: 0 !important;
                color: #475569 !important;
            }
            .sidebar-user-card {
                margin-top: 1.1rem;
                padding: 1rem 1rem 0.9rem;
                border-radius: 12px;
                background: linear-gradient(145deg, #FFFFFF 0%, #F1F5F9 100%);
                box-shadow: 0 10px 28px rgba(30, 41, 59, 0.10);
                border: 1px solid rgba(115, 145, 190, 0.18);
            }
            .sidebar-user-label {
                font-size: 0.72rem;
                color: #94A3B8;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.12rem;
            }
            .sidebar-user-name {
                font-size: 1.08rem;
                font-weight: 760;
                color: #1E293B;
                line-height: 1.25;
                margin-bottom: 0.72rem;
                word-break: break-word;
            }
            .sidebar-role-pill {
                display: inline-flex;
                align-items: center;
                padding: 0.26rem 0.72rem;
                border-radius: 999px;
                background: rgba(30, 64, 175, 0.10);
                color: #1E40AF;
                font-size: 0.9rem;
                font-weight: 700;
            }
            [data-testid="stSidebar"] div.stButton > button {
                margin-top: 0.72rem;
                border-radius: 12px !important;
                border: 1px solid rgba(37, 99, 235, 0.14) !important;
                background: #ffffff !important;
                color: #1E293B !important;
                box-shadow: 0 8px 20px rgba(30, 41, 59, 0.08);
                transition: background-color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
            }
            [data-testid="stSidebar"] div.stButton > button:hover {
                background: #EFF6FF !important;
                transform: translateY(-1px);
                box-shadow: 0 12px 26px rgba(30, 41, 59, 0.12);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    render_sidebar_styles()
    st.sidebar.title("导航")
    pages = {
        t("menu_home"): "home",
        t("menu_add"): "add",
        t("menu_timeline"): "timeline",
        t("menu_password"): "password",
    }
    if auth.is_super_admin(st.session_state.username):
        pages[t("menu_accounts")] = "accounts"

    choice = st.sidebar.radio("nav", list(pages.keys()), label_visibility="collapsed")
    st.sidebar.divider()
    role = t("role_super") if auth.is_super_admin(st.session_state.username) else t("role_admin")
    safe_username = escape(st.session_state.username)
    safe_role = escape(role)
    st.sidebar.markdown(
        f"""
        <div class="sidebar-user-card">
            <div class="sidebar-user-label">{t('curr_user')}</div>
            <div class="sidebar-user-name">{safe_username}</div>
            <div class="sidebar-user-label">权限</div>
            <div class="sidebar-role-pill">{safe_role}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button(t("logout_btn"), use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
    return pages[choice]


# ══════════════════════════════════════════════════════════════════
# 页面
# ══════════════════════════════════════════════════════════════════

def _status_display(student: dict) -> str:
    status = student.get("status", STATUS_ACTIVE)
    note = str(student.get("transfer_note", "")).strip()
    if status != STATUS_ACTIVE and note:
        return f"{status}（{note}）"
    if status == STATUS_TRANSFER and note:
        return f"{status}（{note}）"
    return status


def _filter_students(students: list[dict]) -> list[dict]:
    result = students
    sf = st.session_state.home_state_filter
    if sf != "全部地区":
        result = [s for s in result if s.get("state") == sf]
    nq = st.session_state.home_search_name.strip().lower()
    if nq:
        result = [s for s in result if nq in s.get("name", "").lower() or nq in s.get("pinyin", "").lower()]
    cq = st.session_state.home_search_city.strip().lower()
    if cq:
        result = [s for s in result if cq in s.get("departure_city", "").lower()]
    return result


def page_home() -> None:
    st.title(t("menu_home"))
    raw = load_students()
    all_s = enrich_all(raw)
    urgent_birthdays = birthday_next_days(raw)
    monthly_birthdays = birthday_this_month(raw)

    if urgent_birthdays or monthly_birthdays:
        with st.container(border=True):
            if urgent_birthdays:
                st.markdown(f"### {t('urgent_birthday_title')}")
                for s in urgent_birthdays:
                    st.markdown(
                        f"- 紧急生日预警：**{s['name']}**（{s['_birthday_label']}）"
                        f" · 还有 {s['_days_until']} 天"
                    )
            if monthly_birthdays:
                st.markdown(f"### {t('monthly_birthday_title')}")
                for s in monthly_birthdays:
                    st.markdown(f"- 本月寿星提醒：**{s['name']}**（{s['_birthday_label']}）")

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            big_label(t("search_name"))
            st.text_input("home_search_name", key="home_search_name", label_visibility="collapsed", placeholder="姓名或拼音，回车即搜")
        with c2:
            big_label(t("search_city"))
            st.text_input("home_search_city", key="home_search_city", label_visibility="collapsed", placeholder=t("hint_departure"))

        big_label(t("filter_region"))
        region_opts = ["全部地区"] + list(STATE_CITY_MAPPING.keys())
        sel = st.selectbox("home_state_filter_box", region_opts, index=_idx(region_opts, st.session_state.home_state_filter), label_visibility="collapsed")
        if sel != st.session_state.home_state_filter:
            st.session_state.home_state_filter = sel
            st.rerun()

    filtered = _filter_students(all_s)
    st.markdown(f"**{t('total_students').format(len(filtered))}**")

    if filtered:
        rows = [{
            "姓名": s["name"], "拼音": s["pinyin"], "年龄": s["_age"],
            "推算年级": s["_current_grade"], "中国出发城市": s["departure_city"],
            "大马州属": s.get("state", "—"), "就读城市": s.get("city_my", "—"),
            "就读状态": _status_display(s), "学制": s.get("school_type", "—"),
            "关怀备注": s.get("hobbies") or "—",
        } for s in filtered]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info(t("no_data"))

    if all_s:
        st.divider()
        step_title(t("edit_title"))
        labels = {f"{s['name']}（{s['pinyin']}）· {s.get('status','')}": s for s in all_s}
        pick = st.selectbox("edit_pick", list(labels.keys()), key="edit_pick")
        target = labels[pick]
        form = render_student_form(f"edit_{target['id']}", target.get("created_by", st.session_state.username), target, True)
        if form:
            if update_student(target["id"], build_record(form, target.get("created_by", st.session_state.username), target["id"], target.get("created_at"))):
                st.success("档案已更新并同步云端。")
                st.rerun()
        if st.button(t("del_btn"), key="del_student_btn"):
            if delete_student(target["id"]):
                st.success("已删除。")
                st.rerun()


def page_add() -> None:
    st.title(t("menu_add"))
    form = render_student_form("add_new", st.session_state.username)
    if form:
        add_student(build_record(form, st.session_state.username))
        st.success("档案已安全入库！")
        st.balloons()


def page_timeline() -> None:
    st.title(t("menu_timeline"))
    c1, c2 = st.columns(2)
    with c1:
        y = st.selectbox("", ENROLLMENT_YEARS, format_func=lambda v: f"{v} 年", key="tl_y", label_visibility="collapsed")
    with c2:
        m = st.selectbox("", list(range(1, 13)), format_func=lambda v: f"{v} 月", key="tl_m", label_visibility="collapsed")
    matched = [s for s in enrich_all(load_students()) if str(s.get("enrollment_year")) == str(y) and str(s.get("enrollment_month")) == str(m)]
    st.info(f"{y} 年 {m} 月入境学生：{len(matched)} 人")
    for s in matched:
        st.markdown(f"### {s['name']} ({s['pinyin']}) — {s.get('status','')}")
        st.markdown(
            f"- 出发城市: {s['departure_city']} | 就读: {s.get('state','—')} - {s.get('city_my','—')}\n"
            f"- 年级: {s['_current_grade']} | 电话: {s.get('emergency_phone_cn','—')}\n"
            f"- 备注: {s.get('hobbies') or '—'}"
        )
        if s.get("transfer_note"):
            st.caption(f"去向备注: {s['transfer_note']}")
        st.divider()


def page_password() -> None:
    st.title(t("menu_password"))
    big_label("当前旧密码")
    old_p = st.text_input("pwd_old", type="password", label_visibility="collapsed", key="pwd_old_v1")
    big_label("新密码（至少6位）")
    new_p = st.text_input("pwd_new", type="password", label_visibility="collapsed", key="pwd_new_v1")
    big_label("确认新密码")
    confirm_p = st.text_input("pwd_confirm", type="password", label_visibility="collapsed", key="pwd_confirm_v1")
    if st.button("确认修改密码", type="primary", use_container_width=True):
        if new_p != confirm_p:
            st.error("两次新密码不一致。")
        else:
            ok, msg = auth.change_my_password(st.session_state.username, old_p, new_p)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def page_accounts() -> None:
    if not auth.is_super_admin(st.session_state.username):
        st.error("无权访问。")
        st.stop()

    st.title(t("menu_accounts"))
    st.subheader("创建普通管理员")
    new_u = st.text_input("", placeholder="新账号名", key="acc_new_u", label_visibility="collapsed")
    new_p = st.text_input("", type="password", placeholder="初始密码", key="acc_new_p", label_visibility="collapsed")
    verify1 = st.text_input("", type="password", placeholder="二次核验：输入您本人密码", key="acc_verify1", label_visibility="collapsed")
    if st.button("确认创建", type="primary", key="acc_create_btn"):
        ok, msg = auth.create_admin(new_u, new_p, st.session_state.username, verify1)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
        if ok:
            st.rerun()

    st.subheader("账号列表")
    admins = auth.list_admins()
    st.dataframe(pd.DataFrame([{
        "账号": a["username"],
        "角色": "超级管理员" if auth.is_super_admin(a["username"]) else "普通管理员",
        "创建时间": a.get("created_at", ""),
    } for a in admins]), use_container_width=True, hide_index=True)

    deletable = [a["username"] for a in admins if not auth.is_super_admin(a["username"])]
    if deletable:
        st.subheader("注销管理员")
        del_u = st.selectbox("", deletable, key="acc_del_u", label_visibility="collapsed")
        verify2 = st.text_input("", type="password", placeholder="二次核验：输入您本人密码", key="acc_verify2", label_visibility="collapsed")
        if st.button("确认注销", type="secondary", key="acc_del_btn"):
            ok, msg = auth.delete_admin(del_u, st.session_state.username, verify2)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
            if ok:
                st.rerun()


# ══════════════════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    db.ensure_schema()
    require_auth()
    top1, top2 = st.columns([4, 1])
    with top1:
        banner = f"{datetime.now().year}年度 {get_semester_label()}"
        st.markdown(f'<div class="semester-banner">{banner}</div>', unsafe_allow_html=True)
    with top2:
        st.selectbox("lang_top", list(LANG_DICT.keys()), key="language", label_visibility="collapsed")

    route = render_sidebar()
    {"home": page_home, "add": page_add, "timeline": page_timeline, "password": page_password, "accounts": page_accounts}[route]()


main()
