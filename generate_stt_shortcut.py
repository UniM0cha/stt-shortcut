#!/usr/bin/env python3
"""
Groq Whisper 한국어 음성 받아쓰기 단축어 생성기

사용법:
    python3 generate_stt_shortcut.py YOUR_GROQ_API_KEY

생성 결과: ~/Desktop/음성받아쓰기.shortcut
  - 더블클릭 → Mac 단축어 앱에 추가
  - AirDrop → iPhone/iPad에 전송
"""

import plistlib
import uuid
import subprocess
import sys
import os


def make_uuid():
    return str(uuid.uuid4()).upper()


def make_attachment(output_uuid, output_name):
    """다른 액션의 출력을 참조하는 변수 (WFTextTokenAttachment)"""
    return {
        'Value': {
            'OutputUUID': output_uuid,
            'Type': 'ActionOutput',
            'OutputName': output_name,
        },
        'WFSerializationType': 'WFTextTokenAttachment',
    }


def make_inline_var(output_uuid, output_name):
    """문자열 내에 변수를 삽입 (WFTextTokenString + \ufffc)"""
    return {
        'Value': {
            'string': '\ufffc',
            'attachmentsByRange': {
                '{0, 1}': {
                    'OutputUUID': output_uuid,
                    'Type': 'ActionOutput',
                    'OutputName': output_name,
                }
            }
        },
        'WFSerializationType': 'WFTextTokenString',
    }


def make_text(s):
    """일반 텍스트 값"""
    return {
        'Value': {'string': s},
        'WFSerializationType': 'WFTextTokenString',
    }


def make_file_field(record_uid):
    """WFItemType=5 파일 필드 (multipart/form-data 트리거)"""
    return {
        'WFItemType': 5,
        'WFKey': make_text('file'),
        'WFValue': {
            'Value': {
                'Value': {
                    'Aggrandizements': [
                        {
                            'CoercionItemClass': 'WFGenericFileContentItem',
                            'Type': 'WFCoercionVariableAggrandizement',
                        }
                    ],
                    'OutputUUID': record_uid,
                    'OutputName': 'Recorded Audio',
                    'Type': 'ActionOutput',
                },
                'WFSerializationType': 'WFTextTokenAttachment',
            },
            'WFSerializationType': 'WFTokenAttachmentParameterState',
        },
    }


def make_bearer_header(text_uid):
    """'Bearer ' + Text 액션 출력을 참조하는 헤더 값"""
    return {
        'Value': {
            'string': 'Bearer \ufffc',
            'attachmentsByRange': {
                '{7, 1}': {
                    'OutputUUID': text_uid,
                    'Type': 'ActionOutput',
                    'OutputName': 'Text',
                }
            }
        },
        'WFSerializationType': 'WFTextTokenString',
    }


