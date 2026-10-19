#!/usr/bin/env python3
"""Compile MCLab content folders into a GitHub Pages artifact.
Python >=3.11, standard library only. No APIs, paid services, or secrets.
An invalid record aborts the entire build before changing an existing output.
Only referenced public assets are copied, never arbitrary content-folder files.
"""
from __future__ import annotations
import argparse
import calendar
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any
from urllib.parse import quote, urlsplit
from zoneinfo import ZoneInfo

CATEGORIES = ('people', 'publications', 'projects')
PAGES = ('index', 'people', 'professor', 'research', 'publications', 'projects', 'news', 'join', '404')
LABELS = {
 'ID':'id','공개':'visible','표시순서':'order','이름':'name','한글이름':'nameKo',
 '과정':'role','직책':'role','분류':'group','연구분야':'interest','이메일':'email','사진':'photo',
 '홈페이지':'website','입학연도':'joined','졸업연도':'graduated','현재소속':'affiliation',
 '제목':'title','논문제목':'title','과제명':'title','저자':'authors','학술지':'venue',
 '학회':'venue','연도':'year','종류':'type','상태':'status','게재상태':'status','진행상태':'status',
 'DOI':'doi','권호쪽':'details','대표논문':'featured','소속구분':'era','영상':'video',
 '참고':'note','원문순위표기':'sourceRanking','원문서지':'sourceCitation','출처':'source','책임구분':'leadRole',
 '대분류':'program','설명':'description','날짜':'date','구분':'tag','내용':'text','사진설명':'alt',
 '코드':'code','관련과제':'project','PDF':'pdf','대표그림':'image','링크':'url',
 '지원기관':'funder','지원구분':'category','시작':'start','종료':'end','요약':'summary','공개자료':'attachment',
}
COMMON={'id','visible','order'}
ALLOWED={
 'people':COMMON|{'name','nameKo','role','group','interest','email','photo','website','joined','graduated','affiliation'},
 'publications':COMMON|{'title','authors','venue','year','type','status','doi','details','featured','era','video','code','project','pdf','image','url','note','sourceRanking','sourceCitation','source'},
 'projects':COMMON|{'title','funder','category','code','start','end','status','summary','image','attachment','url','leadRole','source'},
}
GROUPS=['Faculty','Researchers','Ph.D. students','Integrated M.S.–Ph.D. students','M.S. students','Undergraduate interns','Alumni']
GROUP_ALIASES={'교수':'Faculty','연구원':'Researchers','박사과정':'Ph.D. students','석박사통합':'Integrated M.S.–Ph.D. students','석박사통합과정':'Integrated M.S.–Ph.D. students','석사과정':'M.S. students','학부연구생':'Undergraduate interns','졸업생':'Alumni'}
ROLE_ALIASES={'교수':'Professor','박사후연구원':'Postdoctoral Researcher','박사과정':'Ph.D. Student','석박사통합':'Integrated M.S.–Ph.D. Student','석박사통합과정':'Integrated M.S.–Ph.D. Student','석사과정':'M.S. Student','학부연구생':'Undergraduate Intern','졸업생':'Alumnus / Alumna','연구원':'Researcher'}
PUB_STATUSES=['Published','Early Access','Accepted','Preprint','Under review','Submitted','In preparation']
PUB_ALIASES={'게재':'Published','게재완료':'Published','출판':'Published','온라인게재':'Early Access','게재확정':'Accepted','채택':'Accepted','프리프린트':'Preprint','심사중':'Under review','투고':'Submitted','투고완료':'Submitted','작성중':'In preparation','준비중':'In preparation'}
PROJECT_STATUSES=['auto','Ongoing','Upcoming','Completed','On hold','Cancelled']
PROJECT_ALIASES={'자동':'auto','진행':'Ongoing','진행중':'Ongoing','예정':'Upcoming','완료':'Completed','종료':'Completed','보류':'On hold','중단':'Cancelled'}
CATEGORY_ALIASES={'정부':'Government','정부과제':'Government','산업체':'Industry','산업체과제':'Industry','기관':'Institutional','교내':'Institutional'}
IMAGE_EXTS={'.jpg','.jpeg','.png','.webp','.svg'}

