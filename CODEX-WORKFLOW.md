# 실험 작업 지침

이 프로젝트의 사용자 요청은 실험 결과를 GitHub에 자동 게시하는 것을 포함합니다.

- 새 작업을 시작할 때 이 파일과 README.md를 읽습니다.
- 공개 게시 대상은 public/ 아래 파일입니다. 인증 정보, 개인 화면, 다른 프로젝트 파일을 저장하지 않습니다.
- 이미지 생성 결과는 public/assets/images/에 복사합니다.
- Blender 결과는 public/assets/models/에 .blend와 웹 뷰어용 .glb를 함께 저장합니다.
- HTML 실험은 public/assets/experiments/<실험명>/index.html에 저장합니다.
- 사용자 요청으로 기록한 작업 영상은 public/assets/recordings/에 저장합니다.
- 실제 Computer Use 도구가 연결되어 있을 때 Blender UI를 열어 작업합니다. 연결되지 않았다면 사용자에게 연결을 요청하고 UI 조작을 했다고 주장하지 않습니다.
- 파일 저장 완료 후 npm run publish를 실행하고 성공 여부를 확인합니다. 자동 감시가 실행 중이면 중복 커밋을 피합니다.
- 사이트 소스를 수정하면 검증 후 관련 파일만 커밋하고 git push lab HEAD:main을 실행합니다.
- lab은 공개 astra-lab 저장소이며 origin은 기존 비공개 저장소입니다. 배포에는 lab만 사용합니다.
- .blend 등 95MB 초과 파일은 자동 게시가 중단됩니다. 필요한 경우 별도의 GitHub Release 업로드를 구현하고 다운로드 링크를 갤러리에 반영합니다.
- 사이트 화면 공유는 로컬 녹화 기능입니다. 원격 시청자가 PC 화면을 생중계로 볼 수 있는 기능으로 설명하지 않습니다.
