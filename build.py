"""UT 프로토타입 빌드.

index.html(B안 원본)에서
  - index-a.html, index-c.html : A안·C안 원본 (B안과 다른 부분만 치환)
  - A/B/C안_프로토타입.html    : 에셋을 인라인한 단일 파일
  - docs/a|b|c.html            : GitHub Pages 배포본
을 만든다. 실행: python3 build.py
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).parent


def inline_assets(html: str) -> str:
    def rep(m):
        data = (ROOT / 'assets' / m.group(1)).read_bytes()
        return 'data:image/svg+xml;base64,' + base64.b64encode(data).decode()
    out = re.sub(r'assets/([\w-]+\.svg)', rep, html)
    assert 'assets/' not in out
    return out


def replace_once(html: str, old: str, new: str) -> str:
    assert html.count(old) == 1, f'치환 대상이 1개가 아님: {old[:60]}'
    return html.replace(old, new)


TOOLBAR_TIP_CSS = (
    '  .tb-end { display: flex; align-items: center; gap: 8px; }\n'
    '  .tb-dl { position: relative; }\n'
    '  .tb-tip {\n'
    '    position: absolute; bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%);\n'
    '    background: var(--fill-inverse); color: #fff; border-radius: 8px;\n'
    '    padding: 8px 12px; font-size: 12px; font-weight: 500; line-height: 18px; white-space: nowrap;\n'
    '    display: none; z-index: 30; pointer-events: none;\n'
    '  }\n'
    '  .tb-dl:hover .tb-tip { display: block; }\n'
    '  .tb-dl.saving .tb-tip { display: none; }\n'
    '  .tb-dl.saving button { cursor: default; color: var(--typo-disabled); border-color: var(--border-subtle); }\n'
    '  .tb-dl.saving img { opacity: .3; }\n')

VSEP_CSS = '  .vsep { width: 1px; height: 20px; background: var(--fill-surface-raised); }\n'


def add_toolbar_save(html: str, button: str, tip: str, label: str) -> str:
    """'채용 단계 편집' 왼쪽에 현재 공고 저장 버튼(+호버 툴팁)을 넣고 저장 흐름에 연결한다."""
    html = replace_once(
        html,
        '        <button class="btn radius-md" data-log="채용 단계 편집">',
        '        <div class="tb-end">\n'
        '          <div class="tb-dl" id="tbDl">\n'
        f'            {button}\n'
        f'            <div class="tb-tip" role="tooltip">{tip}</div>\n'
        '          </div>\n'
        '        <button class="btn radius-md" data-log="채용 단계 편집">')
    html = replace_once(html, '채용 단계 편집</button>\n', '채용 단계 편집</button>\n        </div>\n')
    html = replace_once(html, VSEP_CSS, VSEP_CSS + TOOLBAR_TIP_CSS)
    html = replace_once(
        html,
        '  // ---- 지원자 선택 & 하단 액션바',
        '  // ---- 툴바 현재 공고 저장 버튼 ----\n'
        '  const tbDl = document.getElementById(\'tbDl\');\n'
        '  tbDl.querySelector(\'button\').addEventListener(\'click\', () => {\n'
        '    if (saving) return;\n'
        f'    startSave(\'current\', \'{label}\');\n'
        '  });\n\n'
        '  // ---- 지원자 선택 & 하단 액션바')
    html = replace_once(
        html,
        "    excelBtn.setAttribute('aria-disabled', 'true');\n",
        "    excelBtn.setAttribute('aria-disabled', 'true');\n"
        "    tbDl.classList.add('saving');\n")
    html = replace_once(
        html,
        "    excelBtn.removeAttribute('aria-disabled');\n",
        "    excelBtn.removeAttribute('aria-disabled');\n"
        "    tbDl.classList.remove('saving');\n")
    return html


def to_variant_a(html: str) -> str:
    html = html.replace('B안 프로토타입', 'A안 프로토타입')

    # '전체 지원자 엑셀 저장' 드롭다운: 진행중/마감만 (현재 공고 항목 없음)
    html = replace_once(
        html,
        '        <button class="dd-item" role="menuitem" data-choice="current" data-log="[엑셀] 현재 공고 지원자">현재 공고 지원자</button>\n'
        '        <div class="dd-sep"></div>\n',
        '')

    # '채용 단계 편집' 좌측 다운로드 아이콘 → 메뉴 없이 바로 현재 공고 저장
    return add_toolbar_save(
        html,
        button='<button class="icon-btn" aria-label="현재 공고 전체 지원자 저장" data-log="[엑셀] 툴바 다운로드 아이콘 (현재 공고)"><img src="assets/download.svg" alt=""></button>',
        tip='현재 공고 전체 지원자 저장',
        label='현재 공고 전체 지원자 (툴바 아이콘)')


def to_variant_c(html: str) -> str:
    """C-2 범위별 분리안 (공고 관리는 변경 없음).

    - 현재 공고 저장: 지원자 목록 툴바의 '엑셀 저장' 텍스트 버튼
    - 전체 공고 저장: 공고 카드 영역('공고' 라벨 줄)의 '공고 전체 지원자 저장' 드롭다운(진행중/마감) + 확인 단계
    """
    html = html.replace('B안 프로토타입', 'C안 프로토타입')

    # 1) 헤더의 '전체 지원자 엑셀 저장'을 떼어 공고 카드 영역 위 '공고' 라벨 줄로 이동
    old_excel = html[html.index('    <div class="excel" id="excel">'):html.index('  </div>\n\n  <div class="postings">')]
    html = replace_once(html, old_excel, '')
    new_excel = (old_excel
        .replace('<button class="btn" id="excelBtn"', '<button class="btn sm" id="excelBtn"')
        .replace('data-log="[엑셀] 전체 지원자 엑셀 저장 버튼"', 'data-log="[엑셀] 공고 영역 \'공고 전체 지원자 저장\' 버튼"')
        .replace('        전체 지원자 엑셀 저장\n', '        공고 전체 지원자 저장\n')
        .replace('        <button class="dd-item" role="menuitem" data-choice="current" data-log="[엑셀] 현재 공고 지원자">현재 공고 지원자</button>\n'
                 '        <div class="dd-sep"></div>\n', '')
        .replace('"[엑셀] 진행중 공고 지원자">진행중 공고 지원자</button>', '"[엑셀] 공고 영역 > 진행중 공고 전체">진행중 공고 전체</button>')
        .replace('"[엑셀] 마감 공고 지원자">마감 공고 지원자</button>', '"[엑셀] 공고 영역 > 마감 공고 전체">마감 공고 전체</button>'))
    html = replace_once(
        html,
        '  <div class="postings">',
        '  <div class="postings-head">\n'
        '    <span class="postings-label">공고 <b>10</b></span>\n'
        + new_excel.replace('\n    ', '\n    ') +
        '  </div>\n'
        '  <div class="postings">')
    html = replace_once(
        html,
        '  .postings { position: relative;',
        '  .postings-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }\n'
        '  .postings-label { font-size: 15px; font-weight: 600; line-height: 22px; color: var(--typo-secondary); }\n'
        '  .postings-label b { color: var(--typo-info); font-weight: 600; margin-left: 2px; }\n'
        '  .postings-head .dropdown { width: 168px; }\n'
        '  .postings { position: relative;')

    # 2) 진행중/마감 선택 시 확인 단계
    html = replace_once(
        html,
        '    setOpen(false);\n    startSave(item.dataset.choice);\n',
        '    setOpen(false);\n    confirmSave(item.dataset.choice);\n')
    html = replace_once(
        html,
        '  function startSave(choice,',
        '  // ---- 전체 공고 저장 확인 단계 (C안 전용) ----\n'
        '  const confirmDim = document.getElementById(\'confirmDim\');\n'
        '  let pendingChoice = null;\n'
        '  function confirmSave(choice) {\n'
        '    pendingChoice = choice;\n'
        '    const total = JOBS.reduce((sum, j) => sum + j.counts[0], 0);\n'
        '    document.getElementById(\'confirmMsg\').textContent = choice === \'ongoing\'\n'
        '      ? `진행중 공고 ${JOBS.length}개의 지원자 ${total}명을 엑셀로 저장할까요?`\n'
        '      : \'마감 공고 38개의 지원자를 엑셀로 저장할까요?\';\n'
        '    confirmDim.classList.add(\'show\');\n'
        '  }\n'
        '  document.getElementById(\'confirmCancel\').addEventListener(\'click\', () => confirmDim.classList.remove(\'show\'));\n'
        '  document.getElementById(\'confirmOk\').addEventListener(\'click\', () => {\n'
        '    confirmDim.classList.remove(\'show\');\n'
        '    startSave(pendingChoice);\n'
        '  });\n\n'
        '  function startSave(choice,')
    html = replace_once(
        html,
        '<div class="toast" id="done"',
        '<div class="confirm-dim" id="confirmDim" role="dialog" aria-modal="true" aria-labelledby="confirmMsg">\n'
        '  <div class="confirm">\n'
        '    <p class="confirm-msg" id="confirmMsg"></p>\n'
        '    <p class="confirm-sub">공고와 지원자가 많으면 파일 생성에 시간이 걸릴 수 있어요.</p>\n'
        '    <div class="confirm-btns">\n'
        '      <button class="btn" id="confirmCancel" data-log="[확인 단계] 취소">취소</button>\n'
        '      <button class="btn primary" id="confirmOk" data-log="[확인 단계] 저장">저장</button>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n\n'
        '<div class="toast" id="done"')
    html = replace_once(
        html,
        '  /* Done toast */',
        '  /* 전체 공고 저장 확인 */\n'
        '  .confirm-dim { position: fixed; inset: 0; z-index: 70; background: rgba(19,22,24,.4); display: none; align-items: center; justify-content: center; }\n'
        '  .confirm-dim.show { display: flex; }\n'
        '  .confirm { width: 400px; padding: 28px 24px 20px; border-radius: 16px; background: #fff; box-shadow: var(--shadow-lg); }\n'
        '  .confirm-msg { font-size: 17px; font-weight: 700; line-height: 26px; }\n'
        '  .confirm-sub { margin-top: 8px; font-size: 14px; line-height: 20px; color: var(--typo-subtle); }\n'
        '  .confirm-btns { display: flex; justify-content: flex-end; gap: 8px; margin-top: 24px; }\n\n'
        '  /* Done toast */')

    # 3) 툴바에 범위가 드러나는 '엑셀 저장' 텍스트 버튼 (현재 공고)
    html = add_toolbar_save(
        html,
        button='<button class="btn radius-md" data-log="[엑셀] 툴바 \'엑셀 저장\' 버튼 (현재 공고)"><img class="ic16" src="assets/download.svg" alt="">엑셀 저장</button>',
        tip='이 공고의 모든 단계 지원자를 엑셀로 저장해요',
        label='현재 공고 전체 지원자 (툴바 \\\'엑셀 저장\\\' 버튼)')

    # 4) 액션바 '다운로드' → 받는 파일이 드러나는 이름
    html = replace_once(html, '</svg></span>다운로드</button>', '</svg></span>엑셀·이력서</button>')
    html = replace_once(
        html,
        '  .ab-dl { position: relative; }\n',
        '  .ab-dl { position: relative; }\n'
        '  .ab-dl .ab-btn { width: auto; min-width: 48px; }\n')

    # 5) 진행자 로그 라벨
    html = replace_once(
        html,
        "  const CHOICE_LABEL = { current: '현재 공고 지원자', ongoing: '진행중 공고 지원자', closed: '마감 공고 지원자' };",
        "  const CHOICE_LABEL = { current: '현재 공고 지원자', ongoing: '진행중 공고 전체 지원자 (공고 영역)', closed: '마감 공고 전체 지원자 (공고 영역)' };")
    # 초기화 시 확인 창도 닫기
    html = replace_once(html, '    clearSelection();\n    entries = [];', '    clearSelection();\n    confirmDim.classList.remove(\'show\');\n    entries = [];')
    return html


def main():
    b_src = (ROOT / 'index.html').read_text()
    a_src = to_variant_a(b_src)
    c_src = to_variant_c(b_src)
    (ROOT / 'index-a.html').write_text(a_src)
    (ROOT / 'index-c.html').write_text(c_src)

    docs = ROOT / 'docs'
    docs.mkdir(exist_ok=True)
    for name, src in (('A', a_src), ('B', b_src), ('C', c_src)):
        out = inline_assets(src)
        (ROOT / f'{name}안_프로토타입.html').write_text(out)
        # GitHub Pages 배포본 (docs/): 영문 파일명으로 링크가 깨지지 않게
        (docs / f'{name.lower()}.html').write_text(out)
    print('built: A/B/C안_프로토타입.html, index-a.html, index-c.html, docs/a|b|c.html')


if __name__ == '__main__':
    main()
