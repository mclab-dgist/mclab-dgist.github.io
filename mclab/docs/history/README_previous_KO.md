# MCLab · 폴더 자동 갱신형 홈페이지

**제작 버전: 2026-10-10 / 실제 GitHub 업로드·배포는 아직 수행하지 않았습니다.**

대상 저장소: `https://github.com/nkh6189-sys/mclab-dgist.github.io`
예상 기본 공개 주소: `https://nkh6189-sys.github.io/mclab-dgist.github.io/`
별도 사용자 도메인이 없는 현재 저장소 이름을 기준으로 한 주소입니다. 실제 공개 주소는 Settings → Pages에서 확인하세요.

## 가장 중요한 변경점

이 버전은 **GitHub Actions**가 `content/` 폴더를 읽어 홈페이지를 생성합니다.
**Settings → Pages → Build and deployment → Source → GitHub Actions**로 설정하세요.
이전 버전의 **Deploy from a branch → main / (root)** 설정과 다릅니다.

파일 추가/수정/삭제 → GitHub 기본 브랜치에 Commit / Push → 검증 → 홈페이지 생성 → Pages 배포.
로컬 PC의 폴더에만 파일을 넣는 것으로는 GitHub가 갱신되지 않습니다. Google Sites 원본을 실시간으로 동기화하는 기능도 아닙니다.

## 첫 설치 — GitHub Desktop 권장

1. 저장소에 기존 파일이 있으면 먼저 백업하고 변경 내용을 검토합니다. 이 패키지는 원격 저장소의 현재 파일을 확인한 병합 결과가 아닙니다.
2. GitHub Desktop에서 본인 계정으로 로그인하고 File → Clone Repository → URL에 위 저장소 주소를 입력해 복제합니다.
3. 이 ZIP을 풀고 **최상위 내용물 전체**를 복제한 저장소 폴더로 복사합니다. `repository/` 또는 `site/`라는 하위 폴더를 새로 만들어 넣지 않습니다. `.github/`, `.gitignore`, `.nojekyll`도 포함합니다. 기존 `.git/` 폴더는 건드리지 않습니다.
4. GitHub Desktop에서 변경 파일을 검토합니다. 기존 홈페이지가 운영 중이라면 새 브랜치에서 검토 후 기본 브랜치에 병합하세요. 새 저장소라면 기본 브랜치에 커밋하고 Push origin을 누릅니다.
5. GitHub 저장소 Settings → Pages → Source를 **GitHub Actions**로 설정합니다. 다른 배포 워크플로가 이미 있다면 중복 배포되지 않게 정리합니다.
6. Actions 탭에서 **Update and deploy MCLab**을 확인합니다. 첫 실행이 Pages 설정 전에 실패했다면 설정 후 Re-run all jobs 또는 Run workflow를 선택합니다. `github-pages` 환경의 배포 브랜치 규칙은 기본 브랜치를 허용해야 합니다.
7. 성공 후 Settings → Pages 또는 배포 작업에 표시되는 주소로 접속합니다. 경로·사진·메뉴를 최종 확인합니다.

GitHub 웹 업로드는 한 번에 최대 100개 파일이므로, 파일이 많은 최초 이관에는 Desktop 방식이 편리합니다. 웹으로 나누어 업로드한다면 **`.github/workflows/deploy.yml`은 나머지 자료가 모두 준비된 마지막에** 반영하세요. 숨김 폴더 업로드가 누락되면 Add file → Create new file로 경로와 내용을 직접 생성할 수 있습니다.

## 이후에는 content 폴더만 관리

```text
content/
├── site.json                         # 연구실 공통 설정, 교수님 이력, 모집 안내
├── people/
│   └── minhyeong-kim/
│       ├── info.txt                  # 이미 들어 있는 실제 구성원 정보
│       └── photo.jpg                 # 사진을 추가할 때 넣는 파일
├── publications/
│   └── j26-cnn/
│       ├── info.txt                  # 이미 들어 있는 논문 정보
│       ├── paper.pdf                 # 공개 가능한 원문만 선택적으로 추가
│       └── figure.png                # 대표 그림을 선택적으로 추가
├── projects/
│   └── i1/
│       ├── info.txt
│       ├── figure.jpg                # 선택 사항
│       └── summary.pdf               # 공개 가능한 요약문만 선택적으로 추가
├── research/<주제-ID>/info.txt        # 기존 11개 세부 연구 주제
├── news/<소식-ID>/info.txt            # 날짜별 소식
└── gallery/<사진-ID>/info.txt         # 사진·캡션·날짜
```