class ContentError(ValueError):
    """A user-editable input is invalid."""

def boolean(value: Any, field: str, default: bool=False) -> bool:
    if value is None or value=='':return default
    if isinstance(value,bool):return value
    if str(value).strip().lower() in ('true','yes','1','예','공개'):return True
    if str(value).strip().lower() in ('false','no','0','아니오','비공개'):return False
    raise ContentError(f'{field}: true 또는 false 를 입력하세요: {value!r}')

def number(value: Any, field: str, default: int=100) -> int:
    if value is None or value=='':return default
    if isinstance(value,bool) or not re.fullmatch(r'-?\d+',str(value).strip()):
        raise ContentError(f'{field}: 정수를 입력하세요.')
    return int(value)

def read_info(path: Path) -> dict[str,Any]:
    try:text=path.read_text(encoding='utf-8-sig')
    except UnicodeError as e:raise ContentError('UTF-8 인코딩으로 저장하세요.') from e
    if path.suffix=='.json':
        def unique(pairs):
            out={}
            for k,v in pairs:
                if k in out:raise ContentError(f'중복 항목: {k}')
                out[k]=v
            return out
        try:raw=json.loads(text,object_pairs_hook=unique)
        except json.JSONDecodeError as e:raise ContentError(f'JSON {e.lineno}행: {e.msg}') from e
        if not isinstance(raw,dict):raise ContentError('info.json은 객체 한 개여야 합니다.')
    else:
        raw={};last=None;multiline=False
        for i,line in enumerate(text.splitlines(),1):
            if not line.strip() or line.lstrip().startswith('#'):continue
            if multiline and line.startswith(('  ','\t')):
                raw[last]+=('\n' if raw[last] else '')+line.lstrip();continue
            if ':' not in line and '：' not in line:
                raise ContentError(f'{i}행: "항목: 값" 형식으로 입력하세요.')
            key,value=re.split('[:：]',line,maxsplit=1);key=key.strip();value=value.strip()
            if not key:raise ContentError(f'{i}행: 항목 이름이 없습니다.')
            if key in raw:raise ContentError(f'{i}행: 중복 항목 {key}')
            multiline=value=='|';raw[key]='' if multiline else value;last=key
    out={}
    for key,value in raw.items():
        canonical=LABELS.get(key,key)
        if canonical in out:raise ContentError(f'같은 항목을 두 번 입력했습니다: {key}')
        if isinstance(value,(dict,list)):raise ContentError(f'{key}: 문자열 또는 숫자만 입력하세요.')
        out[canonical]=value
    return out

def choose(value: Any, choices: list[str], aliases: dict[str,str], field:str) -> str:
    text=str(value or '').strip();text=aliases.get(text,text)
    matched=next((c for c in choices if c.lower()==text.lower()),None)
    if matched is None:raise ContentError(f'{field}: 다음 중 하나를 입력하세요: {", ".join(choices)}')
    return matched

def date_value(value: str, field: str) -> str:
    if not re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?',value):raise ContentError(f'{field}: YYYY-MM 또는 YYYY-MM-DD 형식이어야 합니다.')
    try:dt.date.fromisoformat(value+'-01' if len(value)==7 else value)
    except ValueError as e:raise ContentError(f'{field}: 존재하지 않는 날짜입니다.') from e
    return value

def bound_date(value: str, end: bool=False) -> str:
    if len(value)==10:return value
    day=calendar.monthrange(int(value[:4]),int(value[5:]))[1] if end else 1
    return f'{value}-{day:02d}'

def project_status(start: str,end: str,today: str) -> str:
    return 'Upcoming' if today<bound_date(start) else ('Completed' if today>bound_date(end,True) else 'Ongoing')

def external_url(value: str) -> str:
    if not value:return ''
    parts=urlsplit(value)
    if parts.scheme not in ('http','https') or not parts.netloc or parts.username or parts.password or re.search(r'[\s<>"\'\\\x00-\x1f]',value):
        raise ContentError(f'http:// 또는 https:// 주소만 허용합니다: {value!r}')
    return value

