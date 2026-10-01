# requirement_1 검증 Report (TE 실습)

| 항목 | 내용 |
|------|------|
| **프로젝트** | webOS Subscription Management Dashboard |
| **검증 대상** | requirement_1.md |
| **검증 일시** | 2026-10-01 16:19:02 |
| **작성자** | (여기에 이름을 적으세요) |

**총 9건 중 PASS 9 / FAIL 0 — Pass Rate 100.0%**

| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |
|:-----:|----------------|-----------|-----------|:----:|
| DEV-01 | get_subscribers() 함수 직접 호출 | 5명 반환 | 5명 반환 | ✅ PASS |
| API-01 | GET /api/subscribers 호출 | 200 OK | status=200 | ✅ PASS |
| TE-1 | /api/subscribers 호출 | 5명의 사용자 목록 반환 | 5명 | ✅ PASS |
| TE-3 | 검색창에 "Kim" 입력 | Kim Minsoo만 표시 | 1명: ['Kim Minsoo'] | ✅ PASS |
| TE-4 | 검색창에 "Premium" 입력 | Premium 플랜 사용자만 표시 | 2명 ['Kim Minsoo', 'Choi Sumin'] | ✅ PASS |
| TE-5 | 상태 필터 "Active" 선택 | Active 사용자만 표시 | 3명 ['Kim Minsoo', 'Lee Jiyoon', 'Choi Sumin'] | ✅ PASS |
| TE-6 | 상태 필터 "Expired" 선택 | Jung Hyerin만 표시 | 1명 ['Jung Hyerin'] | ✅ PASS |
| TE-7 | 검색어 "Premium" + 상태 필터 "Active" 동시 적용 | Premium 플랜이면서 Active인 사용자만 표시 | 2명 ['Kim Minsoo', 'Choi Sumin'] | ✅ PASS |
| TE-8 | 검색어 삭제 및 상태 필터 초기화 | 전체 목록 복원 | 5명 ['Kim Minsoo', 'Lee Jiyoon', 'Park Junho', 'Choi Sumin', 'Jung Hyerin'] | ✅ PASS |

> 본 Report 는 `tests/req1_test_template.py` 로 생성되었습니다.
