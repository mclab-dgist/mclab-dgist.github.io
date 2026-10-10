# MCLab 최초 설치 및 폴더 업데이트

## 현재 상태

이 커밋에는 안전한 ZIP 설치기와 자동 배포 설정이 들어 있습니다. 사진과 홈페이지 본체는 아직 업로드되지 않았습니다. ZIP이 없는 동안 기존 공개 사이트는 변경하지 않습니다.

## 최초 한 번: ZIP 하나 업로드

1. 저장소의 `main` 브랜치에서 `Add file → Upload files`를 엽니다.
2. ChatGPT에서 받은 **MCLab_Original_Photos_No_Teaching.zip** 파일 하나를 저장소 최상위에 업로드하고 Commit changes를 누릅니다. 압축을 풀거나 이름을 바꾸지 마세요.
3. `Actions → Install and deploy MCLab`에서 실행 결과를 확인합니다.

설치기는 승인된 ZIP의 SHA-256을 확인하고 240개 원본 파일을 `mclab/` 폴더에 풀어 저장합니다. 홈페이지 테스트와 빌드가 성공해야 소스를 main에 커밋하고, 완성된 사이트만 gh-pages에 배포합니다. 원본 사진을 다른 그림으로 바꾸지 않습니다. Teaching은 새 사이트에 포함되지 않습니다.

예상 SHA-256:
`7ed71aa5ad4abfca8d0d3c4fa174d4968266db6db6f95968358bd6c1209aed55`

## Pages 설정

이 저장소에 있던 `gh-pages` 브랜치 배포 방식을 사용합니다. 공개 주소가 바뀌지 않는 경우 Settings → Pages에서 **Deploy from a branch → gh-pages → /(root)**인지 확인하세요. Source가 GitHub Actions인 경우에는 이 브랜치 방식으로 맞추어야 합니다. 아직 실제 공개 완료를 확인한 것은 아닙니다.

## 이후 폴더 관리

- 학생 정보·사진: `mclab/content/people/학생-id/`
- 논문 정보·첨부: `mclab/content/publications/논문-id/`
- 과제 정보·첨부: `mclab/content/projects/과제-id/`
- 연구 그림: `mclab/content/research/연구-id/`
- 기본 설정: `mclab/content/site.json`

각 폴더의 `info.txt`와 사진을 수정하고 main에 Commit하면 자동 검증·생성·배포가 실행됩니다. 최초 ZIP은 이후 수정한 폴더를 덮어쓰지 않습니다. `mclab/.mclab-import.json` 설치 기록은 삭제하지 마세요.

과거 al-folio 소스는 안전을 위해 그대로 남아 있지만, 최초 설치 후 배포하는 것은 `mclab/_site`뿐입니다. 완성 사이트에 기존 Teaching 페이지가 남지 않도록 gh-pages 배포는 clean 모드로 실행합니다. Git 기록과 백업 브랜치로 이전 상태를 복원할 수 있습니다.

## 검수 범위

로컬에서 설치기 테스트 12개, 홈페이지 테스트 37개를 통과했습니다. 실제 ZIP의 240개 파일이 바이트 단위로 동일하게 복원되는 것과 후속 수정의 보존을 검사했습니다. GitHub에서의 최초 ZIP 설치와 실제 공개 사이트 확인은 별도 단계입니다.

공개 저장소에 업로드한 파일은 저장소에서도 공개됩니다. 비공개 계약서나 개인정보를 추가하지 마세요. 비밀번호나 개인 액세스 토큰을 이 문서 또는 채팅에 입력할 필요가 없습니다.