def check_media(path: Path, extensions:set[str]) -> None:
    if path.is_symlink() or not path.is_file():raise ContentError(f'파일이 없거나 심볼릭 링크입니다: {path.name}')
    if path.suffix.lower() not in extensions:raise ContentError(f'허용하지 않는 첨부 확장자: {path.name}')
    if path.stat().st_size>25*1024*1024:raise ContentError(f'첨부 파일은 25 MiB 이하로 줄이세요: {path.name}')
    with path.open('rb') as f:head=f.read(16)
    ext=path.suffix.lower()
    good={'.jpg':head.startswith(b'\xff\xd8\xff'),'.jpeg':head.startswith(b'\xff\xd8\xff'),'.png':head.startswith(b'\x89PNG\r\n\x1a\n'),'.webp':head.startswith(b'RIFF') and head[8:12]==b'WEBP','.pdf':head.startswith(b'%PDF-')}.get(ext,False)
    if ext=='.svg':
        # SVG files must be static diagrams; reject scripts, external resources and active content.
        import xml.etree.ElementTree as ET
        try:
            tree=ET.parse(path)
            allowed_tags={'svg','rect','path','text','line','circle','ellipse','polyline','polygon','g','title','desc'}
            allowed_attrs={'xmlns','viewBox','width','height','x','y','x1','y1','x2','y2','rx','ry','cx','cy','r','d','fill','stroke','stroke-width','font-family','font-size','font-weight','text-anchor','opacity','transform','role','aria-label','points','stroke-linecap','stroke-linejoin'}
            for node in tree.iter():
                if node.tag.rsplit('}',1)[-1] not in allowed_tags:raise ValueError('unsafe SVG element')
                for key,value in node.attrib.items():
                    if key.rsplit('}',1)[-1] not in allowed_attrs or 'url(' in value.lower():
                        raise ValueError('unsafe SVG attribute')
            if tree.getroot().tag.rsplit('}',1)[-1]!='svg':raise ValueError('missing SVG root')
        except (ET.ParseError,ValueError) as exc:
            raise ContentError(f'허용하지 않는 SVG 내용: {path.name}: {exc}') from exc
        good=True
    if not good:raise ContentError(f'확장자와 실제 파일 형식이 다릅니다: {path.name}')

def media(value: str, folder:Path, category:str, slug:str, extensions:set[str], names: tuple[str,...], assets:dict[str,Path]) -> str:
    """Resolve only an explicit sibling filename or one unambiguous conventional name."""
    value=value.strip()
    if value.startswith(('http://','https://')):return external_url(value)
    if value and (Path(value).name!=value or '/' in value or '\\' in value or value in ('.','..')):
        raise ContentError('사진·첨부는 같은 폴더의 파일명만 입력하세요. 상위 폴더 경로는 허용하지 않습니다.')
    if value:path=folder/value
    else:
        candidates=[p for p in folder.iterdir() if p.name.lower() in names]
        if len(candidates)>1:raise ContentError(f'자동 연결 후보가 여러 개입니다. 파일명을 직접 지정하세요: {", ".join(p.name for p in candidates)}')
        if not candidates:return ''
        path=candidates[0]
    check_media(path,extensions)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    rel=f'media/{category}/{slug}/{digest}-{path.name}'
    assets[rel]=path
    return quote(rel,safe='/')

