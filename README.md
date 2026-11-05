# 엑셀 저장 UT 프로토타입 (A안 / B안)

'전체 지원자 엑셀 저장'과 '현재 공고 지원자 엑셀 저장' 구조를 비교하는 UT용 클릭 프로토타입입니다.

- 안내 페이지: https://kijemi-create.github.io/ut-excel-download/
- A안 (현재 구조): https://kijemi-create.github.io/ut-excel-download/a.html
- B안 (드롭다운 통합안): https://kijemi-create.github.io/ut-excel-download/b.html

## 로컬에서 보기

`A안_프로토타입.html` 또는 `B안_프로토타입.html`을 브라우저로 열면 됩니다. 에셋이 모두 포함된 단일 파일입니다.

## 수정하기

1. `index.html`(B안 원본)을 수정합니다. 아이콘은 `assets/`에 있습니다.
2. `python3 build.py`를 실행하면 A안 원본(`index-a.html`), 단일 파일 두 개, 배포본(`docs/a.html`, `docs/b.html`)이 다시 만들어집니다.
3. 커밋 후 푸시하면 GitHub Pages에 반영됩니다.

## 진행자 기능

- `Shift + L`: 클릭 로그 열기/닫기 (첫 클릭, 저장 경로 기록)
- 참가자 교체 시 로그 창의 '초기화 (다음 참가자)'
