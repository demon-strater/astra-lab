# Astra Lab

Codex에서 작업하고 HTML 사이트에서 결과를 확인하는 개인 실험실입니다. 사이트 버튼이 AI를 호출하는 구조는 아닙니다. 별도 API 키는 필요하지 않습니다.

## 실행

`npm start` → http://127.0.0.1:8010

이미지, GLB, Blender 원본, HTML 실험, 녹화를 `public/assets/` 아래에 저장합니다. `npm run catalog`로 갤러리를 갱신합니다. GLB는 사이트에서 회전/확대 가능하며 .blend는 다운로드용입니다.

`npm run publish`는 결과 파일을 커밋하고 lab에 업로드합니다. `npm run watch`는 실행되어 있는 동안 30초 이상 변하지 않은 결과 파일을 자동 업로드합니다. PC 종료 후에는 다시 실행해야 합니다. 웹 소스 수정은 별도 커밋/푸시가 필요합니다. 95MB 초과 결과물은 업로드를 중단하며 GitHub Release 등 별도 배포가 필요합니다.

## GitHub Pages 초기 설정

GitHub CLI 로그인 후 새 저장소를 만들고 main 브랜치를 push합니다. 저장소 Settings → Pages → Source를 GitHub Actions로 지정합니다. 이후 push마다 사이트가 배포됩니다.

## Blender와 Computer Use

Blender 설치와 Codex Computer Use 연결이 필요합니다. 실제 데스크톱 도구가 연결된 세션에서 Blender를 실행하고 조작해야 합니다. Python 배치 실행은 Computer Use 실험을 대신하지 않습니다.

사이트의 작업 화면 선택 기능은 사용자가 지정한 창을 로컬에서 미리 보고 녹화합니다. 원격 생중계 기능은 아닙니다. 녹화 파일을 public/assets/recordings 아래로 옮기면 자동 게시 대상이 됩니다. 화면 공유와 파일 저장은 브라우저 확인이 필요합니다.

현재 저장소에는 생성 이미지나 Blender 모델 샘플이 없습니다. 이미지 생성 시 imagegen 도구 결과를 파일로 저장하고, Blender 모델은 .blend와 웹 표시용 .glb를 함께 저장하세요.