def collect(root:Path,today:str) -> tuple[dict[str,Any],dict[str,Path],dict[str,Any]]:
    base_path=root/'content/site.json'
    try:base=json.loads(base_path.read_text(encoding='utf-8-sig'))
    except (ValueError,OSError) as e:raise ContentError(f'content/site.json: {e}') from e
    base.pop('teaching', None)
    required={'config','pi','research','news','gallery','recruitment','sources'}
    if not required.issubset(base):raise ContentError('content/site.json에 필수 홈페이지 설정이 없습니다.')
    for cat in CATEGORIES:base[cat]=[]
    assets:dict[str,Path]={};errors=[];warnings=[];hidden=[];seen=set();doi_seen={};faculty_count=0
    for cat in CATEGORIES:
        parent=root/'content'/cat
        if not parent.is_dir():raise ContentError(f'필수 폴더 없음: content/{cat}')
        for folder in sorted(parent.iterdir()):
            if folder.name.startswith(('.', '_')):continue
            if folder.is_symlink():errors.append(f'{folder}: 심볼릭 링크는 허용하지 않습니다.');continue
            if not folder.is_dir():continue
            label=f'content/{cat}/{folder.name}'
            try:
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',folder.name):raise ContentError('폴더명은 영문 소문자·숫자·하이픈만 사용하세요.')
                infos=[p for p in folder.iterdir() if p.name in ('info.txt','info.json')]
                if len(infos)!=1:raise ContentError('info.txt 또는 info.json 중 정확히 하나가 필요합니다. 사진/PDF만으로 내용을 추측하지 않습니다.')
                if infos[0].is_symlink():raise ContentError('정보 파일의 심볼릭 링크는 허용하지 않습니다.')
                r=read_info(infos[0]);unknown=set(r)-ALLOWED[cat]
                if unknown:raise ContentError('알 수 없는 항목: '+', '.join(sorted(unknown)))
                slug=str(r.get('id') or folder.name)
                if slug!=folder.name:raise ContentError('ID와 폴더명을 동일하게 맞추세요. 기존 ID는 변경하지 않는 것을 권장합니다.')
                if slug in seen:raise ContentError(f'중복 ID: {slug}')
                seen.add(slug)
                if not boolean(r.get('visible'), '공개', True):hidden.append(label);continue
                clean={k:('' if v is None else str(v).strip()) for k,v in r.items() if k not in ('visible','order','featured','year')}
                clean['id']=slug;clean['order']=number(r.get('order'),'표시순서')
                for key in ALLOWED[cat]-COMMON-{'featured','year'}:clean.setdefault(key,'')
                required_fields={'people':('name','role','group'),'publications':('title','authors','venue','status'),'projects':('title','funder','category','start','end')}[cat]
                for k in required_fields:
                    if not clean[k]:raise ContentError(f'필수 항목 누락: {k}')
                if cat=='people':
                    clean['role']=ROLE_ALIASES.get(clean['role'],clean['role'])
                    clean['group']=choose(clean['group'],GROUPS,GROUP_ALIASES,'분류')
                    if clean['email'] and not re.fullmatch(r'[^\s@<>"\']+@[^\s@<>"\']+\.[^\s@<>"\']+',clean['email']):raise ContentError('이메일 형식을 확인하세요.')
                    for k in ('joined','graduated'):
                        if clean[k] and not re.fullmatch(r'\d{4}',clean[k]):raise ContentError(f'{k}: 4자리 연도만 입력하세요.')
                    clean['website']=external_url(clean['website'])
                    clean['photo']=media(clean['photo'],folder,cat,slug,IMAGE_EXTS,('photo.jpg','photo.jpeg','photo.png','photo.webp'),assets)
                    if clean['group']=='Faculty':
                        faculty_count+=1
                        if faculty_count>1:raise ContentError('주임교수 Faculty 항목은 한 개만 지원합니다.')
                        for k in ('name','nameKo','role','email','photo'):base['pi'][k]=clean[k]
                        if clean['interest']:base['pi']['interests']=[v.strip() for v in clean['interest'].split(' / ') if v.strip()]
                        continue
                elif cat=='publications':
                    clean['status']=choose(clean['status'],PUB_STATUSES,PUB_ALIASES,'상태')
                    clean['type']=choose(clean['type'] or 'Journal',['Journal','Conference'],{'저널':'Journal','학술지':'Journal','학회':'Conference'},'종류')
                    clean['year']=None if r.get('year') in ('',None) else number(r['year'],'연도')
                    if clean['year'] is not None and not 1800<=clean['year']<=2200:raise ContentError('연도를 확인하세요.')
                    if clean['status'] in ('Published','Early Access') and clean['year'] is None:raise ContentError('게재 논문에는 연도가 필요합니다.')
                    clean['featured']=boolean(r.get('featured'),'대표논문',False)
                    doi=re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',clean['doi'],flags=re.I)
                    if doi and not re.fullmatch(r'10\.\d{4,9}/[^\s<>"\'\\]+',doi):raise ContentError('DOI 형식을 확인하세요. 예: 10.1234/example')
                    if doi:
                        if doi.lower() in doi_seen:raise ContentError('중복 DOI: '+doi+' / '+doi_seen[doi.lower()])
                        doi_seen[doi.lower()]=label
                    clean['doi']=doi
                    for k in ('video','code','project','url','source'):clean[k]=external_url(clean[k])
                    clean['pdf']=media(clean['pdf'],folder,cat,slug,{'.pdf'},('paper.pdf',),assets)
                    clean['image']=media(clean['image'],folder,cat,slug,IMAGE_EXTS,('figure.jpg','figure.jpeg','figure.png','figure.webp'),assets)
                    if not clean['era']:clean['era']='DGIST'
                else:
                    clean['category']=choose(clean['category'],['Government','Industry','Institutional'],CATEGORY_ALIASES,'지원구분')
                    clean['start']=date_value(clean['start'],'시작');clean['end']=date_value(clean['end'],'종료')
                    if bound_date(clean['start'])>bound_date(clean['end'],True):raise ContentError('종료일은 시작일보다 빠를 수 없습니다.')
                    requested=choose(clean['status'] or 'auto',PROJECT_STATUSES,PROJECT_ALIASES,'상태')
                    clean['statusMode']=requested
                    clean['status']=project_status(clean['start'],clean['end'],today) if requested=='auto' else requested
                    clean['url']=external_url(clean['url'])
                    clean['source']=external_url(clean['source'])
                    clean['image']=media(clean['image'],folder,cat,slug,IMAGE_EXTS,('figure.jpg','figure.jpeg','figure.png','figure.webp'),assets)
                    clean['attachment']=media(clean['attachment'],folder,cat,slug,{'.pdf'},('summary.pdf',),assets)
                base[cat].append(clean)
                conventional=set(('photo.jpg','photo.jpeg','photo.png','photo.webp','paper.pdf','figure.jpg','figure.jpeg','figure.png','figure.webp','summary.pdf'))
                for p in folder.iterdir():
                    if p.name not in ('info.txt','info.json','README.txt') and p not in assets.values():
                        warnings.append(f'{label}/{p.name}: 연결하지 않은 파일은 홈페이지 배포에서 제외됩니다. 공개 저장소 자체에서는 열람될 수 있습니다.')
            except (ContentError,OSError,ValueError) as e:errors.append(f'{label}: {e}')
    if faculty_count==0:errors.append('공개된 Faculty 항목이 없습니다. content/people/kanghyun-nam/info.txt를 확인하세요.')
    if errors:raise ContentError('\n'.join(errors))
    base['people'].sort(key=lambda r:(GROUPS.index(r['group']),r['order'],r['name'].casefold()))
    base['publications'].sort(key=lambda r:(-(r['year'] or 0),r['order'],r['title'].casefold()))
    base['projects'].sort(key=lambda r:(-int(r['start'].replace('-','')[:6]),r['order'],r['title'].casefold()))
    for cat in CATEGORIES:
        for r in base[cat]:r.pop('order',None)
    collect_extra_sections(root,base,assets,warnings,hidden,seen)
    timestamp=dt.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
    base['config']['builtAt']=timestamp;base['config']['contentMode']='folders';base['config']['statusDate']=today
    for r in base['research']:
        for field,cat in [('pubIds','publications'),('projectIds','projects')]:
            existing={v['id'] for v in base[cat]}
            for missing in set(r.get(field,[]))-existing:warnings.append(f'Research {r["id"]}: 삭제/숨김으로 연결되지 않는 {cat} ID {missing}')
    report={'builtAt':timestamp,'statusDate':today,'people':len(base['people']),'faculty':faculty_count,'publications':len(base['publications']),'projects':len(base['projects']),'linkedAssets':len(assets),'researchTopics':len(base.get('researchTopics',[])),'news':len(base.get('news',[])),'gallery':len(base.get('gallery',[])),'hiddenRecords':hidden,'warnings':warnings}
    return base,assets,report

