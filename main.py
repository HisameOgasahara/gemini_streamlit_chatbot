import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import json
from datetime import datetime
from google.generativeai.types import GenerateContentResponse, HarmCategory, HarmBlockThreshold
import base64
import streamlit as st
from pathlib import Path  # 경로 관리를 위해 pathlib 추가

# ----------------------------------------------------------------------
# 초기 설정 및 세션 상태 초기화
# ----------------------------------------------------------------------
def initialize_session_state():
    """세션 상태를 초기화하는 함수"""
    # 기본 정보
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "model_name" not in st.session_state:
        st.session_state.model_name = "gemini-1.5-pro-latest"
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None
    if "history" not in st.session_state:
        st.session_state.history = []
    
    # 모델 설정
    if "system_instruction" not in st.session_state:
        st.session_state.system_instruction = "You are a helpful and friendly AI assistant. Please respond in Korean."
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    if "top_p" not in st.session_state:
        st.session_state.top_p = 1.0
    if "top_k" not in st.session_state:
        st.session_state.top_k = 40
    if "max_output_tokens" not in st.session_state:
        st.session_state.max_output_tokens = 2048
        
    if "safety_settings" not in st.session_state:
        st.session_state.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
    # [변경점] UI 설정에 아바타 정보 추가
    if "ui_settings" not in st.session_state:
        st.session_state.ui_settings = {
            "user_avatar": "🧑‍💻",  # 기본값: 이모지
            "ai_avatar": "🤖",
            "avatar_size": 40 # px 단위
        }
        
    # 로그
    if "raw_logs" not in st.session_state:
        st.session_state.raw_logs = []

# ----------------------------------------------------------------------
# Gemini 모델 관련 함수
# (이전과 동일)
# ----------------------------------------------------------------------
def configure_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"API 키 설정에 실패했습니다: {e}")
        return False

def get_gemini_model():
    if not st.session_state.api_key:
        st.error("모델을 초기화하기 전에 API 키를 설정해주세요.")
        return False

    generation_config = {
        "temperature": st.session_state.temperature,
        "top_p": st.session_state.top_p,
        "top_k": st.session_state.top_k,
        "max_output_tokens": st.session_state.max_output_tokens,
    }
    
    try:
        model = genai.GenerativeModel(
            model_name=st.session_state.model_name,
            generation_config=generation_config,
            system_instruction=st.session_state.system_instruction,
            safety_settings=st.session_state.safety_settings
        )
        
        st.session_state.chat_session = model.start_chat(
            history=st.session_state.history
        )
        return True
    except Exception as e:
        st.error(f"모델 초기화에 실패했습니다: {e}")
        return False

# ----------------------------------------------------------------------
# Helper 함수
# ----------------------------------------------------------------------
def response_to_dict(response: GenerateContentResponse) -> dict:
    """GenerateContentResponse 객체를 JSON 직렬화 가능한 딕셔너리로 변환 (상세 정보 포함)"""
    def get_parts_list(parts):
        # ... (이전과 동일)
        return []

    candidates_list = []
    if response and response.candidates:
        for candidate in response.candidates:
            candidates_list.append({
                "content": {"parts": [{"type": "text", "content": part.text} for part in candidate.content.parts], "role": candidate.content.role},
                "finish_reason": candidate.finish_reason.name if candidate.finish_reason else "UNKNOWN",
                "safety_ratings": {rating.category.name: rating.probability.name for rating in candidate.safety_ratings},
                "token_count": candidate.token_count
            })

    usage_metadata = {}
    if response and hasattr(response, 'usage_metadata'):
        usage_metadata = {
            "prompt_token_count": response.usage_metadata.prompt_token_count,
            "candidates_token_count": response.usage_metadata.candidates_token_count,
            "total_token_count": response.usage_metadata.total_token_count
        }

    prompt_feedback = {}
    if response and hasattr(response, 'prompt_feedback'):
        prompt_feedback = {
            "block_reason": response.prompt_feedback.block_reason.name if response.prompt_feedback.block_reason else "NONE",
            "safety_ratings": {rating.category.name: rating.probability.name for rating in response.prompt_feedback.safety_ratings}
        }

    return {
        "candidates": candidates_list,
        "prompt_feedback": prompt_feedback,
        "usage_metadata": usage_metadata
    }

