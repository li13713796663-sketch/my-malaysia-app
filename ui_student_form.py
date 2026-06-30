"""
留学生管理系统 — 纯净空白格子与全量下拉框占位对齐表单组件
"""

import calendar
from datetime import date
import streamlit as st
from constants import ENROLLMENT_YEARS, STATE_CITY_MAPPING, LANG_DICT, STATUS_OPTIONS

def render_student_form(form_key: str, created_by: str, defaults: dict = None, is_edit: bool = False) -> dict | None:
    if defaults is None:
        defaults = {}

    lang = st.session_state.get("language", "简体中文")
    t = LANG_DICT[lang]

    # 解析联动数据的默认值状态
    default_state = defaults.get("state", list(STATE_CITY_MAPPING.keys())[0])
    if default_state not in STATE_CITY_MAPPING:
        default_state = list(STATE_CITY_MAPPING.keys())[0]
        
    default_city = defaults.get("city_my", STATE_CITY_MAPPING[default_state][0])
    if default_city not in STATE_CITY_MAPPING[default_state]:
        default_city = STATE_CITY_MAPPING[default_state][0]

    with st.form(form_key):
        st.markdown("### 第一步：学生基本隐私信息")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**中文姓名**")
            name = st.text_input("name_in", value=defaults.get("name", ""), key=f"{form_key}_name", placeholder="请输入名字")
            st.markdown("**护照号码**")
            passport = st.text_input("pass_in", value=defaults.get("passport", ""), key=f"{form_key}_pass", placeholder="请输入护照号")
        with c2:
            st.markdown("**大写护照拼音**")
            pinyin = st.text_input("py_in", value=defaults.get("pinyin", ""), key=f"{form_key}_py", placeholder="如：ZHANG SAN")
            st.markdown("**性别**")
            # 性别增加伪空白占位符
            gender_options = ["— 请选择性别 —", "男", "女"]
            gender_idx = 0
            if defaults.get("gender") in ["男", "女"]:
                gender_idx = gender_options.index(defaults.get("gender"))
            gender = st.selectbox("gen_in", gender_options, index=gender_idx, key=f"{form_key}_gen", label_visibility="collapsed")

        today = date.today()
        # 出生日期一进来默认跟随今天，不再写死旧年份
        default_birth = date.fromisoformat(defaults["birth_date"]) if defaults.get("birth_date") else today
        st.markdown("**出生日期**")
        by_col, bm_col, bd_col = st.columns(3)
        with by_col:
            birth_year = st.selectbox(
                "birth_year_in",
                list(range(today.year - 40, today.year + 1)),
                index=list(range(today.year - 40, today.year + 1)).index(default_birth.year),
                key=f"{form_key}_birth_year",
                label_visibility="collapsed",
                format_func=lambda y: f"{y} 年",
            )
        with bm_col:
            birth_month = st.selectbox(
                "birth_month_in",
                list(range(1, 13)),
                index=default_birth.month - 1,
                key=f"{form_key}_birth_month",
                label_visibility="collapsed",
                format_func=lambda m: f"{m} 月",
            )
        with bd_col:
            birth_day = st.selectbox(
                "birth_day_in",
                list(range(1, 32)),
                index=default_birth.day - 1,
                key=f"{form_key}_birth_day",
                label_visibility="collapsed",
                format_func=lambda d: f"{d} 日",
            )

        st.divider()
        st.markdown("### 第二步：中国背景与关怀备注")
        
        st.markdown("**中国居住地**")
        departure_city = st.text_input("dep_in", value=defaults.get("departure_city", ""), key=f"{form_key}_dep", placeholder=t["hint_departure"], label_visibility="collapsed")
        
        st.markdown("**兴趣爱好、饮食与日常备注**")
        hobbies = st.text_area("hob_in", value=defaults.get("hobbies", ""), key=f"{form_key}_hob", placeholder=t["hint_hobbies"], label_visibility="collapsed")

        st.divider()
        st.markdown(f"### {t['step3_title']}")
        
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**入学年份**")
            # 入学年份伪空白化
            year_options = [" "] + [str(y) for y in ENROLLMENT_YEARS]
            ey_val = defaults.get("enrollment_year", "")
            ey_idx = year_options.index(str(ey_val)) if str(ey_val) in year_options else 0
            enrollment_year = st.selectbox("ey_in", year_options, index=ey_idx, key=f"{form_key}_ey", label_visibility="collapsed")
        with cc2:
            st.markdown("**入学月份**")
            # 入学月份伪空白化
            month_options = [" "] + [f"{m}月" for m in range(1, 13)]
            em_val = defaults.get("enrollment_month", "")
            em_str = f"{em_val}月" if em_val else ""
            em_idx = month_options.index(em_str) if em_str in month_options else 0
            enrollment_month = st.selectbox("em_in", month_options, index=em_idx, key=f"{form_key}_em", label_visibility="collapsed")

        st.markdown("**大马就读学校所在地（省市联动）**")
        ccc1, ccc2 = st.columns(2)
        with ccc1:
            state_list = list(STATE_CITY_MAPPING.keys())
            selected_state = st.selectbox(
                t["select_state"], state_list, 
                index=state_list.index(default_state), 
                key=f"{form_key}_state_select",
                label_visibility="collapsed"
            )
        with ccc2:
            city_options = STATE_CITY_MAPPING[selected_state]
            c_idx = city_options.index(default_city) if default_city in city_options else 0
            selected_city = st.selectbox(
                t["select_city"], city_options, 
                index=c_idx, 
                key=f"{form_key}_city_select",
                label_visibility="collapsed"
            )

        cccc1, cccc2 = st.columns(2)
        with cccc1:
            st.markdown("**当前学制**")
            # 学制伪空白化
            school_options = ["— 请选择学制 —", "华文独中", "国际学校", "其他/预科"]
            stype = defaults.get("school_type", "")
            st_idx = school_options.index(stype) if stype in school_options else 0
            school_type = st.selectbox("st_in", school_options, index=st_idx, key=f"{form_key}_st", label_visibility="collapsed")
        with cccc2:
            st.markdown("**入学初始年级**")
            # 年级伪空白化
            grade_options = ["— 请选择年级 —", '初一', '初二', '初三', '高一', '高二', '高三', 'Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6', 'Year 7', 'Year 8', 'Year 9', 'Year 10', 'Year 11', 'Year 12', 'Year 13']
            init_g = defaults.get("initial_grade", "")
            ig_idx = grade_options.index(init_g) if init_g in grade_options else 0
            initial_grade = st.selectbox("ig_in", grade_options, index=ig_idx, key=f"{form_key}_ig", label_visibility="collapsed")

        st.divider()
        st.markdown("### 第四步：状态与联系人")
        
        cl1, cl2 = st.columns(2)
        with cl1:
            st.markdown("**当前就读状态**")
            # 就读状态伪空白化
            status_options = ["— 请选择就读状态 —"] + STATUS_OPTIONS
            curr_status = defaults.get("status", "")
            stat_idx = status_options.index(curr_status) if curr_status in status_options else 0
            status = st.selectbox("stat_in", status_options, index=stat_idx, key=f"{form_key}_stat", label_visibility="collapsed")
        with cl2:
            st.markdown("**中国紧急联系电话**")
            emergency_phone_cn = st.text_input("phone_in", value=defaults.get("emergency_phone_cn", ""), key=f"{form_key}_phone", placeholder="请输入电话号码", label_visibility="collapsed")

        transfer_note = ""
        if "转学" in status:
            st.markdown("**请注明异地转学去向（具体省份、城市与学校名）**")
            transfer_note = st.text_input("trans_in", value=defaults.get("transfer_note", ""), key=f"{form_key}_trans", placeholder="如：雪兰莪国际学校...", label_visibility="collapsed")

        st.markdown("**大马本地监护人/宿舍信息**")
        guardian_info = st.text_area("guard_in", value=defaults.get("guardian_info", ""), key=f"{form_key}_guard", placeholder="输入宿舍房间号或监护人联系方式...", label_visibility="collapsed")

        btn_label = "确认保存并更新档案" if is_edit else "确认录入并保存档案"
        submitted = st.form_submit_button(btn_label, type="primary", use_container_width=True)

        if submitted:
            # 终极设计者闸门：漏选拦截校验机制
            if not name.strip():
                st.error("拦截：请输入中文姓名！")
                return None
            if gender == "— 请选择性别 —":
                st.error("拦截：请选择学生性别！")
                return None
            if enrollment_year == " " or enrollment_month == " ":
                st.error("拦截：请选择完整的入境大马入学年份与月份！")
                return None
            if school_type == "— 请选择学制 —":
                st.error("拦截：请选择当前所就读的学制！")
                return None
            if initial_grade == "— 请选择年级 —":
                st.error("拦截：请选择入学时的初始年级！")
                return None
            if status == "— 请选择就读状态 —":
                st.error("拦截：请确定该学生的当前在就读状态档案！")
                return None
            if birth_day > calendar.monthrange(birth_year, birth_month)[1]:
                st.error("拦截：请选择有效的出生日期！")
                return None

            b_date = date(birth_year, birth_month, birth_day)

            return {
                "name": name.strip(),
                "pinyin": pinyin.strip().upper(),
                "gender": gender,
                "passport": passport.strip(),
                "birth_date": b_date.isoformat(),
                "departure_city": departure_city.strip(),
                "hobbies": hobbies.strip(),
                "enrollment_year": enrollment_year,
                "enrollment_month": enrollment_month.replace("月", "").strip(),
                "state": selected_state,          
                "city_my": selected_city,        
                "region": f"{selected_state} - {selected_city}", 
                "school_type": school_type,
                "initial_grade": initial_grade,
                "status": status,
                "transfer_note": transfer_note.strip(),
                "emergency_phone_cn": emergency_phone_cn.strip(),
                "guardian_info": guardian_info.strip(),
                "created_by": created_by
            }
    return None