# Optional folder-managed sections extend the same no-server editing workflow.
EXTRA_SECTIONS = {
    'research': ('researchTopics', {'program','title','description','image','video','source'}, ('program','title','description')),
    'news': ('news', {'date','title','tag','text','image','source'}, ('date','title','text')),
    'gallery': ('gallery', {'date','title','text','image','alt','source'}, ('title',)),
}

def collect_extra_sections(root, base, assets, warnings, hidden, seen):
    for folder_name,(key,fields,required) in EXTRA_SECTIONS.items():
        parent=root/'content'/folder_name
        base.setdefault(key,[])
        if not parent.exists():continue
        records=[]
        for folder in sorted(parent.iterdir()):
            if folder.name.startswith(('.', '_')):continue
            if folder.is_symlink():raise ContentError(f'{folder}: symbolic links are not allowed.')
            if not folder.is_dir():continue
            label=f'content/{folder_name}/{folder.name}'
            try:
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',folder.name):raise ContentError('Use lowercase letters, digits, and hyphens for the folder name.')
                infos=[f for f in folder.iterdir() if f.name in ('info.txt','info.json')]
                if len(infos)!=1:raise ContentError('Exactly one info.txt or info.json is required.')
                if infos[0].is_symlink():raise ContentError('info file cannot be a symbolic link.')
                raw=read_info(infos[0])
                unknown=set(raw)-COMMON-fields
                if unknown:raise ContentError('Unknown fields: '+', '.join(sorted(unknown)))
                if not boolean(raw.get('visible'), '공개', True):
                    hidden.append(label);continue
                slug=str(raw.get('id') or folder.name).strip()
                if slug!=folder.name:raise ContentError('ID must match the folder name.')
                if slug in seen:raise ContentError('Duplicate ID: '+slug)
                seen.add(slug)
                r={f:str(raw.get(f) or '').strip() for f in fields}
                r.update(id=slug, order=number(raw.get('order'),'표시순서'))
                for f in required:
                    if not r[f]:raise ContentError(f'Missing required field: {f}')
                if 'date' in r and r['date']:
                    date_value(r['date'],'날짜')
                    if len(r['date'])!=10:raise ContentError('날짜 must be YYYY-MM-DD.')
                if folder_name=='research':
                    if r['program'] not in {g['id'] for g in base.get('researchPrograms',[])}:raise ContentError('Unknown research program ID.')
                    names=('figure.jpg','figure.jpeg','figure.png','figure.webp')
                    r['video']=external_url(r['video'])
                else:names=('photo.jpg','photo.jpeg','photo.png','photo.webp')
                r['source']=external_url(r.get('source',''))
                r['image']=media(r.get('image',''),folder,folder_name,slug,IMAGE_EXTS,names,assets)
                if folder_name=='gallery' and not r['image']:raise ContentError('A visible gallery record needs a photo.')
                records.append(r)
                for f in folder.iterdir():
                    if f.name not in ('info.txt','info.json','README.txt') and f not in assets.values():warnings.append(f'{label}/{f.name}: unlinked file omitted from Pages; it may still be public in the repository.')
            except (ContentError,OSError,ValueError) as e:raise ContentError(f'{label}: {e}') from e
        if folder_name=='research':records.sort(key=lambda r:(r['order'],r['title']))
        else:records.sort(key=lambda r:(r.get('date') or '',-r['order']),reverse=True)
        for r in records:r.pop('order',None)
        base[key]=records


