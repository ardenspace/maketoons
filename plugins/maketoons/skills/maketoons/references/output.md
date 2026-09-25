# 저장

## 로컬 프로젝트

사용자가 선택한 작업 폴더를 `--project`에 전달한다. 플러그인 설치 폴더를 작업 폴더로 쓰지 않는다. 저장 위치가 불분명하면 그 위치만 질문한다. Python 3.9 이상에서 도우미를 사용할 수 있으며 외부 패키지는 필요 없다.

```bash
python3 scripts/save_output.py /absolute/generated.png \
  --project /absolute/user-project --title '월요일 출근' \
  --panels 4 --layout '2x2' --text-mode none --reference-version gangbyul-v1
```

scripts 경로는 스킬 루트 기준이며 실행할 때는 스킬의 절대 경로를 사용한다. 한 장 안의 4컷이면 `--panel`을 주지 않는다. 개별 컷은 전체 컷 수 `--panels 4`와 `--panel 1` 등을 함께 준다. 수정본은 `--revision 1`을 추가한다. 대사는 `--text-mode dialogue`, 효과음 등만 있으면 `--text-mode other`다.

도우미는 실제 이미지 형식에 맞는 확장자를 선택하고 한국 시각으로 이름을 만든다. 기존 파일이 있으면 `_02`부터 붙여 덮어쓰지 않는다. 같은 이름의 `.json`에 저장 시각·기준 버전·컷 수·배치·텍스트 방식을 기록한다. `--record /path/record.json`으로 승인 콘티와 실제 참조 파일 등 추가 기록을 넣을 수 있다. 이 JSON 객체는 sidecar의 `details`에 저장된다.

반환한 image와 record 경로가 실제 존재하는지 확인하고 링크한다. 실패하면 원본을 보존하고 오류를 알린다. 실패를 숨기기 위해 API를 호출하거나 이미지를 재생성하지 않는다.

## 웹·모바일 또는 도우미 실행 불가

환경의 파일·이미지 도구가 제공하는 다운로드 기능을 사용한다. 지원하면 같은 파일명 규칙을 적용한다. 사용자 로컬에 자동 저장했다고 말하지 않는다. 실제 시각을 확인할 수 없으면 시각을 받거나 파일명 적용이 불가능함을 알린다. 가짜 시각을 만들지 않는다.

다운로드한 팀원이 자신의 `makeimgs/outputs/`에 넣을 수 있도록 안내한다. 도우미 없이 저장했다면 JSON 기록 제공 여부를 명확히 한다.
