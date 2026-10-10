#!/usr/bin/env python3
"""Build a Korean PDF manual without changing the live website or main branch."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
from xml.sax.saxutils import escape
import zipfile

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent
ROOT.mkdir(parents=True, exist_ok=True)
REPO = 'https://github.com/nkh6189-sys/mclab-dgist.github.io'
SITE = 'https://nkh6189-sys.github.io/mclab-dgist.github.io/'
ACTIONS = REPO + '/actions/workflows/deploy.yml'
PAGES = REPO + '/settings/pages'
DATE = '2026-10-10'
PDF_PATH = ROOT / 'MCLab_Data_Update_Guide_KO.pdf'


def probe(url: str) -> dict:
    request = urllib.request.Request(url, headers={'User-Agent': 'MCLab-Documentation-Check/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read(400_000)
            text = data.decode('utf-8', errors='replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
            return {'status': response.status, 'url': response.url,
                    'title': re.sub(r'\s+', ' ', title.group(1)).strip() if title else ''}
    except urllib.error.HTTPError as exc:
        return {'status': exc.code, 'url': url, 'error': str(exc)}
    except Exception as exc:
        return {'status': None, 'url': url, 'error': str(exc)}


status = {
    'checked_at_kst': dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(),
    'website': probe(SITE),
    'installed_folder': probe('https://api.github.com/repos/nkh6189-sys/mclab-dgist.github.io/contents/mclab?ref=main'),
    'scope': 'Documentation-only branch. No changes to main, gh-pages or production deployment settings.'
}
(ROOT / 'verification.json').write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')

regular = Path('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')
bold = Path('/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf')
if not regular.is_file() or not bold.is_file():
    raise RuntimeError('Install fonts-nanum before building the Korean PDF.')
pdfmetrics.registerFont(TTFont('Nanum', str(regular)))
pdfmetrics.registerFont(TTFont('NanumBold', str(bold)))
pdfmetrics.registerFontFamily('Nanum', normal='Nanum', bold='NanumBold', italic='Nanum', boldItalic='NanumBold')

W, H = A4
M = 44
CW = W - M * 2
INK = colors.HexColor('#142A46')
MUTED = colors.HexColor('#56677C')
BLUE = colors.HexColor('#245ED7')
PALE = colors.HexColor('#EFF4FC')
LINE = colors.HexColor('#DCE5F0')
AMBER = colors.HexColor('#FFF3DF')
TEAL = colors.HexColor('#0D726C')
WHITE = colors.white
TOTAL = 12
c = canvas.Canvas(str(PDF_PATH), pagesize=A4, pageCompression=1)
c.setTitle('MCLab 홈페이지 데이터 업데이트 - 초보자용 안내서')
c.setAuthor('DGIST Mobility Control Laboratory')
c.setSubject('학생, 사진, 논문, 과제 정보 업데이트 및 GitHub Pages 확인 절차')
page_no = 0
y = H - 44
page_checks = []


def para_obj(text: str, size: float = 12.0, leading: float = 19.0, color=INK, bold_text=False):
    style = ParagraphStyle('manual', fontName='NanumBold' if bold_text else 'Nanum', fontSize=size,
                           leading=leading, textColor=color, alignment=TA_LEFT,
                           wordWrap='CJK', splitLongWords=True, spaceBefore=0, spaceAfter=0)
    return Paragraph(text, style)


def ensure(height: float) -> None:
    if y - height < 56:
        raise RuntimeError(f'Page {page_no} overflow: y={y:.1f}, height={height:.1f}')


def p(text: str, size=12.0, leading=19.0, gap=8, color=INK, bold_text=False):
    global y
    item = para_obj(text, size, leading, color, bold_text)
    _, height = item.wrap(CW, H)
    ensure(height)
    item.drawOn(c, M, y - height)
    y -= height + gap


def label(text: str):
    p(escape(text), size=12.8, leading=20, gap=8, color=BLUE, bold_text=True)


def step(number: int, title: str, body: str):
    global y
    t = para_obj(escape(title), 12.8, 19.5, INK, True)
    b = para_obj(body, 11.7, 18.1, MUTED)
    width = CW - 42
    _, ht = t.wrap(width, H)
    _, hb = b.wrap(width, H)
    height = max(27, ht + 5 + hb)
    ensure(height)
    c.setFillColor(BLUE)
    c.roundRect(M, y - 26, 26, 26, 7, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('NanumBold', 12)
    c.drawCentredString(M + 13, y - 18.2, str(number))
    t.drawOn(c, M + 42, y - ht)
    b.drawOn(c, M + 42, y - ht - 5 - hb)
    y -= height + 11


def note(title: str, body: str, warn=False):
    global y
    tp = para_obj(escape(title), 12.0, 18.5, INK, True)
    bp = para_obj(body, 11.4, 17.5, MUTED)
    width = CW - 30
    _, ht = tp.wrap(width, H)
    _, hb = bp.wrap(width, H)
    height = ht + hb + 27
    ensure(height)
    c.setFillColor(AMBER if warn else PALE)
    c.roundRect(M, y - height, CW, height, 8, fill=1, stroke=0)
    tp.drawOn(c, M + 15, y - 12 - ht)
    bp.drawOn(c, M + 15, y - 18 - ht - hb)
    y -= height + 11


def code(text: str, size=11.2):
    global y
    lines = text.strip('\n').split('\n')
    widest = max(pdfmetrics.stringWidth(line, 'Nanum', size) for line in lines)
    if widest > CW - 30:
        size *= (CW - 30) / widest
    if size < 9.2:
        raise RuntimeError(f'Code too wide on page {page_no}')
    leading = size * 1.52
    height = len(lines) * leading + 22
    ensure(height)
    c.setFillColor(PALE)
    c.setStrokeColor(LINE)
    c.roundRect(M, y - height, CW, height, 7, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont('Nanum', size)
    baseline = y - 17 - size * 0.2
    for line in lines:
        c.drawString(M + 14, baseline, line)
        baseline -= leading
    y -= height + 11


def table(headers, rows, widths=None, size=10.8):
    global y
    widths = widths or [CW / len(headers)] * len(headers)
    data = [[para_obj(escape(str(a)), size, size * 1.55, INK, True) for a in headers]]
    for row in rows:
        data.append([para_obj(str(a), size, size * 1.55, INK) for a in row])
    t = Table(data, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PALE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), .5, LINE),
    ]))
    _, height = t.wrap(CW, H)
    ensure(height)
    t.drawOn(c, M, y - height)
    y -= height + 11


def url(text: str, target: str):
    p(f'<link href="{escape(target, {chr(34): "&quot;"})}" color="#245ED7">{escape(text)}</link>',
      size=11.0, leading=17.5, gap=12)


def finish():
    if not page_no:
        return
    page_checks.append({'page': page_no, 'content_bottom_y': round(y, 2), 'minimum_y': 56})
    c.setStrokeColor(LINE)
    c.line(M, 43, W - M, 43)
    c.setFont('Nanum', 8.1)
    c.setFillColor(MUTED)
    c.drawString(M, 28, f'MCLab · DGIST  |  {DATE} 작성  |  초보자용 관리 안내')
    c.drawRightString(W - M, 28, f'{page_no} / {TOTAL}')
    c.showPage()


def page(section: str, title: str, subtitle: str):
    global page_no, y
    finish()
    page_no += 1
    c.bookmarkPage(f'page-{page_no}')
    c.addOutlineEntry(f'{page_no:02d}  {title}', f'page-{page_no}', level=0)
    c.setFillColor(BLUE)
    c.setFont('NanumBold', 9)
    c.drawString(M, H - 41, section)
    c.setFillColor(INK)
    c.setFont('NanumBold', 24)
    c.drawString(M, H - 80, title)
    y = H - 99
    p(escape(subtitle), 11.1, 17.5, gap=17, color=MUTED)


# 01: A useful cover, not a blank title page.
page('START HERE  /  01', '홈페이지 데이터 업데이트', '원본 사진 반영 · Teaching 제외 · 폴더 자동 업데이트형 MCLab 홈페이지')
p('처음 사용하는 분도<br/><b>아래 순서만 따라 하면 됩니다.</b>', 23, 34, gap=22)
note('기억할 것은 한 가지입니다.', '<b>정보 파일 수정 → Commit changes로 저장 → Actions 확인 → 홈페이지 새로고침</b><br/>PC에만 저장하거나 Google Sites만 수정하면 새 홈페이지는 바뀌지 않습니다.')
label('방문자가 보는 홈페이지 주소')
url(SITE, SITE)
label('담당자가 내용을 수정하는 관리 주소')
url(REPO, REPO)
folder_status = status['installed_folder']['status']
if folder_status == 404:
    install_text = '확인 시점에 main 브랜치의 mclab 폴더가 아직 없습니다. <b>먼저 2쪽의 최초 설치</b>를 마친 뒤 3쪽부터 따라 하세요.'
elif folder_status == 200:
    install_text = '확인 시점에 main 브랜치의 mclab 폴더가 있습니다. 이미 설치했다면 2쪽은 건너뛰고 3쪽부터 따라 하세요. 실제 새 화면은 10쪽 방법으로 확인합니다.'
else:
    install_text = '현재 설치 폴더 존재 여부를 자동 확인하지 못했습니다. 저장소에서 mclab 폴더가 보이면 3쪽부터, 보이지 않으면 2쪽부터 확인하세요.'
web_code = status['website']['status']
web_text = f'웹주소 확인 결과: HTTP {web_code}. ' if web_code is not None else '웹주소의 접속 결과를 자동 확인하지 못했습니다. '
if web_code == 200:
    web_text += '주소 접속 성공과 새 디자인 설치 완료는 서로 다릅니다.'
else:
    web_text += '아래 주소는 저장소 이름에 따른 기본 공개 주소이며, 실제 공개 상태는 Settings → Pages에서 확인합니다.'
note('현재 상태와 이 안내서의 적용 범위', install_text + '<br/>' + web_text, warn=True)
p('빠르게 찾기: 최초 설치 2쪽 · 폴더 위치 3쪽 · 기존 정보 수정 4쪽 · 새 학생 5쪽 · 사진 6쪽 · 논문 7쪽 · 과제 8쪽 · 소식 9쪽 · 확인 10쪽 · 오류 11쪽', 10.8, 17, gap=0, color=MUTED)

# 02
page('ONE-TIME SETUP  /  02', '최초 설치는 한 번만 합니다', '저장소에 mclab 폴더가 이미 있다면 이 페이지는 건너뛰세요.')
step(1, 'GitHub에 로그인하고 저장소를 엽니다.', '관리 주소에서 <b>Code</b> 탭을 누르고, 왼쪽 브랜치 선택이 <b>main</b>인지 확인합니다.')
step(2, '완성된 ZIP 하나를 그대로 올립니다.', '<b>Add file → Upload files</b>를 누릅니다. 대화에서 받은 <b>MCLab_Original_Photos_No_Teaching.zip</b>을 저장소 최상위에 올립니다. 압축을 풀거나 이름을 바꾸지 않습니다.')
step(3, 'Commit changes를 눌러 저장합니다.', '설명에는 “최초 홈페이지 설치”를 적습니다. 현재 main에 직접 저장하는 항목이 제공되면 선택합니다. 새 브랜치만 허용되면 관리자의 검토와 main 병합이 필요합니다.')
step(4, '설치 결과를 확인합니다.', '<b>Actions → Install and deploy MCLab → 최신 실행</b>을 엽니다. 홈페이지 검사·생성·배포 단계가 실제로 수행되었는지 확인하고, Code에서 <b>mclab</b> 폴더가 생겼는지 봅니다.')
step(5, 'Pages 공개 설정을 확인합니다.', '<b>Settings → Pages</b>에서 아래 값을 확인합니다. 설치·배포가 끝난 뒤 이 화면에 표시되는 공개 주소로 접속합니다.')
code('Source: Deploy from a branch\nBranch: gh-pages\nFolder: /(root)', 11.5)
note('예전 안내서와 다른 부분', '현재 저장소의 설치기는 <b>main에서 자료를 생성하여 gh-pages로 보내는 방식</b>입니다. 이 안내서는 현재 연결된 deploy.yml을 기준으로 합니다. 기존 ZIP이 수정되면 무결성 검사에서 거절될 수 있습니다.', warn=True)

# 03
page('WHERE TO EDIT  /  03', '수정할 폴더부터 찾으세요', 'Code → main → mclab → content 순서로 들어가면 대부분의 자료가 있습니다.')
p('<b>한 사람·한 논문·한 과제마다 폴더 하나</b>를 사용합니다. 폴더 안의 <b>info.txt</b>는 정보 입력지이고, 사진·PDF는 첨부 파일입니다.')
table(['바꾸려는 내용', 'content 아래 폴더', '홈페이지 위치'], [
    ['학생·연구원 이름과 정보', 'people', 'People'],
    ['연구논문·게재 상태', 'publications', 'Publications'],
    ['연구과제·연구기간', 'projects', 'Projects'],
    ['세부 연구 내용·그림', 'research', 'Research'],
    ['연구실 소식', 'news', 'News'],
    ['행사·연구실 사진', 'gallery', '사진 갤러리'],
], [192, 149, CW - 341])
code('mclab/\n  content/\n    people/\n      minhyeong-kim/\n        info.txt\n        photo.jpg', 11.8)
note('어느 브랜치를 수정하나요?', '<b>main = 정보를 수정하는 곳</b><br/><b>gh-pages = 자동으로 만들어진 공개 결과</b><br/>gh-pages, _site, data/site-data.js를 직접 수정하지 마세요. 다음 자동 생성 때 덮어써질 수 있습니다.')
p('작성 도구가 content/people/...로 위치를 표시하더라도, 이 저장소에서는 앞에 <b>mclab/</b>이 붙습니다. Teaching은 제거되었으므로 관리 대상이 아닙니다.', 11.2, 18, color=MUTED)

# 04
page('EDIT EXISTING INFO  /  04', '기존 학생 정보를 수정하기', '예: 연구 분야, 학위과정, 이메일을 바꿀 때. HTML 코드는 수정하지 않습니다.')
step(1, '해당 학생의 info.txt를 엽니다.', '<b>main → mclab → content → people → 학생 폴더 → info.txt</b>를 차례로 클릭합니다.')
step(2, '연필 모양의 Edit 버튼을 누릅니다.', '파일 내용 위의 연필 아이콘을 찾습니다. 편집창이 열리면 <b>항목명과 콜론(:)은 그대로 두고, 오른쪽 값만</b> 수정합니다.')
code('수정 전\n연구분야: Vehicle dynamics\n\n수정 후\n연구분야: Steer-by-Wire and vehicle motion control', 11.3)
step(3, 'Commit changes로 저장합니다.', '“학생 연구분야 수정”처럼 변경 이유를 짧게 적고 main에 저장합니다. 저장 전 변경된 줄에 오타가 없는지 한 번 봅니다.')
step(4, 'People 화면에서 결과를 확인합니다.', 'Actions에서 배포 결과를 확인한 뒤 홈페이지의 People을 엽니다. 예전 내용이 보이면 Windows에서 <b>Ctrl + F5</b>로 새로고침합니다.')
note('졸업생으로 바꾸려면', '같은 학생 폴더의 <b>분류: Alumni</b>로 변경하고, 과정·졸업연도·현재소속을 함께 수정합니다. 같은 사람의 폴더를 새로 만들지 말고 기존 ID를 유지하세요.')
p('잠시 숨길 때는 <b>공개: false</b>, 다시 보이게 할 때는 <b>공개: true</b>로 저장합니다. 이 설정은 홈페이지 표시만 바꾸며 저장소 파일을 비공개로 만들지는 않습니다.', 11.3, 18, color=MUTED)

# 05
page('ADD A PERSON  /  05', '새 학생을 추가하기', '아래 이름은 설명용 가상 예시입니다. 실제 학생 정보로 바꾸어 사용하세요.')
step(1, '저장소 최상위에서 새 파일을 만듭니다.', '<b>Code → main → Add file → Create new file</b>을 누릅니다. 파일 이름 칸에 아래 전체 경로를 입력하면 하위 폴더도 함께 만들어집니다.')
code('mclab/content/people/hong-gildong/info.txt', 11.8)
step(2, '정보 입력지를 작성합니다.', '아래 예시를 복사해 이름·연구 분야 등을 바꿉니다. <b>ID와 폴더 이름</b>은 같아야 합니다. 검토 전에는 공개를 false로 두고, 게시할 때 true로 바꿉니다.')
code('ID: hong-gildong\n공개: false\n표시순서: 100\n이름: Gildong Hong\n한글이름: 홍길동\n과정: M.S. Student\n분류: M.S. students\n연구분야: Steer-by-Wire control\n이메일:\n사진:', 11.0)
p('<b>분류 입력값</b><br/>석사: M.S. students · 박사: Ph.D. students<br/>통합과정: Integrated M.S.–Ph.D. students · 학부인턴: Undergraduate interns', 10.9, 17.3)
step(3, '저장하고 사진을 추가한 뒤 공개합니다.', 'Commit changes로 저장합니다. 사진 추가는 다음 쪽을 따릅니다. 이름·사진 게시 동의를 확인한 뒤 <b>공개: true</b>로 바꾸고 다시 저장합니다.')
p('ID에는 영문 소문자·숫자·하이픈을 사용하세요. 기존 학생의 ID를 복사했다면 반드시 새 ID로 바꿔 중복을 피합니다.', 10.9, 17, color=MUTED)

# 06
page('UPLOAD A PHOTO  /  06', '학생 사진을 넣거나 바꾸기', '사진은 학생의 info.txt와 같은 폴더에 넣습니다.')
step(1, '기존 연결 파일명을 먼저 확인합니다.', 'info.txt의 <b>사진:</b> 값을 봅니다. 예를 들어 photo.jpg라고 되어 있으면 새 사진도 photo.jpg로 준비합니다. photo.webp라면 같은 형식을 사용하거나 정보 파일의 값도 함께 바꿉니다.')
step(2, '해당 학생 폴더에서 사진을 업로드합니다.', '<b>학생 폴더 → Add file → Upload files</b>를 누르고 사진 파일을 끌어 넣습니다. 교체라면 기존 사진과 <b>이름·확장자·대소문자</b>가 같아야 합니다.')
step(3, 'Commit changes로 저장합니다.', '“학생 사진 교체”를 적고 저장합니다. 자동 배포가 끝난 뒤 People 화면의 사진을 확인합니다.')
code('mclab/content/people/hong-gildong/\n  info.txt\n  photo.jpg\n\ninfo.txt 안의 연결 예시\n사진: photo.jpg', 11.5)
note('처음 사진을 넣는 경우', '사진 항목이 비어 있으면 <b>photo.jpg / photo.png / photo.webp</b> 같은 기본 이름으로 자동 연결할 수 있습니다. 기본 이름 후보를 여러 개 넣지 말고 한 개만 두세요. 다른 이름을 쓰면 사진 항목에 정확한 파일명을 적습니다.')
table(['권장하는 준비', '주의할 점'], [
    ['인물 사진 약 800 × 1000 px<br/>가능하면 1 MB 이하', 'PNG 파일의 확장자만 JPG로 바꾸지 않습니다. 실제 형식으로 저장하세요.'],
    ['원본 사진과 실제 인물 확인', '다른 학생 사진을 추측해 연결하지 않습니다. 사진 게시 동의와 위치정보를 확인하세요.'],
], [195, CW - 195], 10.7)
p('Windows에서는 파일 확장자 표시를 켜서 photo.jpg.jpg, info.txt.txt처럼 이름이 중복되지 않았는지 확인하세요.', 10.8, 17, color=MUTED)

# 07
page('UPDATE PUBLICATIONS  /  07', '논문을 등록하거나 수정하기', '논문 PDF만 올리는 방식이 아닙니다. 제목·저자·학술지 정보는 info.txt에 적습니다.')
p('<b>새 논문 경로 예시</b> — 저장소 최상위의 Create new file에서 입력합니다.')
code('mclab/content/publications/paper-2026-example/info.txt', 11.3)
code('ID: paper-2026-example\n공개: false\n제목: 실제 논문 제목으로 교체\n저자: 실제 저자 순서대로 입력\n학술지: 실제 학술지 또는 학회명\n연도: 2026\n종류: Journal\n상태: Under review\nDOI:\n대표논문: false\n소속구분: DGIST', 10.9)
p('정보를 확인하고 <b>공개: true</b>로 바꾼 뒤 Commit changes를 누릅니다. 이미 등록된 논문은 새 폴더를 만들지 말고 기존 info.txt의 상태·연도·DOI를 수정합니다.', 11.5, 18.1)
table(['상태', '언제 사용하나요?'], [
    ['Under review / Submitted', '심사 중 / 제출한 원고'],
    ['Accepted', '게재 확정 통보를 받은 원고'],
    ['Early Access / Published', '조기 온라인 공개 / 게재된 논문'],
], [190, CW - 190], 10.7)
note('선택 첨부 자료', '같은 폴더에 <b>figure.png</b>를 넣으면 대표 그림, <b>paper.pdf</b>를 넣으면 원문 첨부로 연결됩니다. DOI만 적어도 출판사 연결에 사용할 수 있습니다. PDF 공개 권한이 불확실하면 원문 파일 대신 DOI를 사용하세요.')
p('학회 논문은 종류: Conference로 입력합니다. DOI가 있다고 게재 상태가 자동 확정되는 것은 아닙니다. 같은 DOI를 두 번 등록하지 마세요.', 10.8, 17, color=MUTED)

# 08
page('UPDATE PROJECTS  /  08', '과제를 등록하고 기간을 바꾸기', '과제 하나당 폴더 하나. 종료된 과제도 삭제하지 않고 이력으로 남길 수 있습니다.')
p('<b>새 과제 경로 예시</b>')
code('mclab/content/projects/project-example/info.txt', 11.5)
code('ID: project-example\n공개: false\n제목: 실제 과제명으로 교체\n지원기관: 공개 가능한 지원기관명\n지원구분: Industry\n시작: 2026-11\n종료: 2027-07\n상태: auto\n요약: 공개 가능한 연구내용을 한두 문장으로 입력', 11.2)
table(['항목', '입력 방법'], [
    ['지원구분', '산업체 Industry / 정부 Government / 기관 Institutional'],
    ['시작·종료', 'YYYY-MM 형태로 입력합니다. 예: 2026-11'],
    ['상태: auto', '입력한 기간을 기준으로 예정·진행·완료를 분류합니다.'],
], [119, CW - 119], 10.8)
step(1, '공개 내용을 검토한 뒤 저장합니다.', '게시 가능한 제목·기간·지원기관인지 확인하고 <b>공개: true</b>로 바꿉니다. Commit changes 후 Projects 화면을 확인합니다.')
step(2, '기간 연장이나 종료는 기존 파일에서 수정합니다.', '기존 폴더의 종료: 값을 바꾸어 저장합니다. 상태를 날짜에 맡기려면 auto를 유지합니다. 보류·취소처럼 예외가 있을 때만 별도 상태를 사용합니다.')
note('과제 첨부는 공개용 자료만', '<b>figure.jpg</b>는 대표 그림, <b>summary.pdf</b>는 공개 요약문으로 사용할 수 있습니다. 계약서 원본·비공개 연구비·개인정보가 담긴 계획서는 올리지 마세요.', warn=True)

# 09
page('NEWS AND OTHER CONTENT  /  09', '소식·연구 그림·졸업생 관리', '같은 방식으로 info.txt를 수정하고 저장하면 됩니다.')
label('연구실 소식 추가')
code('파일: mclab/content/news/lab-news-example/info.txt\n\nID: lab-news-example\n공개: false\n날짜: 2026-10-10\n구분: Lab news\n제목: 실제 소식 제목으로 교체\n내용: 공개할 내용을 한두 문장으로 입력', 11.0)
p('날짜와 내용을 확인한 뒤 공개를 true로 바꿔 저장합니다. 소식 사진은 같은 폴더에 photo.jpg로 넣습니다. 예시 날짜는 실제 행사 날짜로 교체하세요.', 11.3, 18)
table(['관리 항목', '수정 위치와 방법'], [
    ['행사 사진 갤러리', 'mclab/content/gallery/사진-ID/<br/>info.txt의 제목·내용과 photo.jpg를 관리합니다. 날짜를 모르면 빈칸으로 둡니다.'],
    ['기존 연구 그림', 'mclab/content/research/연구-ID/<br/>대표그림 항목의 파일명을 확인하고 같은 이름의 그림으로 교체합니다.'],
    ['졸업생 전환', '기존 people 폴더에서 분류: Alumni로 변경합니다. 졸업연도·현재소속도 함께 수정합니다.'],
    ['주소·교수님 이력 등', 'mclab/content/site.json<br/>공통 설정은 구조화된 JSON입니다. 일상적인 학생·논문 수정 때는 건드리지 않습니다.'],
], [116, CW - 116], 10.8)
note('입력 화면을 사용하는 방법도 있습니다.', 'PC에서 패키지의 <b>admin/info-helper.html</b>을 열면 구성원·논문·과제 정보를 입력하고 info.txt로 저장할 수 있습니다. <b>기본 공개값은 false</b>입니다. 이 도구는 GitHub에 자동 업로드하지 않으므로 생성 파일을 알맞은 폴더에 올리고 Commit해야 합니다.')

# 10
page('CHECK THE RESULT  /  10', '저장 후, 반영 여부 확인하기', 'Commit changes는 저장이고, Actions는 홈페이지를 새로 만드는 과정입니다.')
step(1, 'Actions에서 해당 실행을 엽니다.', '<b>Actions → Install and deploy MCLab</b>을 누릅니다. 방금 저장한 변경 설명이 보이는 실행을 선택합니다. 다른 검사 이름과 혼동하지 마세요.')
step(2, '배포 단계까지 실행되었는지 봅니다.', '실행 화면의 <b>deploy</b> 작업을 엽니다. 아래 홈페이지 검사·생성·배포 단계가 건너뛰기(skipped)가 아니라 성공(success)인지 확인합니다.')
table(['화면에 표시되는 단계', '의미'], [
    ['Validate website content and images', '자료 형식과 이미지 연결 검사'],
    ['Build website from content folders', '수정한 info.txt로 홈페이지 생성'],
    ['Publish verified website to existing gh-pages branch', '공개용 파일을 gh-pages에 반영'],
], [302, CW - 302], 10.4)
step(3, '실제 홈페이지를 새로고침합니다.', '홈페이지 주소를 열고 수정한 메뉴를 확인합니다. 홈페이지 공개 작업이 따로 실행되는 경우 해당 작업 결과도 확인합니다. 예전 화면이면 <b>Ctrl + F5</b>로 다시 불러옵니다.')
step(4, '변경한 내용과 사진을 직접 확인합니다.', '이름·사진·논문 상태·과제 기간을 하나씩 봅니다. 검색 필터가 걸려 있다면 초기화한 뒤 다시 찾습니다.')
note('초록색 성공 표시만 보고 끝내지 마세요.', 'ZIP이 없는 초기 실행은 설치기 검사만 성공하고 실제 홈페이지 배포는 skipped일 수 있습니다. <b>mclab 폴더 생성 + 배포 단계 수행 + 실제 홈페이지 화면</b>을 함께 확인해야 합니다.', warn=True)
url('자동 생성·배포 실행 목록 열기', ACTIONS)

# 11
page('TROUBLESHOOTING  /  11', '막히면 이 표부터 확인하세요', '잘못 수정했더라도 새 배포 전에는 성공적으로 공개된 이전 화면이 유지됩니다.')
table(['증상', '먼저 확인할 내용'], [
    ['mclab 폴더가 없습니다.', '2쪽 최초 설치를 확인합니다. ZIP을 저장소 최상위 main에 올렸는지 확인하세요.'],
    ['연필·편집 버튼이 없습니다.', 'GitHub 로그인 계정과 저장소 수정 권한을 확인합니다. 권한이 없으면 관리자에게 요청합니다.'],
    ['저장했는데 홈페이지가 그대로입니다.', 'main에 저장했는지, Actions에서 배포 단계까지 성공했는지, Ctrl + F5로 다시 불러왔는지 봅니다.'],
    ['새 학생·논문·과제가 안 보입니다.', '공개: true인지, 기존 ID와 중복되지 않는지, 필터에 가려지지 않았는지 확인합니다.'],
    ['사진이 안 보이거나 이전 사진입니다.', 'info.txt의 파일명·확장자·대소문자와 실제 파일을 대조합니다. 기본 이름 사진이 여러 개면 정리합니다.'],
    ['Actions에 빨간 실패 표시가 뜹니다.', 'Install and deploy MCLab의 실패한 단계를 엽니다. 오류에 나온 폴더·항목을 수정하고 다시 Commit합니다.'],
    ['성공인데 실제 배포가 skipped입니다.', '초기 ZIP이 없거나 설치 준비가 끝나지 않은 상태일 수 있습니다. 2쪽과 10쪽을 확인합니다.'],
    ['주소가 404이거나 예전 사이트입니다.', 'Settings → Pages에서 gh-pages / (root)와 실제 공개 주소를 확인합니다. 새 사이트 설치 여부도 봅니다.'],
], [152, CW - 152], 10.5)
note('정보 파일을 잘못 고쳤다면', '해당 파일의 <b>History</b>에서 이전 내용을 확인해 필요한 값을 복사합니다. 현재 main의 info.txt를 다시 편집하여 올바른 값으로 저장합니다. 큰 변경 전에 기존 내용을 따로 보관하면 복구가 쉽습니다.')
p('<b>직접 삭제하지 않을 것:</b> .github 폴더, mclab/.mclab-import.json, scripts 폴더. 공개 저장소에 올린 민감정보는 파일만 지워도 과거 이력에 남을 수 있으므로 처음부터 올리지 않는 것이 중요합니다.', 10.8, 17, color=MUTED)

# 12
page('QUICK REFERENCE  /  12', '이 한 장만 기억해도 됩니다', '새 자료는 새 폴더, 기존 자료는 기존 info.txt. 마지막에는 항상 저장과 화면 확인입니다.')
table(['내가 할 일', '기억할 경로·버튼'], [
    ['학생 정보·사진', 'main → mclab/content/people/'],
    ['논문 정보·첨부', 'main → mclab/content/publications/'],
    ['과제 정보·첨부', 'main → mclab/content/projects/'],
    ['수정 내용 저장', 'Commit changes'],
    ['자동 생성·배포 확인', 'Actions → Install and deploy MCLab'],
], [150, CW - 150], 10.8)
p('<b>저장 전 확인:</b> 실제 정보인가? · 공개 가능한가? · ID와 폴더 이름이 같은가? · 사진 파일명이 정확한가?<br/><b>저장 후 확인:</b> main에 반영했는가? · 배포 단계가 성공했는가? · 실제 화면을 확인했는가?', 11.0, 18)
label('자주 사용하는 바로가기')
url('홈페이지  |  ' + SITE, SITE)
url('관리 저장소  |  ' + REPO, REPO)
url('Actions 실행 결과  /  홈페이지 생성·배포', ACTIONS)
url('Settings → Pages  /  공개 주소·배포 브랜치', PAGES)
label('작성 근거와 공식 도움말')
p('현재 저장소 deploy.yml과 설치기, 제공된 MCLab 정보 작성 도구의 항목 정의, 원본 사진·Teaching 제외 버전의 관리 안내를 기준으로 작성했습니다. 예시 인물·논문·과제는 실제 신규 등록 자료가 아닙니다.', 9.7, 15, gap=9, color=MUTED)
url('저장소의 실제 자동 설치·배포 설정', REPO + '/blob/main/.github/workflows/deploy.yml')
url('GitHub 공식: 파일 편집 및 새 파일 업로드', 'https://docs.github.com/en/repositories/working-with-files/managing-files')
url('GitHub 공식: Pages 공개 소스 설정', 'https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site')
p('안내서의 현재 상태는 작성 시점 기준입니다. 이 PDF 제작은 별도 문서용 브랜치에서 수행되며, 그 자체로 새 홈페이지를 설치하거나 공개하지 않습니다.', 9.7, 15, color=MUTED, gap=0)

finish()
if page_no != TOTAL:
    raise RuntimeError(f'Expected {TOTAL} pages, built {page_no}')
c.save()

# Provide conservative copy-and-edit text examples. They are hidden by default.
templates = {
    'people/hong-gildong/info.txt': 'ID: hong-gildong\n공개: false\n표시순서: 100\n이름: Gildong Hong\n한글이름: 홍길동\n과정: M.S. Student\n분류: M.S. students\n연구분야: 실제 연구 분야로 교체\n이메일:\n사진:\n',
    'publications/paper-2026-example/info.txt': 'ID: paper-2026-example\n공개: false\n제목: 실제 논문 제목으로 교체\n저자: 실제 저자 순서대로 입력\n학술지: 실제 학술지 또는 학회명\n연도: 2026\n종류: Journal\n상태: Under review\nDOI:\n대표논문: false\n소속구분: DGIST\n',
    'projects/project-example/info.txt': 'ID: project-example\n공개: false\n제목: 실제 과제명으로 교체\n지원기관: 공개 가능한 지원기관명\n지원구분: Industry\n시작: 2026-11\n종료: 2027-07\n상태: auto\n요약: 공개 가능한 연구내용으로 교체\n',
    'README_KO.txt': '설명용 가상 예시입니다. 실자료로 바꾸고 ID와 폴더 이름을 일치시키세요.\n이 ZIP은 최초 홈페이지 설치용 ZIP이 아닙니다. 그대로 저장소 최상위에 업로드하지 마세요.\n필요한 info.txt만 꺼내 수정한 뒤 main의 mclab/content/ 아래 올바른 위치에 저장하세요.\n기본 공개값은 false입니다. 게시 동의와 내용을 검토한 뒤 true로 변경합니다.\n사진과 PDF는 포함되어 있지 않습니다. 민감정보나 비공개 계약서는 올리지 마세요.\n',
}
with zipfile.ZipFile(ROOT / 'MCLab_Update_Templates.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for name, text in templates.items():
        z.writestr(name, text)

# Validate page count, embedded Korean fonts, links and content bounds; render previews.
import fitz

doc = fitz.open(PDF_PATH)
if len(doc) != TOTAL:
    raise RuntimeError('PDF page count mismatch')
text = ''.join(page.get_text() for page in doc)
if '홈페이지 데이터 업데이트' not in text or 'Commit changes' not in text:
    raise RuntimeError('PDF text extraction check failed')
links = sum(len(page.get_links()) for page in doc)
font_count = len({font[0] for page in doc for font in page.get_fonts()})
if links < 8 or font_count < 2:
    raise RuntimeError('Expected working links and Korean fonts')
preview_pages = [0, 1, 4, 5, 6, 9, 11]
for index in preview_pages:
    doc[index].get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False).save(ROOT / f'preview-{index+1:02d}.png')
status['pdf'] = {
    'pages': len(doc), 'bytes': PDF_PATH.stat().st_size,
    'sha256': hashlib.sha256(PDF_PATH.read_bytes()).hexdigest(),
    'link_annotations': links, 'font_resources': font_count,
    'layout_checks': page_checks,
    'text_extraction': 'passed', 'rendered_pages': [i+1 for i in preview_pages],
}
(ROOT / 'verification.json').write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'README.md').write_text('# MCLab 데이터 업데이트 안내서\n\n'
    '- [PDF 안내서](MCLab_Data_Update_Guide_KO.pdf)\n'
    '- [정보 입력 예시 ZIP](MCLab_Update_Templates.zip)\n'
    '- [생성 및 접속 확인 결과](verification.json)\n\n'
    '이 문서는 docs/update-guide-20261010 브랜치에만 생성되었습니다. '
    'main, gh-pages 및 기존 홈페이지 배포 설정은 변경하지 않았습니다.\n', encoding='utf-8')
print(json.dumps(status, ensure_ascii=False, indent=2))
