
# Gemini Streamlit Chatbot 🤖

Google의 강력한 Gemini 모델을 활용하는 고도로 사용자 정의 가능한 웹 기반 챗봇 인터페이스입니다. Streamlit을 사용하여 제작되었으며, 텍스트 및 이미지(멀티모달) 입력을 지원하고 모델의 거의 모든 파라미터를 실시간으로 조정할 수 있는 기능을 제공합니다.


## ✨ 주요 기능

-   💬 **인터랙티브 채팅 인터페이스**: 실시간 스트리밍 응답을 지원하는 직관적인 채팅 UI.
-   📸 **멀티모달 입력**: 텍스트뿐만 아니라 이미지 파일을 첨부하여 질문할 수 있습니다.
-   🔧 **세밀한 모델 설정**:
    -   API 키 및 Gemini 모델(`gemini-2.5-flash` 등) 선택 기능. AI스튜디오를 통해 발급받은 Free tier aPI key라면 가급적 flash 모델을 이용하는는 걸 추천.
    -   `Temperature`, `Top-P`, `Top-K`, `Max Output Tokens` 등 주요 파라미터 조정.
    -   **시스템 프롬프트**를 직접 편집하여 AI의 역할과 행동을 정의.
    -   콘텐츠 안전성(Safety Settings) 등급을 상세하게 설정.
-   🎨 **UI 커스터마이징**:
    -   사용자와 AI의 아바타를 원하는 이미지로 변경.
    -   채팅창의 아바타 크기를 슬라이더로 조절.
-   📜 **대화 로그 관리**:
    -   **텍스트 로그**: 전체 대화 내용을 확인하고, 특정 메시지를 수정하거나 삭제하여 대화의 흐름을 제어.
    -   **LLM 원본 로그**: 디버깅을 위해 모델과 주고받은 실제 요청/응답(JSON)을 확인.
    -   모든 로그(텍스트, 원본)를 파일로 다운로드.
-   🚀 **업데이트 로그 표시**: `CHANGELOG.md` 파일을 앱 내에서 직접 확인하여 최신 변경 사항을 쉽게 파악.

## 📁 파일 구조

```
.
├── CHANGELOG.md      # 앱 내에서 보여주는 업데이트 내역
├── README.md         # 현재 보고 있는 파일
├── main.py           # Streamlit 앱 메인 코드
└── requirements.txt  # 필요한 파이썬 라이브러리 목록
```

## 🚀 시작하기

### 사전 준비 사항

-   Python 3.9 이상
-   [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받은 Gemini API 키. 아직 버텍스는 대응 X.

### 설치 및 실행 방법

1.  **저장소 복제:**
    ```bash
    git clone https://github.com/HisameOgasahara/gemini_streamlit_chatbot.git
    cd gemini_streamlit_chatbot
    ```

2.  **가상 환경 생성 및 활성화 (권장):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **필요한 라이브러리 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Streamlit 앱 실행:**
    ```bash
    streamlit run main.py
    ```

5.  **API 키 설정:**
    -   웹 앱이 실행되면 `⚙️ 모델 설정` 탭으로 이동합니다.
    -   'Google AI Studio API Key' 입력란에 발급받은 API 키를 붙여넣고 `API 키 적용` 버튼을 클릭합니다.

이제 `💬 채팅` 탭으로 돌아가 Gemini 챗봇 사용을 시작할 수 있습니다!

## 📖 사용 방법

-   **💬 채팅**: 메인 채팅 화면입니다. 하단의 입력창에 메시지를 입력하고, 사이드바의 파일 업로더를 통해 이미지를 첨부할 수 있습니다. `스트리밍 응답` 토글로 실시간 답변 여부를 선택하세요.
-   **⚙️ 모델 설정**: API 키, 모델 종류, 시스템 프롬프트, Temperature 등 모델의 동작을 제어하는 모든 설정을 변경할 수 있습니다. 변경 후 `설정 저장 및 채팅 초기화`를 누르면 새 설정으로 채팅이 시작됩니다.
-   **📜 로그**:
    -   `텍스트 로그`: 지금까지의 대화 내용을 확인, 수정, 삭제할 수 있습니다. 대화 내용을 다운로드할 수도 있습니다.
    -   `LLM 원본 로그`: 디버깅을 위해 API와 주고받은 상세한 JSON 데이터를 확인할 수 있습니다.
-   **🎨 UI 조정**: 채팅창에 표시될 사용자 및 AI 아바타를 원하는 이미지로 바꾸거나 크기를 조절할 수 있습니다.

## 📝 변경 기록 (Changelog)

본 프로젝트는 `CHANGELOG.md` 파일을 통해 업데이트 내역을 관리합니다. 이 파일은 앱 내의 '🚀 업데이트 로그' 섹션에서 직접 렌더링되므로, 별도로 열어볼 필요 없이 앱을 실행하여 최신 변경 사항을 확인할 수 있습니다.

자세한 전체 변경 이력은 [CHANGELOG.md](CHANGELOG.md) 파일에서 직접 확인하실 수도 있습니다.