"""UT 프로토타입 빌드.

index.html(B안 원본)에서
  - B안_프로토타입.html : 에셋을 인라인한 단일 파일
  - index-a.html        : A안 원본 (B안과 다른 부분만 치환)
  - A안_프로토타입.html : A안 단일 파일
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


def to_variant_a(html: str) -> str:
    # 제목
    html = html.replace('B안 프로토타입', 'A안 프로토타입')

    # 1) '전체 지원자 엑셀 저장' 드롭다운: 진행중/마감만 (현재 공고 항목 없음)
    html = replace_once(
        html,
        '        <button class="dd-item" role="menuitem" data-choice="current" data-log="[엑셀] 현재 공고 지원자">현재 공고 지원자</button>\n'
        '        <div class="dd-sep"></div>\n',
        '')

    # 2) '채용 단계 편집' 좌측 다운로드 아이콘 + 호버 툴팁
    html = replace_once(
        html,
        '        <button class="btn radius-md" data-log="채용 단계 편집">',
        '        <div class="tb-end">\n'
        '          <div class="tb-dl" id="tbDl">\n'
        '            <button class="icon-btn" id="tbDlBtn" aria-label="현재 공고 전체 지원자 저장" data-log="[엑셀] 툴바 다운로드 아이콘 (현재 공고)"><img src="assets/download.svg" alt=""></button>\n'
        '            <div class="tb-tip" role="tooltip">현재 공고 전체 지원자 저장</div>\n'
        '          </div>\n'
        '        <button class="btn radius-md" data-log="채용 단계 편집">')
    html = replace_once(
        html,
        '채용 단계 편집</button>\n',
        '채용 단계 편집</button>\n        </div>\n')

    html = replace_once(
        html,
        '  .vsep { width: 1px; height: 20px; background: var(--fill-surface-raised); }\n',
        '  .vsep { width: 1px; height: 20px; background: var(--fill-surface-raised); }\n'
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
        '  .tb-dl.saving .icon-btn { cursor: default; }\n'
        '  .tb-dl.saving .icon-btn img { opacity: .3; }\n')

    # 아이콘 클릭 → 메뉴 없이 바로 현재 공고 전체 지원자 저장
    html = replace_once(
        html,
        '  // ---- 지원자 선택 & 하단 액션바',
        '  // ---- 툴바 다운로드 아이콘 (A안 전용) ----\n'
        '  const tbDl = document.getElementById(\'tbDl\');\n'
        '  document.getElementById(\'tbDlBtn\').addEventListener(\'click\', () => {\n'
        '    if (saving) return;\n'
        '    startSave(\'current\', \'현재 공고 전체 지원자 (툴바 아이콘)\');\n'
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


def main():
    b_src = (ROOT / 'index.html').read_text()
    a_src = to_variant_a(b_src)
    (ROOT / 'index-a.html').write_text(a_src)
    a_out, b_out = inline_assets(a_src), inline_assets(b_src)
    (ROOT / 'B안_프로토타입.html').write_text(b_out)
    (ROOT / 'A안_프로토타입.html').write_text(a_out)

    # GitHub Pages 배포본 (docs/): 영문 파일명으로 링크가 깨지지 않게
    docs = ROOT / 'docs'
    docs.mkdir(exist_ok=True)
    (docs / 'a.html').write_text(a_out)
    (docs / 'b.html').write_text(b_out)
    print('built: B안_프로토타입.html, index-a.html, A안_프로토타입.html, docs/a.html, docs/b.html')


if __name__ == '__main__':
    main()
