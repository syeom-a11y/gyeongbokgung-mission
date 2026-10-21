import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import base64

# ---------------------------------------------------------
# 1. 페이지 설정 및 디자인 스타일 지정
# ---------------------------------------------------------
st.set_page_config(
    page_title="경복궁 산책 미션 스코어보드",
    page_icon="🏯",
    layout="wide"
)

SUBMISSIONS_FILE = "submissions.json"

# ---------------------------------------------------------
# 2. 데이터 저장/불러오기 함수 (공유 파일 방식)
# ---------------------------------------------------------
def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        try:
            with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_submissions(submissions_list):
    try:
        with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(submissions_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"저장 중 오류 발생: {e}")

# ---------------------------------------------------------
# 3. 파일 존재 여부 안전 확인 함수 (대소문자 확장자 대응)
# ---------------------------------------------------------
def get_existing_image_path(base_name):
    for ext in [".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG"]:
        full_path = f"{base_name}{ext}"
        if os.path.exists(full_path):
            return full_path
    return None

# ---------------------------------------------------------
# 4. 데이터 초기화
# ---------------------------------------------------------
TEAMS = ["훈조", "민조", "정조", "음조"]

MISSIONS = {
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (1번)": 20,
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (2번)": 20,
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (3번)": 20,
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (4번)": 20,
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (5번)": 20,
    "🏃‍♂️ 경회루 배경으로 7명 전원 점프샷": 50,
    "🎭 드라마 한 장면 재현": 50,
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (1회차)": 10,
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (2회차)": 10,
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (3회차)": 10,
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (4회차)": 10,
    "🪷 향원정 베스트 뷰 포인트 사진": 10
}