def js_data(data:dict[str,Any]) -> str:
    # Escape < to keep generated data safe even when inlined into preview HTML.
    return '// GENERATED by scripts/build_site.py. Edit content/*/<id>/info.txt instead.\nwindow.MCLAB_DATA = '+json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')+';\n'

def build(root:Path,output:Path,today:str|None=None) -> dict[str,Any]:
    root=root.resolve();output=output.resolve()
    if output==root or output in root.parents:raise ContentError('출력 경로는 저장소 자체 또는 상위 폴더일 수 없습니다.')
    if output.parent!=root or output.name!='_site':raise ContentError('안전한 출력 경로는 저장소 내부의 _site/ 입니다.')
    today=today or dt.datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
    try:dt.date.fromisoformat(today)
    except ValueError as e:raise ContentError('--today는 YYYY-MM-DD 형식이어야 합니다.') from e
    data,assets,report=collect(root,today)
    # Validate first. Build into a temporary directory, then replace only the artifact.
    with tempfile.TemporaryDirectory(prefix='mclab-build-') as tmp:
        dest=Path(tmp)/'_site';dest.mkdir()
        for name in PAGES:
            p=root/(name+'.html')
            if not p.is_file():raise ContentError(f'필수 화면 파일 없음: {p.name}')
            html=p.read_text(encoding='utf-8')
            # Cache busting uses actual file contents, so updates are automatic on every build.
            # All page templates share these assets; the data hash changes with folder edits.
            versions={
                'assets/css/style.css':hashlib.sha256((root/'assets/css/style.css').read_bytes()).hexdigest()[:12] if (root/'assets/css/style.css').is_file() else '',
                'assets/js/app.js':hashlib.sha256((root/'assets/js/app.js').read_bytes()).hexdigest()[:12] if (root/'assets/js/app.js').is_file() else '',
                'data/site-data.js':hashlib.sha256(js_data(data).encode('utf-8')).hexdigest()[:12],
            }
            for asset,version in versions.items():
                if version:html=html.replace(f'"{asset}"',f'"{asset}?v={version}"')
            (dest/p.name).write_text(html,encoding='utf-8')
        for name in ('.nojekyll','robots.txt','sitemap.xml'):
            if (root/name).is_file():shutil.copy2(root/name,dest/name)
        # Website assets are public by design. Reject links and ignore readme/hidden files.
        for source in (root/'assets').rglob('*'):
            if source.is_symlink():raise ContentError(f'assets 안의 심볼릭 링크: {source}')
            if source.is_file() and not any(p.startswith('.') for p in source.relative_to(root/'assets').parts) and source.suffix.lower() in {'.css','.js','.svg','.jpg','.jpeg','.png','.webp','.ico','.mp4','.webm'}:
                target=dest/source.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        # Publish the two experiment videos used by the Research page.
        for filename in ('SBW.mp4', 'DualSbW.mp4'):
            source=root/'content'/'research'/'human-machine'/filename
            if not source.is_file() or source.is_symlink():
                raise ContentError(f'Research video missing: {filename}')
            target=dest/'assets'/'video'/'research'/filename
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        (dest/'data').mkdir()
        (dest/'data/site-data.js').write_text(js_data(data),encoding='utf-8')
        for rel,source in assets.items():
            target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        if output.exists():shutil.rmtree(output)
        shutil.copytree(dest,output)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,default=None)
    parser.add_argument('--today',help='YYYY-MM-DD; testing only, default Asia/Seoul today')
    args=parser.parse_args()
    try:
        report=build(args.root,args.output or args.root/'_site',args.today)
        summary=os.environ.get('GITHUB_STEP_SUMMARY')
        if summary:
            with open(summary,'a',encoding='utf-8') as f:
                f.write(f'## MCLab content build\n\nFaculty {report["faculty"]} · People {report["people"]} · Publications {report["publications"]} · Projects {report["projects"]} · Assets {report["linkedAssets"]}\n\n')
                f.write('Only validated, visible records and linked assets are included in the Pages artifact.\n')
                for warning in report['warnings']:f.write('- '+warning+'\n')
        return 0
    except (ContentError,OSError) as e:
        print('MCLab build failed / 공개 파일을 수정하지 않았습니다:\n'+str(e),file=sys.stderr)
        return 1
if __name__=='__main__':sys.exit(main())