위의 사진·PDF는 추가 방법을 설명하는 예시입니다. 이번 이관에서는 기존 Google Sites 이미지가 다운로드되지 않아 실제 인물 사진·연구 그림·PDF를 넣지 않았습니다.

**새 자료:** `templates/`에서 맞는 템플릿을 복사하거나 `admin/info-helper.html`을 열어 작성합니다. ID와 폴더 이름을 같게 정하고 검토 후 `공개: true`로 바꿉니다. 같은 폴더 안에는 `info.txt` 또는 `info.json` 중 하나만 두세요.

**수정:** 해당 폴더의 `info.txt` 또는 사진을 교체하고 Commit / Push합니다. 같은 ID를 유지해야 관련 링크가 끊기지 않습니다.

**삭제:** 해당 폴더를 삭제하고 반영하면 홈페이지 목록에서 제외됩니다. `공개: false`로 숨길 수도 있습니다. GitHub의 과거 커밋에서 파일이 제거되는 것은 아닙니다.

**졸업생 전환:** 같은 사람의 폴더에서 `분류: Alumni`, `과정: Alumnus / Alumna`, `졸업연도`, `현재소속`을 수정합니다. ID를 유지하면 사람이 중복 생성되지 않습니다.

## 파일명 자동 연결 규칙

| 자료 | 기본 이미지명 | 기본 PDF명 | 홈페이지 반영 |
|---|---|---|---|
| 구성원 | `photo.jpg`, `photo.png`, `photo.webp` 중 하나 | 없음 | People, 교수님은 상세 프로필에도 반영 |
| 논문 | `figure.jpg`, `figure.png`, `figure.webp` 중 하나 | `paper.pdf` | 논문·대표논문 그림, PDF 버튼 |
| 과제 | `figure.jpg`, `figure.png`, `figure.webp` 중 하나 | `summary.pdf` | 과제 그림·공개 요약문 버튼 |
| 연구주제 | `figure.jpg`, `figure.png`, `figure.webp` 중 하나 | 없음 | Research 세부 카드 |
| 소식·갤러리 | `photo.jpg`, `photo.png`, `photo.webp` 중 하나 | 없음 | News / Lab gallery |

`.jpeg`도 지원합니다. 이름이 다르면 정보 파일의 `사진`, `대표그림`, `PDF`, `공개자료`에 **같은 폴더 안 파일명**을 직접 적습니다. 원본 확장자만 바꾸면 안 됩니다. 후보가 두 개 이상이면 자동으로 하나를 추측하지 않고 오류를 알려 줍니다. 파일명과 경로의 대소문자를 구분하세요. 미디어는 파일당 25 MiB 이하로 제한했습니다.

사진 파일의 해시를 주소에 넣어 교체 후 브라우저가 이전 사진을 계속 표시하는 문제를 줄였습니다. 사진이 없는 구성원은 이니셜로 표시합니다.

## 정보 파일 예시 — 새 학생

```text
ID: new-student
공개: true
이름: Gildong Hong
한글이름: 홍길동
과정: 박사과정
분류: 박사과정
연구분야: Steer-by-Wire and integrated vehicle control
이메일:
사진:
표시순서: 100
```

이름은 설명용 가상 예시이며 실제 구성원에 포함되어 있지 않습니다. 사진을 같은 폴더의 `photo.jpg`로 넣으면 `사진:` 값은 비워도 됩니다. UTF-8로 저장하고 Windows에서 `info.txt.txt`가 되지 않도록 확장자를 확인하세요.

## 논문과 과제의 상태

논문은 `Published`, `Early Access`, `Accepted`, `Preprint`, `Under review`, `Submitted`, `In preparation`을 구분합니다. DOI가 있다고 자동으로 Published로 바꾸지 않습니다. Accepted는 게재 확정, Published는 게재 목록이며 서로 구분해 표시합니다. 연도순 정렬·검색·Before DGIST 필터·BibTeX가 갱신됩니다.

과제의 `상태: auto`는 시작·종료 날짜로 Upcoming / Ongoing / Completed를 계산합니다. 월 단위 종료일은 해당 월 마지막 날까지 진행으로 봅니다. 홈페이지를 열 때 한국 시간 기준으로 다시 계산하므로 날짜가 지나면 표시가 바뀝니다. 명시적으로 `On hold`, `Cancelled` 등을 지정한 항목은 유지합니다.

