# MCLab · 원본 사진 반영 / Teaching 제거 버전

2026-10-10 수정. 사용자 제공 Webpages.zip의 원본 사진과 연구 그림을 사용했습니다.

## 확인할 파일
- `docs/MCLab_Original_Photos_Guide_KO.html`: 이번 버전의 적용·관리 안내
- `docs/MCLab_Photo_Name_Check.html`: 파일명에 이름이 없는 사진의 이름 확인
- `docs/ORIGINAL_PHOTO_MAPPING.csv`: 원본 파일명과 새 파일 위치
- `admin/info-helper.html`: 기존 정보 파일 작성 도구

## 변경사항
- 교수님 포함 13명 원본 사진, 연구 주제 11개 원본 그림, 갤러리 8개.
- Home에 원본 실험 플랫폼·시뮬레이터·단체 사진, 생일 소식에 원본 행사 사진.
- Teaching 메뉴·라우트·데이터·배포 페이지 제거.
- 원본은 손대지 않고 웹용 사본만 생성했습니다. 파일명과 원본 SHA-256을 대응표에 기록했습니다.
- 사진이 확인되지 않은 5명의 프로필은 이니셜로 유지합니다. 임의 인물 연결을 하지 않았습니다.

## 최초 적용
1. 현재 저장소를 백업합니다. 최근 수정한 content 정보가 있다면 이번 파일과 먼저 병합하세요.
2. 이 폴더의 내용 전체를 저장소 루트에 반영합니다. `.github/`가 반드시 포함되어야 합니다.
3. 기존 저장소의 `teaching.html`을 삭제합니다.
4. Pages의 Source는 기존과 같이 **GitHub Actions**로 둡니다.
5. Commit/Push 후 Actions의 검증·배포 성공을 확인합니다.

이 패키지는 계정 로그인·원격 저장소 수정·라이브 배포를 이미 수행한 결과가 아닙니다.

## 평소 관리
학생별 `content/people/<id>/info.txt`와 `photo.jpg`, 논문별 `content/publications/<id>/info.txt`, 과제별 `content/projects/<id>/info.txt`를 수정해 GitHub에 반영합니다. 기존 자동 업데이트 방식은 그대로입니다. 공개 정보·공개 가능한 사진만 넣으세요.

## 로컬 빌드 (Python 3.11 이상, 표준 라이브러리)
```sh
python -m unittest discover -s tests -v
python scripts/build_site.py
python scripts/build_preview.py --output MCLab_Preview.html
```
새 결과는 `_site/`에 생성됩니다. `data/site-data.js`는 최초 로컬 열람용 스냅샷입니다. 실배포는 content에서 새 데이터를 생성하므로 스냅샷을 수동 수정하지 마세요.

## 검증 결과
`docs/`의 현재 보고서를 확인하세요. `docs/history/`는 원본 사진을 받기 전의 과거 자료이므로 현재 상태 설명으로 사용하지 마세요.
