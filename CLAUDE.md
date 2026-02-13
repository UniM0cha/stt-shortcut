# CLAUDE.md

## 프로젝트 개요

**stt-shortcut**은 음성-텍스트 변환(STT)용 Apple 단축어 `.shortcut` 파일을 프로그래밍 방식으로 생성하는 Python 스크립트입니다. 생성된 단축어는 iPhone/iPad/Mac에서 음성을 녹음하고, Groq Whisper API로 텍스트 변환 후, 결과를 클립보드에 복사합니다.

프로젝트의 주 언어(코드 주석, UI 문자열, README): **한국어**.

## 저장소 구조

```
.
├── generate_stt_shortcut.py   # 메인 스크립트 — .shortcut 파일 생성
├── README.md                  # 사용자 문서 (한국어)
├── .gitignore                 # 생성된 *.shortcut 파일 무시
└── CLAUDE.md                  # 이 파일
```

단일 파일 프로젝트로 하위 디렉토리, 테스트, 패키지 관리 도구가 없습니다.

## 기술 스택

- **Python 3** (표준 라이브러리만 사용 — 서드파티 의존성 없음)
- 주요 표준 라이브러리 모듈: `plistlib`, `uuid`, `subprocess`, `sys`, `os`
- **Apple Shortcuts CLI** (`shortcuts sign`) — macOS에서 생성된 단축어 서명에 필요
- **Groq Whisper API** — 외부 STT 서비스 (OpenAI 호환 엔드포인트)

## 실행 방법

```bash
python3 generate_stt_shortcut.py YOUR_GROQ_API_KEY
```

스크립트 디렉토리에 서명된 `음성받아쓰기.shortcut` 파일이 생성됩니다. `shortcuts` CLI가 설치된 macOS 환경이 필요합니다.

## 아키텍처

스크립트는 **빌더 패턴**으로 Apple 단축어 plist를 구성합니다:

1. **헬퍼 함수**들(`make_uuid`, `make_text`, `make_attachment`, `make_inline_var`, `make_file_field`, `make_bearer_header`)이 단축어 액션 파라미터와 액션 간 참조를 위한 데이터 구조를 생성합니다.

2. **`generate_shortcut(api_key)`**가 6개 액션으로 구성된 단축어 파이프라인을 조립합니다:
   - 액션 0: 오디오 녹음 (무손실, 즉시 시작)
   - 액션 1: 텍스트 가져오기 (API 키 저장; 가져오기 질문으로 채워짐)
   - 액션 2: Groq API에 HTTP POST (multipart/form-data로 오디오 파일 전송)
   - 액션 3: JSON 응답에서 `"text"` 키 추출
   - 액션 4: 클립보드에 복사
   - 액션 5: 알림 표시

3. **`main()`**이 단축어를 바이너리 plist로 직렬화한 뒤 `shortcuts sign --mode anyone`으로 서명합니다.

액션들은 UUID로 연결됩니다 — 각 액션의 출력 UUID를 하위 액션들이 참조합니다.

## 주요 컨벤션

- **외부 의존성 없음** — 모든 것이 Python 표준 라이브러리만 사용합니다. `pip` 패키지를 추가하지 마세요.
- **한국어 문자열** — 모든 사용자 대면 텍스트(단축어 이름, 알림, CLI 메시지, 주석)는 한국어입니다. 이 관례를 유지하세요.
- **설정 가능한 파라미터**는 `generate_shortcut()` 내에 인라인으로 존재합니다:
  - API URL: `https://api.groq.com/openai/v1/audio/transcriptions`
  - 모델: `whisper-large-v3`
  - 언어: `ko` (ISO 639-1)
  - 녹음 품질: `Lossless`
- **린팅/포매팅 설정 없음**. 기존 코드 스타일을 따르세요: 간결한 함수, 명확한 변수명, 한국어 독스트링/주석.
- **생성된 `.shortcut` 파일은 gitignore 처리** — 절대 커밋하지 마세요.

## 개발 참고사항

- 테스트, CI/CD, 빌드 시스템이 없습니다. macOS에서 스크립트를 실행하고 생성된 단축어를 가져오기해서 검증합니다.
- `shortcuts sign` 명령은 macOS에서만 동작합니다. 다른 플랫폼에서는 `/tmp/stt_shortcut_unsigned.shortcut`에 unsigned plist가 생성되지만 서명 단계에서 실패합니다.
- Apple 단축어 plist 형식은 공식 문서가 없습니다. 이 스크립트의 데이터 구조는 리버스 엔지니어링으로 파악한 것입니다. 액션 파라미터를 수정할 때 `WFSerializationType`과 `WFItemType` 값을 정확히 유지하세요.
- API 키는 CLI 인수로 전달되며 가져오기 질문의 기본값으로 포함됩니다. 최종 사용자가 단축어 설치 시 자신의 키로 변경할 수 있습니다.
