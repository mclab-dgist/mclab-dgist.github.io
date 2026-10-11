#!/usr/bin/env python3
"""Generate a concise Korean MCLab GitHub editing guide (2 A4 pages)."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs'/'MCLab_홈페이지_업데이트_간편매뉴얼.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
font='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
pdfmetrics.registerFont(TTFont('Nanum',font))
navy=colors.HexColor('#102a4c'); blue=colors.HexColor('#2365c8'); grey=colors.HexColor('#52637a')
styles={
'title':ParagraphStyle('t',fontName='Nanum',fontSize=20,leading=29,textColor=navy,spaceAfter=13),
'h':ParagraphStyle('h',fontName='Nanum',fontSize=12.2,leading=18,textColor=navy,spaceBefore=12,spaceAfter=7),
'body':ParagraphStyle('b',fontName='Nanum',fontSize=9.6,leading=16.2,textColor=navy,spaceAfter=6),
'small':ParagraphStyle('s',fontName='Nanum',fontSize=8.3,leading=13,textColor=grey,spaceAfter=4),
}
P=lambda t,sty='body':Paragraph(t,styles[sty])
story=[]
story.extend([P('MCLab 홈페이지 업데이트 간편 매뉴얼','title'),
P('학생·사진·논문·과제·뉴스 수정 | GitHub 웹브라우저에서 직접 관리'),
P('관리 주소: https://github.com/mclab-dgist/mclab-dgist.github.io','small'),
P('방문자 주소: https://mclab-dgist.github.io/','small')])
story.append(P('1. 가장 중요한 5단계','h'))
for x in [
'① GitHub에 로그인 → 위 관리 주소 접속 → <b>main</b> 브랜치 확인',
'② <b>mclab/content</b> 폴더로 이동 → 수정할 분야 선택',
'③ 해당 항목의 <b>info.txt</b> 클릭 → 오른쪽 위 연필(Edit) 클릭',
'④ 필요한 글만 바꾸고 오른쪽 위 <b>Commit changes</b> 클릭',
'⑤ <b>Actions → Install and deploy MCLab</b>에서 초록 체크 확인 → 홈페이지 새로고침']:
 story.append(P(x))
story.append(P('2. 어디를 수정하나요?','h'))
rows=[
['작업','GitHub 폴더'],
['학생 정보 / 사진','mclab/content/people/학생-id/'],
['논문 추가 / 수정','mclab/content/publications/논문-id/'],
['연구과제 추가 / 수정','mclab/content/projects/과제-id/'],
['뉴스 / 행사 사진','mclab/content/news/뉴스-id/'],
['연구 내용 / 그림','mclab/content/research/연구-id/'],
]
table=Table([[P(c,'small') for c in row] for row in rows],colWidths=[126,365],hAlign='LEFT')
table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf2fd')),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#d6e2ee')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
story.append(table)
story.append(Spacer(1,8))
story.append(P('3. 사진을 바꾸려면','h'))
story.append(P('기존 사진 파일을 교체할 때는 같은 폴더에 같은 파일명(예: photo.jpg)으로 업로드합니다. 새 파일명이라면 info.txt의 <b>사진:</b> 또는 <b>대표그림:</b> 값도 함께 바꾸세요.'))
story.append(P('주의: PC에 파일만 저장하면 홈페이지는 바뀌지 않습니다. GitHub에서 반드시 Commit해야 합니다.','small'))
story.append(PageBreak())
story.append(P('새 항목 추가 · 자동배포 확인','title'))
story.append(P('4. 새 학생·논문·과제·뉴스 추가','h'))
story.append(P('① 같은 분야의 기존 항목 폴더를 참고하여 새 폴더를 만듭니다. 예: <b>mclab/content/people/new-student/</b>'))
story.append(P('② 그 안에 <b>info.txt</b>를 만들고 기존 항목의 형식(항목: 값)을 복사해 새 내용으로 바꿉니다. <b>ID</b>는 폴더 이름과 같게 설정하세요.'))
story.append(P('③ 사진이 필요하면 같은 폴더에 업로드하고 파일명을 연결합니다. 모든 수정 후 <b>Commit changes</b>를 누릅니다.'))
story.append(P('학생 정보 예시','h'))
for x in ['ID: new-student','공개: true','이름: New Student','한글이름: 홍길동','과정: M.S. Student','분류: M.S. students','연구분야: Vehicle Dynamics and Control','사진: photo.jpg']:
 story.append(P(x,'small'))
story.append(P('5. 자동배포는 누가 하나요?','h'))
story.append(P('<b>GitHub Actions가 자동으로 수행합니다.</b> Commit하면 검증 → 사이트 생성 → 게시가 진행됩니다. 일반적으로 별도 배포 버튼을 누를 필요가 없습니다.'))
story.append(P('확인: 저장소 상단 <b>Actions</b> → <b>Install and deploy MCLab</b> → 최신 실행 결과가 <b>초록색 체크</b>인지 확인합니다. 실패(빨간색)하면 해당 실행의 실패 단계와 오류 메시지를 확인해야 합니다.'))
story.append(P('6. 자주 하는 실수','h'))
for x in [
'• 저장만 하고 Commit을 누르지 않음 → 공개 홈페이지에 반영되지 않음',
'• 사진 파일명과 info.txt에 적은 이름이 다름 → 이미지가 보이지 않음',
'• 날짜나 필수 항목 형식이 틀림 → 자동 검증이 실패할 수 있음',
'• 배포 성공 후 이전 화면이 보임 → 새로고침(Ctrl+Shift+R) 및 잠시 후 확인',
'• 공개 저장소에 개인정보·계약서 업로드 금지 (공개: false여도 파일은 보일 수 있음)']:
 story.append(P(x))
story.append(Spacer(1,9))
story.append(P('간단한 원칙: <b>info.txt 수정 → Commit → Actions 초록 체크 → 홈페이지 확인</b>','h'))
story.append(P('메뉴 디자인·레이아웃 수정은 일반 콘텐츠 수정과 다르므로 개발 코드 변경이 필요합니다.','small'))
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=44,bottomMargin=43,title='MCLab 홈페이지 업데이트 간편 매뉴얼',author='MCLab')
def footer(canvas,doc):
 canvas.setFont('Nanum',8);canvas.setFillColor(grey);canvas.drawString(48,24,'MCLab · DGIST | 홈페이지 관리 요약');canvas.drawRightString(A4[0]-48,24,str(doc.page))
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
