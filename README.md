# stt-shortcut

iPhone/iPad/Mac에서 음성을 녹음하고 STT API로 텍스트 변환하여 클립보드에 복사하는 Apple 단축어 생성기.

iPhone 뒷면 탭으로 실행하면 어디서든 음성 받아쓰기를 할 수 있습니다.

## 기능

1. 음성 녹음 (즉시 시작, 고음질)
2. Groq Whisper API로 한국어 음성 인식
3. 인식된 텍스트를 클립보드에 복사
4. 알림으로 결과 표시

## 사전 준비

[Groq](https://console.groq.com)에서 무료 API 키를 발급받으세요. (신용카드 불필요)

## 사용법

```bash
python3 generate_stt_shortcut.py YOUR_GROQ_API_KEY
```

현재 디렉토리에 `음성받아쓰기.shortcut` 파일이 생성됩니다.

## 설치

- **Mac**: 생성된 `.shortcut` 파일을 더블클릭하면 단축어 앱에 추가됩니다.
- **iPhone/iPad**: AirDrop으로 전송하거나 iCloud Drive를 통해 열어주세요.

> 단축어를 추가할 때 API 키 입력 팝업이 표시됩니다. 다른 사람에게 공유할 때는 각자 자신의 API 키를 입력하면 됩니다.

## iPhone 뒷면 탭 설정

**설정** > **손쉬운 사용** > **터치** > **뒷면 탭** > **이중 탭** > `음성받아쓰기` 선택

이제 iPhone 뒷면을 두 번 탭하면 바로 음성 받아쓰기가 시작됩니다.

## 커스터마이징

스크립트의 `generate_shortcut()` 함수에서 다음 값을 변경할 수 있습니다:

| 항목 | 기본값 | 설명 |
|------|--------|------|
| API URL | `api.groq.com/.../transcriptions` | OpenAI-compatible STT API 엔드포인트 |
| model | `whisper-large-v3` | 사용할 STT 모델 |
| language | `ko` | 인식 언어 ([ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)) |
| WFRecordingCompression | `Lossless` | 녹음 품질 (`Lossless` / `Normal`) |

OpenAI-compatible API를 제공하는 다른 서비스(OpenAI, Fireworks, Together 등)로도 교체할 수 있습니다.