MISSION_DESCRIPTIONS = {
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (1번)": "📷 **[조건]** 아래 가이드 사진 속 장소를 경복궁 내에서 직접 찾아, 구도를 똑같이 맞춰 7명 전원이 나오게 촬영해 주세요!",
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (2번)": "📷 **[조건]** 아래 가이드 사진 속 장소를 경복궁 내에서 직접 찾아, 구도를 똑같이 맞춰 7명 전원이 나오게 촬영해 주세요!",
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (3번)": "📷 **[조건]** 아래 가이드 사진 속 장소를 경복궁 내에서 직접 찾아, 구도를 똑같이 맞춰 7명 전원이 나오게 촬영해 주세요!",
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (4번)": "📷 **[조건]** 아래 가이드 사진 속 장소를 경복궁 내에서 직접 찾아, 구도를 똑같이 맞춰 7명 전원이 나오게 촬영해 주세요!",
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (5번)": "📷 **[조건]** 아래 가이드 사진 속 장소를 경복궁 내에서 직접 찾아, 구도를 똑같이 맞춰 7명 전원이 나오게 촬영해 주세요!",
    "🏃‍♂️ 경회루 배경으로 7명 전원 점프샷": "📷 **[조건]** 아름다운 경회루를 배경으로 조원 7명 전원의 발이 공중에 번쩍 떠 있는 찰나를 남겨주세요!(전원 다 땅에서 발 떨어져야 인정)",
    "🎭 드라마 한 장면 재현": "📷 **[조건]** 한 명은 난간(월대) 위에서 '왕'처럼 서고, 나머지 6명은 아래 마당에서 '신하'처럼 만세를 하세요!",
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (1회차)": "💡 **[조건]** 근정전 난간의 12지신 중 본인 띠 석상과 단둘이 촬영! (개/돼지띠는 해태 석상과 촬영, 띠 중복은 인정 안됨)\n🔗 [💡 십이지상 위치 및 참고 가이드 보기](https://blog.naver.com/roadgrapher_rilla/223718165750)",
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (2회차)": "💡 **[조건]** 근정전 난간의 12지신 중 본인 띠 석상과 단둘이 촬영! (개/돼지띠는 해태 석상과 촬영, 띠 중복은 인정 안됨)\n🔗 [💡 십이지상 위치 및 참고 가이드 보기](https://blog.naver.com/roadgrapher_rilla/223718165750)",
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (3회차)": "💡 **[조건]** 근정전 난간의 12지신 중 본인 띠 석상과 단둘이 촬영! (개/돼지띠는 해태 석상과 촬영, 띠 중복은 인정 안됨)\n🔗 [💡 십이지상 위치 및 참고 가이드 보기](https://blog.naver.com/roadgrapher_rilla/223718165750)",
    "🐉 내 띠 동물(또는 해태) 석상 찾기 (4회차)": "💡 **[조건]** 근정전 난간의 12지신 중 본인 띠 석상과 단둘이 촬영! (개/돼지띠는 해태 석상과 촬영, 띠 중복은 인정 안됨)\n🔗 [💡 십이지상 위치 및 참고 가이드 보기](https://blog.naver.com/roadgrapher_rilla/223718165750)",
    "🪷 향원정 베스트 뷰 포인트 사진": "📷 **[조건]** 경복궁의 아름다운 향원정과 연못이 가장 돋보이는 뷰 포인트에서 조원 7명 전원이 나와 촬영해 주세요."
}

MISSION_IMAGES = {
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (1번)": [("IMG_6862", "📸 장소 1번")],
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (2번)": [("IMG_6863", "📸 장소 2번")],
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (3번)": [("IMG_6864", "📸 장소 3번")],
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (4번)": [("IMG_6865", "📸 장소 4번")],
    "📍 [장소 찾기] 지정된 장소/건물 사진 보고 똑같이 찍기 (5번)": [("IMG_6866", "📸 장소 5번")],
    "🏃‍♂️ 경회루 배경으로 7명 전원 점프샷": [("IMG_6867", "📸 경회루 점프샷 예시")],
    "🎭 드라마 한 장면 재현": [
        ("IMG_6868", "📸 사극 패러디 예시 1"),
        ("IMG_6869", "📸 사극 패러디 예시 2"),
        ("IMG_6870", "📸 사극 패러디 예시 3")
    ],
    "🪷 향원정 베스트 뷰 포인트 사진": [("IMG_6871", "📸 향원정 베스트 뷰 예시")]
}

# ---------------------------------------------------------
# 5. 메인 레이아웃 및 헤더
# ---------------------------------------------------------
st.title("🏯 경복궁 팀 미션 스코어보드")
st.markdown("""
**[공통 필수 규칙]** 
모든 미션 인증 사진에는 **7명 팀원 전원**이 나와야 인정됩니다. (단, **내 띠 동물 미션만 해당 띠 팀원 1명 + 석상 촬영**)
""")

# 새로고침 버튼 제공
if st.button("🔄 실시간 점수 새로고침"):
    st.rerun()

st.divider()

# ---------------------------------------------------------
# 6. 탭 구성
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 실시간 스코어보드", 
    "📸 미션 사진 제출", 
    "🖼️ 전체 제출 현황", 
    "📜 전체 미션 안내"
])

submissions = load_submissions()

# ---------------------------------------------------------
# TAB 1: 실시간 스코어보드
# ---------------------------------------------------------
with tab1:
    st.subheader("🏆 조별 실시간 순위 및 점수")
    
    scores = {team: 0 for team in TEAMS}
    completed_missions = {team: {} for team in TEAMS}
    
    for sub in submissions:
        scores[sub["team"]] += sub["score"]
        completed_missions[sub["team"]][sub["mission"]] = sub["score"]
    
    score_df = pd.DataFrame(list(scores.items()), columns=["팀명", "총 점수 (만점 250점)"])
    score_df = score_df.sort_values(by="총 점수 (만점 250점)", ascending=False).reset_index(drop=True)
    score_df.index = [f"{i+1}위" for i in range(len(score_df))]
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for idx, row in score_df.iterrows():
        rank = int(idx.replace("위", "")) - 1
        with cols[rank]:
            st.metric(label=f"{row['팀명']}", value=f"{row['총 점수 (만점 250점)']} 점")

    st.divider()
    
    st.subheader("📋 조별 상세 미션 달성 현황")
    st.caption("✅ 완료한 미션은 획득 점수가 표시되고, 미완료 미션은 - 로 표시됩니다.")
    
    detail_data = []
    for mission_name, max_score in MISSIONS.items():
        row = {"미션 항목": mission_name, "배점": f"{max_score}점"}
        for team in TEAMS:
            if mission_name in completed_missions[team]:
                row[team] = f"✅ 완료 ({completed_missions[team][mission_name]}점)"
            else:
                row[team] = "-"
        detail_data.append(row)
        
    detail_df = pd.DataFrame(detail_data)
    st.dataframe(detail_df, use_container_width=True, height=450)

# ---------------------------------------------------------
# TAB 2: 미션 사진 제출
# ---------------------------------------------------------
with tab2:
    st.subheader("📸 미션 인증 사진 업로드")
    
    selected_team = st.selectbox("조를 선택하세요", TEAMS)
    selected_mission = st.selectbox("수행한 미션을 선택하세요", list(MISSIONS.keys()))
    
    mission_score = MISSIONS[selected_mission]
    st.write(f"🎯 **획득 가능 점수**: `{mission_score}점`")
    
    st.info(MISSION_DESCRIPTIONS[selected_mission])
    
    if selected_mission in MISSION_IMAGES:
        img_list = MISSION_IMAGES[selected_mission]
        for base_img_name, label in img_list:
            found_path = get_existing_image_path(base_img_name)
            if found_path:
                col_img, _ = st.columns([7, 3])
                with col_img:
                    st.image(found_path, caption=label, use_container_width=True)
            else:
                st.warning(f"⚠️ 가이드 이미지 파일('{base_img_name}')을 업로드 폴더에서 찾을 수 없습니다.")

    with st.form("mission_upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("인증 사진을 첨부하세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])
        comment = st.text_input("한 줄 소감 또는 설명 (선택 사항)")
        
        submit_button = st.form_submit_button("미션 인증 제출하기")
        
        if submit_button:
            if uploaded_file is None:
                st.error("사진을 첨부해야 제출이 가능합니다!")
            else:
                already_submitted = any(
                    sub["team"] == selected_team and sub["mission"] == selected_mission 
                    for sub in submissions
                )
                
                if already_submitted:
                    st.warning(f"⚠️ 이미 [{selected_team}]에서 [{selected_mission}] 미션을 제출했습니다!")
                else:
                    # 이미지 파일을 base64 문자열로 인코딩하여 저장
                    file_bytes = uploaded_file.read()
                    encoded_img = base64.b64encode(file_bytes).decode("utf-8")
                    
                    new_sub = {
                        "team": selected_team,
                        "mission": selected_mission,
                        "score": mission_score,
                        "image_base64": encoded_img,
                        "comment": comment,
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
                    submissions.append(new_sub)
                    save_submissions(submissions)
                    st.success(f"🎉 [{selected_team}] [{selected_mission}] 인증 완료! ({mission_score}점 획득)")
                    st.rerun()

# ---------------------------------------------------------
# TAB 3: 전체 제출 현황
# ---------------------------------------------------------
with tab3:
    st.subheader("🖼️ 조별 제출 사진 모아보기")
    
    if len(submissions) == 0:
        st.info("아직 제출된 미션 인증 사진이 없습니다.")
    else:
        for sub in reversed(submissions):
            with st.expander(f"[{sub['time']}] {sub['team']} - {sub['mission']} ({sub['score']}점)", expanded=True):
                col_sub_img, _ = st.columns([7, 3])
                with col_sub_img:
                    if "image_base64" in sub:
                        img_data = base64.b64decode(sub["image_base64"])
                        st.image(img_data, use_container_width=True)
                if sub.get("comment"):
                    st.caption(f"💬 {sub['comment']}")

# ---------------------------------------------------------
# TAB 4: 전체 미션 안내 및 가이드
# ---------------------------------------------------------
with tab4:
    st.subheader("📜 전체 미션 목록 & 상세 수행 규칙")
    st.caption("각 조별로 미션 내용을 숙지하고 경복궁 탐방 중에 인증샷을 촬영해 보세요!")
    
    guide_items = [
        ("📍 1. [장소 찾기] 지정된 장소/건물 찾아 똑같이 찍기", "20점 × 5개 (총 100점)", "팀원 7명 전원 등장 필수", "제공된 가이드 사진 속 5개 장소를 경복궁 안에서 직접 찾아내어 동일한 구도로 촬영해야 합니다.", [
            ("IMG_6862", "📸 장소 1번"),
            ("IMG_6863", "📸 장소 2번"),
            ("IMG_6864", "📸 장소 3번"),
            ("IMG_6865", "📸 장소 4번"),
            ("IMG_6866", "📸 장소 5번")
        ]),
        ("🏃‍♂️ 2. 경회루 배경으로 7명 전원 점프샷", "50점 (1회)", "팀원 7명 전원 등장 필수", "경회루와 연못을 한 화면에 담으며 조원 7명의 발이 동시에 지상에서 떨어져 뛰어오르는 모습을 순간 포착하세요!", [
            ("IMG_6867", "📸 경회루 점프샷 예시")
        ]),
        ("🎭 3. 드라마 한 장면 재현", "50점 (1회)", "팀원 7명 전원 등장 필수", "한 조원이 왕처럼 근정전 난간(월대) 위로 오르고, 나머지 6명의 신하들이 아래에서 사극처럼 만세를 부르는 장면을 연출해 보세요.", [
            ("IMG_6868", "📸 사극 패러디 예시 1"),
            ("IMG_6869", "📸 사극 패러디 예시 2"),
            ("IMG_6870", "📸 사극 패러디 예시 3")
        ]),
        ("🐉 4. 내 띠 동물(또는 해태) 석상 찾기", "10점 × 최대 4회 (총 40점)", "💡 [예외] 해당 띠 팀원 1명 + 석상 2인 촬영", "근정전 난간의 12지신 석상 중 자신의 띠에 해당하는 동물 석상을 찾으세요. (개/돼지띠는 해태 석상) 팀당 최대 4명까지, 해당 띠 주인공과 석상 2인 촬영으로 제출합니다.\n\n🔗 **[💡 십이지상 위치 및 참고 가이드 블로그 보기](https://blog.naver.com/roadgrapher_rilla/223718165750)**", []),
        ("🪷 5. 향원정 베스트 뷰 포인트 사진", "10점 (1회)", "팀원 7명 전원 등장 필수", "향원정과 연못, 다리가 가장 고즈넉하게 어우러지는 베스트 구도를 조원들과 힘을 합쳐 담아 주세요.", [
            ("IMG_6871", "📸 향원정 베스트 뷰 예시")
        ])
    ]
    
    for title, score, rule, desc, imgs in guide_items:
        with st.expander(f"{title} - [{score}]", expanded=True):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(f"**🎯 점수**: `{score}`")
                st.markdown(f"**👥 등장 조건**: `{rule}`")
                
                if imgs:
                    for base_img_name, label in imgs:
                        found_path = get_existing_image_path(base_img_name)
                        if found_path:
                            col_g_img, _ = st.columns([8, 2])
                            with col_g_img:
                                st.image(found_path, caption=label, use_container_width=True)
                        else:
                            st.warning(f"⚠️ 이미지 파일('{base_img_name}') 없음")
            with col_b:
                st.markdown(f"**📖 미션 설명**: {desc}")
