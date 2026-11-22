# MCLab 홈페이지 · 현재 기준 관리

기준일: **2026-11-22**. 저장소는 `mclab-dgist/mclab-dgist.github.io`,
공개 주소는 <https://mclab-dgist.github.io/>입니다.

## 하나의 원본만 수정

현재 승인된 홈페이지 내용을 기준으로, **`main` 브랜치의 `mclab/content/`가
공개 정보의 유일한 수정 원본**입니다. 과거 패키지, 로컬 복사본, 미리보기,
과거 대화의 내용으로 현재 정보를 덮어쓰지 않습니다.

아래 경로는 모두 `mclab/` 기준입니다.

| 수정 대상 | 원본 경로 |
| --- | --- |
| 홈페이지 기본 설정·연구 프로그램 | `content/site.json` |
| 교수·구성원 정보와 사진 | `content/people/<id>/` |
| 연구 설명과 대표 그림 | `content/research/<id>/` |
| 논문·원고 정보 | `content/publications/<id>/` |
| 진행·종료 과제 정보 | `content/projects/<id>/` |
| 소식·갤러리 정보와 사진 | `content/news/<id>/`, `content/gallery/<id>/` |
| 화면 표현 | 해당 HTML 템플릿과 `assets/` |
| 승인 기준 확인 | `quality/approved-baseline.json` |

`gh-pages` 브랜치와 `_site/`는 원본으로부터 생성된 배포 결과입니다.
직접 수정하거나 `content/`로 역복사하지 않습니다. 생성된
`_site/data/site-data.js`도 수동 편집하지 않습니다.

## 변경 절차

1. 최신 `main`과 현재 공개 내용을 확인하고, 사용자가 요청한 항목만 수정합니다.
2. 정보 파일과 연결된 사진·그림을 확인합니다. 기존 항목을 무관하게 교체하거나
   과거 파일 묶음으로 폴더 전체를 덮어쓰지 않습니다.
3. 의도한 변경을 검토한 뒤 `quality/approved-baseline.json`에서 **그 변경에
   해당하는 항목만** 함께 갱신합니다. 검증 통과를 위해 승인 기준 전체를
   자동 재생성하거나 검증을 우회하지 않습니다.
4. 아래 테스트·빌드·승인 검증을 실행하고 생성 화면을 확인합니다.
5. 승인된 원본 변경을 반영한 뒤 GitHub Actions 결과와 공개 홈페이지의 실제
   내용을 확인합니다. 빌드 성공만으로 공개 반영 완료라고 판단하지 않습니다.

현재 목록에 있는 과거 연도 논문과 종료 과제는 유효한 연구실 실적입니다.
**오래된 버전 정리는 오래된 연도의 연구실적 삭제를 의미하지 않습니다.**

## 로컬 검증과 미리보기

Python 3.11 이상과 표준 라이브러리를 사용합니다. 저장소 루트에서 실행합니다.

```bash
cd mclab
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 scripts/verify_approved_release.py
```

미리보기는 방금 생성된 `_site/` 또는 그 결과로 새로 만든 단일 HTML만 사용합니다.
원본 `index.html` 등을 직접 열거나 예전 미리보기 파일을 재사용하지 않습니다.

```bash
python3 -m http.server 8000 --directory _site
```

위 서버로 <http://localhost:8000/>을 확인할 수 있습니다. 별도 단일 파일이
필요하면 빌드 후 다음 명령을 실행합니다. 미리보기는 배포 원본이 아니므로
저장소에 커밋하지 않습니다.

```bash
python3 scripts/build_preview.py --output /tmp/MCLab_Preview.html
```

검증 실패 시 원본 또는 해당 변경의 승인 여부를 확인합니다. 오래된 검증
보고서의 성공 기록을 현재 테스트 결과 대신 사용하지 않습니다.

## 보존과 안전

- 오래된 설치 ZIP, 별도 데이터 사본, 과거 검증·이관 보고서는 현재 작업에서
  사용하지 않습니다. 설치를 다시 실행하거나 옛 패키지로 복구하지 않습니다.
- `.mclab-import.json` 설치 표식, 설치 도구, 배포 워크플로는 유지합니다.
- 사진 원본의 대응 기록은 `docs/ORIGINAL_PHOTO_MAPPING.csv`와
  `docs/ORIGINAL_PHOTO_MAPPING.json`에서 확인합니다. 이는 사진 출처 기록이며
  현재 인물·연구 목록의 원본은 아닙니다. 신원이 불확실한 사진은 임의로
  연결하지 않습니다.
- `admin/info-helper.html`은 정보 파일 작성 보조 도구입니다. 작성 후 원본
  파일에 반영하고 위 검증 절차를 따릅니다.
- 공개 저장소에는 공개 가능한 정보·사진만 올립니다. `공개: false`는
  홈페이지 표시만 제어하며 저장소 파일 자체를 비공개로 만들지 않습니다.
- 현재 브랜치의 낡은 사본 제거와 Git 변경이력 영구 삭제는 별개입니다.
  Git 이력은 복구를 위해 유지하며, 이 안내서는 이력 재작성이나 강제 푸시를
  지시하지 않습니다.