def image_to_base64(image_file):
    """UploadedFile 객체를 Base64 데이터 URI로 변환"""
    img_bytes = image_file.getvalue()
    base64_encoded = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{base64_encoded}"

# [변경점 1] 로그 파일을 읽고 캐싱하는 함수 추가
@st.cache_data
def load_changelog():
    """CHANGELOG.md 파일을 읽어 그 내용을 반환합니다."""
    # Path 객체를 사용하여 파일 경로를 안전하게 처리
    changelog_path = Path(__file__).parent / "CHANGELOG.md"
    try:
        with changelog_path.open("r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "업데이트 로그 파일을 찾을 수 없습니다."


# ----------------------------------------------------------------------
# 탭 렌더링 함수
# ----------------------------------------------------------------------
def render_chat_tab():
    st.header("💬 Gemini 챗봇")
    
    # 아바타 설정 적용
    user_avatar = st.session_state.ui_settings.get('user_avatar', '🧑‍💻')
    ai_avatar = st.session_state.ui_settings.get('ai_avatar', '🤖')

    for message in st.session_state.history:
        role = "assistant" if message['role'] == 'model' else message['role']
        avatar = ai_avatar if role == 'assistant' else user_avatar
        with st.chat_message(role, avatar=avatar):
            for part in message['parts']:
                if isinstance(part, str):
                    st.markdown(part)
                elif isinstance(part, Image.Image):
                    st.image(part, width=200)

    with st.sidebar:
        st.subheader("질문 입력")
        uploaded_file = st.file_uploader("파일 첨부 (이미지)", type=["png", "jpg", "jpeg"])
        use_streaming = st.toggle("스트리밍 응답", value=True)

    if prompt := st.chat_input("메시지를 입력하세요..."):
        if not st.session_state.api_key:
            st.error("모델 설정 탭에서 API 키를 먼저 입력해주세요.")
            st.stop()

        if st.session_state.chat_session is None:
            if not get_gemini_model():
                st.stop()
        
        user_parts = [prompt]
        if uploaded_file:
            image = Image.open(uploaded_file)
            user_parts.insert(0, image)

        st.session_state.history.append({"role": "user", "parts": user_parts})
        
        with st.chat_message("user", avatar=user_avatar):
            if uploaded_file:
                st.image(image, width=200)
            st.markdown(prompt)

        # ... (이하 AI 응답 처리 로직은 이전과 거의 동일)
        # 로그 기록용 요청 본문 생성
        safety_settings_log = {k.name: v.name for k, v in st.session_state.safety_settings.items()}
        request_body = {
            "model_name": st.session_state.model_name,
            "system_instruction": st.session_state.system_instruction,
            "generation_config": {
                "temperature": st.session_state.temperature, "top_p": st.session_state.top_p,
                "top_k": st.session_state.top_k, "max_output_tokens": st.session_state.max_output_tokens
            },
            "safety_settings": safety_settings_log
        }
        
        try:
            with st.chat_message("assistant", avatar=ai_avatar):
                response_placeholder = st.empty()
                response = st.session_state.chat_session.send_message(user_parts, stream=use_streaming)
                
                final_response_obj = None
                if use_streaming:
                    full_response_text = ""
                    for chunk in response:
                        if chunk.text:
                            full_response_text += chunk.text
                            response_placeholder.markdown(full_response_text + "▌")
                    response_placeholder.markdown(full_response_text)
                    st.session_state.history.append({"role": "model", "parts": [full_response_text]})
                    final_response_obj = response._result
                else:
                    response_placeholder.markdown(response.text)
                    st.session_state.history.append({"role": "model", "parts": [response.text]})
                    final_response_obj = response

            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "request": request_body,
                "response": { "body": response_to_dict(final_response_obj), "success": True }
            }
            st.session_state.raw_logs.append(log_entry)

        except Exception as e:
            st.error(f"메시지 전송 중 오류가 발생했습니다: {e}")
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "request": request_body,
                "response": {"body": str(e), "success": False}
            }
            st.session_state.raw_logs.append(log_entry)

