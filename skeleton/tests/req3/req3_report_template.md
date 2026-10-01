# requirement_3 검증 Report (TE 실습)

| 항목 | 내용 |
|------|------|
| **프로젝트** | webOS Subscription Management Dashboard |
| **검증 대상** | requirement_3.md |
| **검증 일시** | 2026-10-01 16:49:24 |
| **작성자** | (여기에 이름을 적으세요) |

**총 13건 중 PASS 8 / FAIL 5 - Pass Rate 61.5%**

| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |
|:-----:|----------------|-----------|-----------|:----:|
| TE-01 | Active 상태 구독자 확인 | 초록 badge | badgeClass("Active") -> badge status-active 매핑: True, CSS .status-active 색상 규칙: True | PASS |
| TE-02 | Paused 상태 구독자 확인 | 파랑 badge | badgeClass("Paused") -> badge status-paused 매핑: True, CSS .status-paused 색상 규칙: True | PASS |
| TE-03 | Expired 상태 구독자 확인 | 빨강 badge | badgeClass("Expired") -> badge status-expired 매핑: True, CSS .status-expired 색상 규칙: True | PASS |
| TE-04 | Online 상태 가전 확인 | 초록 badge | badgeClass("Online") -> badge status-active 매핑: True, CSS .status-active 색상 규칙: True | PASS |
| TE-05 | Offline 상태 가전 확인 | 회색 badge | badgeClass("Offline") -> badge status-offline 매핑: True, CSS .status-offline 색상 규칙: True | PASS |
| TE-06 | Error 상태 가전 확인 | 빨강 badge | badgeClass("Error") -> badge status-expired 매핑: True, CSS .status-expired 색상 규칙: True | PASS |
| TE-07 | Power On 상태 확인 | 노랑 badge | badgeClass("On") -> badge status-on 매핑: True, CSS .status-on 색상 규칙: False | FAIL |
| TE-08 | Health Normal 상태 확인 | 초록 badge | badgeClass("Normal") -> badge status-active 매핑: True, CSS .status-active 색상 규칙: True | PASS |
| TE-09 | Health Warning 상태 확인 | 빨강 badge | badgeClass("Warning") -> badge status-expired 매핑: True, CSS .status-expired 색상 규칙: True | PASS |
| CI-01 | main push 시 CI 자동 실행 | Actions 탭에서 실행 확인 | 확인 필요: CI_MAIN_PUSH_CONFIRMED=true 설정 후 실행 | FAIL |
| CI-02 | CI에서 health 체크 통과 | 초록 체크마크 | 로컬 /health status=200, body={'status': 'ok'}, CI 확인=False | FAIL |
| CI-03 | CI에서 API 테스트 통과 | 3개 엔드포인트 모두 통과 | 로컬 API statuses={'/api/subscribers': 200, '/api/subscribers/U001/devices': 200, '/api/devices/D001/usage': 200}, CI 확인=False | FAIL |
| DEPLOY-01 | CI 통과 후 Render 배포 확인 | 배포 URL 접속 가능 | 확인 필요: RENDER_DEPLOY_URL 환경변수에 배포 URL 설정 후 실행 | FAIL |

> 본 Report는 `tests/req3_test_template.py`로 생성되었습니다.