def generate_shortcut(api_key):
    # 액션 간 데이터 연결용 UUID
    record_uid = make_uuid()
    text_uid = make_uuid()
    request_uid = make_uuid()
    dict_value_uid = make_uuid()

    shortcut = {
        'WFWorkflowMinimumClientVersionString': '900',
        'WFWorkflowMinimumClientVersion': 900,
        'WFWorkflowClientVersion': '1172.1',
        'WFWorkflowIcon': {
            'WFWorkflowIconStartColor': 463140863,   # 파란색
            'WFWorkflowIconGlyphNumber': 61440,       # 마이크 아이콘
        },
        'WFWorkflowInputContentItemClasses': [
            'WFStringContentItem',
        ],
        'WFWorkflowTypes': ['NCWidget', 'WatchKit'],
        'WFWorkflowImportQuestions': [
            {
                'ActionIndex': 1,
                'Category': 'Parameter',
                'DefaultValue': api_key,
                'ParameterKey': 'WFTextActionText',
                'Text': 'Groq API 키를 입력하세요\nhttps://console.groq.com',
            }
        ],
        'WFWorkflowActions': [

            # ─── [0] 오디오 녹음 (바로 시작, 고음질) ───
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.recordaudio',
                'WFWorkflowActionParameters': {
                    'WFRecordingStart': 'Immediately',
                    'WFRecordingCompression': 'Lossless',
                    'UUID': record_uid,
                }
            },

            # ─── [1] API 키 (Import Question이 이 값을 채움) ───
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.gettext',
                'WFWorkflowActionParameters': {
                    'WFTextActionText': make_text(api_key),
                    'UUID': text_uid,
                }
            },

            # ─── [2] API POST (multipart/form-data) ───
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.downloadurl',
                'WFWorkflowActionParameters': {
                    'Advanced': True,
                    'ShowHeaders': True,
                    'WFURL': 'https://api.groq.com/openai/v1/audio/transcriptions',
                    'WFHTTPMethod': 'POST',
                    'WFHTTPBodyType': 'Form',
                    'WFFormValues': {
                        'Value': {
                            'WFDictionaryFieldValueItems': [
                                {
                                    'WFItemType': 0,
                                    'WFKey': make_text('model'),
                                    'WFValue': make_text('whisper-large-v3'),
                                },
                                {
                                    'WFItemType': 0,
                                    'WFKey': make_text('language'),
                                    'WFValue': make_text('ko'),
                                },
                                make_file_field(record_uid),
                            ]
                        },
                        'WFSerializationType': 'WFDictionaryFieldValue',
                    },
                    'WFHTTPHeaders': {
                        'Value': {
                            'WFDictionaryFieldValueItems': [
                                {
                                    'WFItemType': 0,
                                    'WFKey': make_text('Authorization'),
                                    'WFValue': make_bearer_header(text_uid),
                                },
                                {
                                    'WFItemType': 0,
                                    'WFKey': make_text('Content-Type'),
                                    'WFValue': make_text('multipart/form-data'),
                                },
                            ]
                        },
                        'WFSerializationType': 'WFDictionaryFieldValue',
                    },
                    'UUID': request_uid,
                }
            },

            # ─── [3] JSON에서 "text" 키 추출 ───
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.getvalueforkey',
                'WFWorkflowActionParameters': {
                    'WFInput': make_attachment(request_uid, 'Contents of URL'),
                    'WFDictionaryKey': 'text',
                    'UUID': dict_value_uid,
                }
            },

            # ─── [4] 클립보드에 복사 ───
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.setclipboard',
                'WFWorkflowActionParameters': {
                    'WFInput': make_attachment(dict_value_uid, 'Dictionary Value'),
                }
            },

            # ─── [5] 알림 표시 ───
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.notification',
                'WFWorkflowActionParameters': {
                    'WFNotificationActionBody': make_inline_var(dict_value_uid, 'Dictionary Value'),
                    'WFNotificationActionTitle': '받아쓰기 완료',
                }
            },
        ]
    }

    return shortcut


def main():
    if len(sys.argv) < 2:
        print("사용법: python3 generate_stt_shortcut.py YOUR_GROQ_API_KEY")
        print("Groq API 키 발급: https://console.groq.com")
        sys.exit(1)

    api_key = sys.argv[1]

    # 단축어 plist 생성
    shortcut = generate_shortcut(api_key)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    unsigned_path = '/tmp/stt_shortcut_unsigned.shortcut'
    signed_path = os.path.join(script_dir, '음성받아쓰기.shortcut')

    # 1. unsigned 파일 저장
    with open(unsigned_path, 'wb') as f:
        plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
    print(f"[1/2] Unsigned shortcut 생성 완료: {unsigned_path}")

    # 2. 서명
    result = subprocess.run(
        ['shortcuts', 'sign',
         '--mode', 'anyone',
         '--input', unsigned_path,
         '--output', signed_path],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"[2/2] Signed shortcut 생성 완료: {signed_path}")
        print()
        print("=== 설치 방법 ===")
        print(f"1. 더블클릭: {signed_path}")
        print("   → Mac 단축어 앱에 자동 추가")
        print("2. AirDrop으로 iPhone/iPad에 전송")
        print()
        print("=== 뒷면 탭 설정 (iPhone) ===")
        print("설정 > 손쉬운 사용 > 터치 > 뒷면 탭 > 이중 탭 → '음성받아쓰기' 선택")
    else:
        print(f"서명 실패: {result.stderr}")
        print("unsigned 파일은 생성되었으니 수동으로 서명할 수 있습니다:")
        print(f"  shortcuts sign --mode anyone --input {unsigned_path} --output {signed_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