def render_settings_tab():
    # ... (이전과 동일)
    st.header("⚙️ 모델 설정")
    st.subheader("API 키 설정")
    api_key = st.text_input("Google AI Studio API Key", type="password", value=st.session_state.api_key)
    if st.button("API 키 적용"):
        st.session_state.api_key = api_key
        if configure_gemini(api_key):
            st.success("API 키가 성공적으로 설정되었습니다.")
        else:
            st.error("API 키 설정에 실패했습니다. 키를 확인해주세요.")

    st.markdown("---")
    st.subheader("모델 선택")
    if st.session_state.api_key:
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            gemini_models = sorted([m for m in models if 'gemini' in m])
            st.session_state.model_name = st.selectbox(
                "사용할 Gemini 모델을 선택하세요:",
                gemini_models,
                index=gemini_models.index(st.session_state.model_name) if st.session_state.model_name in gemini_models else 0
            )
        except Exception as e:
            st.error(f"모델 목록을 불러오는 데 실패했습니다: {e}")
    else:
        st.warning("API 키를 먼저 입력해주세요.")

    st.markdown("---")
    st.subheader("시스템 프롬프트")
    st.session_state.system_instruction = st.text_area("시스템 프롬프트 설정:", value=st.session_state.system_instruction, height=150)
    
    st.markdown("---")
    st.subheader("모델 파라미터")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.05)
        st.session_state.top_k = st.slider("Top-K", 1, 100, st.session_state.top_k, 1)
    with col2:
        st.session_state.top_p = st.slider("Top-P", 0.0, 1.0, st.session_state.top_p, 0.05)
        st.session_state.max_output_tokens = st.number_input("Max Output Tokens", 1, 8192, st.session_state.max_output_tokens, 64)
    st.markdown("---")
    st.subheader("안전 설정 (Safety Settings)")
    st.info("차단 기준을 낮춥니다 (예: BLOCK_NONE은 거의 차단 안 함).")
    
    threshold_options = [t.name for t in HarmBlockThreshold]
    
    for category in st.session_state.safety_settings:
        current_threshold = st.session_state.safety_settings[category]
        selected_threshold_name = st.selectbox(
            f"{category.name.replace('HARM_CATEGORY_', '')}",
            options=threshold_options,
            index=threshold_options.index(current_threshold.name),
            key=f"safety_{category.name}"
        )
        st.session_state.safety_settings[category] = HarmBlockThreshold[selected_threshold_name]
    if st.button("설정 저장 및 채팅 초기화"):
        if get_gemini_model():
            st.success("설정이 저장되었고, 채팅이 새 설정으로 초기화되었습니다.")