PDF·Word·Excel을 아무 형식으로 올려도 AI가 내용을 추측하여 등록하는 방식이 아닙니다. **필수 서지·개인·과제 정보는 info.txt에 명시**하고, PDF는 검토된 첨부 자료로 연결합니다. 학생 개인정보나 논문 게재 상태를 잘못 추정하는 것을 피하기 위한 구조입니다.

## 오류가 나면

Actions의 build 작업 로그에 **문제가 있는 폴더와 항목**이 표시됩니다. 필수 정보 누락, 날짜 오류, ID 중복, DOI 중복, 알 수 없는 항목명, 잘못된 파일 형식 등은 새 배포를 중단합니다. 이미 성공적으로 공개된 홈페이지는 새 배포가 성공할 때까지 유지됩니다. 최초 배포가 실패했다면 아직 새 홈페이지가 생기지 않은 상태입니다.

오류를 고쳐 다시 Commit / Push하세요. `data/site-data.js`나 `_site/`를 수동으로 수정하여 해결하지 마세요. 두 곳은 생성 결과이고 `content/`가 원본입니다.

## 소식·사진·연구주제 및 모집 정보

`content/news`, `content/gallery`, `content/research`도 동일한 파일 방식입니다. 소식 날짜는 `YYYY-MM-DD`, 갤러리 날짜는 모르면 빈칸입니다. 연구주제의 `대분류`는 `vehicle-dynamics`, `mechatronics`, `mobile-robots` 중 하나입니다.

교수님 상세 학력·경력·수상, 연구실 주소, 연구 대분류, 교과목 소개, 모집 공통 정보는 `content/site.json`에서 관리합니다. 모집 숫자는 원본 페이지들 간 표기가 달라 현재 확정 인원처럼 노출하지 않습니다. 원문 공고 참고에는 확인된 /home 페이지 내용을 보존했습니다. 실제 인원을 확인한 뒤 `recruitment`의 `masters`, `integrated`, `phd`와 `showConfirmedCounts`를 수정하세요.

## 공개 자료만 저장하세요

`공개: false`는 **홈페이지 출력 제외** 기능이지 보안 기능이 아닙니다. Public 저장소의 원본·커밋 이력은 열람될 수 있습니다. 비밀계약서, 신분증, 개인정보, 비공개 연구계획서, 비밀번호, API 키를 올리지 마세요. 논문 PDF의 배포 가능 범위와 사진 게시 동의를 확인하고 불필요한 위치·EXIF 정보도 제거하세요.

배포물에는 검증된 공개 레코드와 연결된 파일만 복사합니다. 원본 `content/`, 관리자 도구, 테스트, 검토 문서는 Pages 배포물에 들어가지 않습니다. 다만 공개 GitHub 저장소에서의 접근은 별개의 문제입니다.

## 로컬 개발 / 재검사

Python 3.11 이상, 표준 라이브러리만 사용합니다. 별도 AI API 키나 서버 데이터베이스가 필요 없습니다.

```text
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/build_preview.py
```

두 번째 명령은 `_site/`를 새로 만듭니다. `_site/index.html` 또는 새로 만든 `MCLab_Preview.html`을 엽니다. 받은 단일 미리보기는 제작 시점의 스냅샷이며 폴더 수정만으로 저절로 갱신되지 않습니다.

## 기존 홈페이지 반영 및 한계

구성원 18명(교수님 포함), 논문 56개 레코드(게재 목록 50 + 미게재 6), 과제 54개(초기 스냅샷 기준), 기존 3개 연구 대분류와 11개 세부 주제, 날짜가 확인된 소식 2건을 반영했습니다. 과거 논문 41건은 원문 권·호·쪽 정보와 주석까지 보완했습니다. 교수님 학력·경력·수상·편집위원·리뷰 활동과 Office E6-212 / Lab E6-115를 보완했습니다.

이미지 주소 접근 제한으로 실사진과 원본 연구 그림을 이관하지 못했습니다. 일부 원본 웹페이지가 이전 내용으로 반환되어 초기 이관 기록과 다른 부분은 임의로 삭제·중복 등록하지 않고 `docs/MIGRATION_REVIEW_KO.md`에 남겼습니다. 이관 레코드 수는 공식 최신 실적 집계가 아닙니다. Teaching은 원본 이관이 아닌 별도 소개 초안입니다.

## 공식 설명과 출처

- GitHub Pages 설정: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Actions Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Desktop 복제: https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop
- 웹 업로드 제한: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
- 원본 MCLab: https://sites.google.com/view/mclab/home
- 상세 이관 기록: docs/MIGRATION_REVIEW_KO.md