def render_log_tab():
    st.header("📜 로그")
    log_text_tab, log_raw_tab = st.tabs(["텍스트 로그", "LLM 원본 로그"])
    
    with log_text_tab:
        st.info("여기서 메시지를 수정/삭제하면 다음 대화부터 반영됩니다.")
        
        # [변경점] 텍스트 로그 다운로드 버튼
        if st.session_state.history:
            log_str = ""
            for msg in st.session_state.history:
                role = "User" if msg['role'] == 'user' else "AI"
                text_part = next((part for part in msg['parts'] if isinstance(part, str)), "[이미지 또는 파일]")
                log_str += f"[{role}]\n{text_part}\n\n---\n"
            st.download_button(
                label="📥 모든 텍스트 로그 다운로드 (.txt)",
                data=log_str.encode('utf-8'),
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

        history_changed = False
        for i, message in enumerate(list(st.session_state.history)):
            # ... (이전과 동일한 수정/삭제 로직)
            role = "사용자" if message['role'] == 'user' else "AI"
            current_text = next((part for part in message['parts'] if isinstance(part, str)), "")
            with st.expander(f"**{i+1}. {role}:** {current_text[:30]}..."):
                new_text = st.text_area("내용 수정", value=current_text, key=f"edit_log_{i}")
                col1, col2 = st.columns([4, 1])
                with col1:
                    if new_text != current_text:
                        text_part_index = -1
                        for idx, part in enumerate(message['parts']):
                            if isinstance(part, str): text_part_index = idx; break
                        if text_part_index != -1: st.session_state.history[i]['parts'][text_part_index] = new_text
                        else: st.session_state.history[i]['parts'].append(new_text)
                        history_changed = True
                        st.caption("내용이 수정되었습니다. '변경사항 적용'을 눌러주세요.")
                with col2:
                    if st.button("삭제", key=f"delete_log_{i}"):
                        st.session_state.history.pop(i); history_changed = True; st.rerun()

        if history_changed:
            if st.button("변경사항 적용 및 채팅 세션 재시작"):
                if get_gemini_model():
                    st.success("변경사항이 적용되었습니다.")
                st.rerun()
                
    with log_raw_tab:
        st.info("개발자 디버깅을 위한 LLM과의 실제 통신 기록입니다.")
        
        # [변경점] 원본 로그 다운로드 버튼
        if st.session_state.raw_logs:
            col1, col2 = st.columns(2)
            with col1:
                file_type = st.selectbox("다운로드 파일 형식 선택", ["json", "txt"])
            
            log_data_str = json.dumps(st.session_state.raw_logs, indent=2, ensure_ascii=False)
            file_name = f"raw_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_type}"
            
            with col2:
                st.download_button(
                    label=f"📥 모든 원본 로그 다운로드 (.{file_type})",
                    data=log_data_str,
                    file_name=file_name,
                    mime="application/json" if file_type == "json" else "text/plain",
                    key="download-raw-logs"
                )
        
        if not st.session_state.raw_logs:
            st.write("아직 기록된 로그가 없습니다.")
        else:
            for i, log in enumerate(reversed(st.session_state.raw_logs)):
                # ... (이전과 동일한 로그 표시 로직)
                with st.expander(f"**Log #{len(st.session_state.raw_logs) - i} | {log['timestamp']}**"):
                    st.markdown("#### Request"); st.json(log.get('request', {}), expanded=False)
                    st.markdown("---")
                    st.markdown("#### Response")
                    if log.get('response', {}).get('success', False):
                        st.json(log['response']['body'])
                    else:
                        st.code(log.get('response', {}).get('body', 'No response body.'), language='text')

def render_ui_tab():
    st.header("🎨 UI 조정")
    
    # [변경점] 아바타 크기 및 이미지 업로드 UI
    st.subheader("아바타 설정")
    
    # 크기 조절
    st.session_state.ui_settings['avatar_size'] = st.slider(
        "아바타 크기 (px)", min_value=20, max_value=80, 
        value=st.session_state.ui_settings.get('avatar_size', 40)
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write("사용자 아바타")
        user_avatar_file = st.file_uploader("사용자 이미지 업로드", type=['png', 'jpg', 'jpeg'], key='user_avatar_uploader')
        if user_avatar_file:
            st.session_state.ui_settings['user_avatar'] = image_to_base64(user_avatar_file)
            st.image(user_avatar_file, caption="업로드된 사용자 아바타", width=100)
    
    with col2:
        st.write("AI 아바타")
        ai_avatar_file = st.file_uploader("AI 이미지 업로드", type=['png', 'jpg', 'jpeg'], key='ai_avatar_uploader')
        if ai_avatar_file:
            st.session_state.ui_settings['ai_avatar'] = image_to_base64(ai_avatar_file)
            st.image(ai_avatar_file, caption="업로드된 AI 아바타", width=100)

    if st.button("UI 설정 적용 및 새로고침"):
        st.success("UI 설정이 적용되었습니다. 채팅창에 반영됩니다.")
        st.rerun()

# ----------------------------------------------------------------------
# 메인 함수
# ----------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Gemini 챗봇", page_icon="🤖", layout="wide")
    initialize_session_state()
    
    avatar_size = st.session_state.ui_settings.get('avatar_size', 40)
    st.markdown(f"""
    <style>
        [data-testid="stChatMessage"] [data-testid="stAvatar"] img {{
            width: {avatar_size}px;
            height: {avatar_size}px;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # [변경점 2] 하드코딩된 로그 대신 함수 호출로 변경
    with st.expander("🚀 업데이트 로그", expanded=False):
        changelog_content = load_changelog()
        st.markdown(changelog_content, unsafe_allow_html=True) # 마크다운 형식으로 렌더링
        
    chat_tab, settings_tab, log_tab, ui_tab = st.tabs(
        ["💬 채팅", "⚙️ 모델 설정", "📜 로그", "🎨 UI 조정"]
    )
    
    with chat_tab:
        render_chat_tab()
    with settings_tab:
        render_settings_tab()
    with log_tab:
        render_log_tab()
    with ui_tab:
        render_ui_tab()

if __name__ == "__main__":
    main()