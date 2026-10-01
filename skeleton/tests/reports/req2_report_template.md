# requirement_2 검증 Report (TE 실습)

| 항목 | 내용 |
|------|------|
| **프로젝트** | webOS Subscription Management Dashboard |
| **검증 대상** | requirement_2.md |
| **검증 일시** | 2026-10-01 16:34:47 |
| **작성자** | (여기에 이름을 적으세요) |

**총 12건 중 PASS 12 / FAIL 0 - Pass Rate 100.0%**

| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |
|:-----:|----------------|-----------|-----------|:----:|
| API-01 | /api/subscribers/U001/devices 호출 | D001, D002 2개 가전 JSON 반환 | status=200, 2개 ['D001', 'D002'] | PASS |
| API-02 | /api/subscribers/U005/devices 호출 | 빈 배열 [] 반환 | status=200, body=[] | PASS |
| API-03 | /api/subscribers/U999/devices 호출 | 404 에러 반환 | status=404, body={'detail': 'User not found'} | PASS |
| TE-01 | U001 클릭 시 가전 Table 표시 | D001, D002 표시 | 2개 ['D001', 'D002'] | PASS |
| TE-02 | U005 클릭 시 안내 메시지 표시 | "No registered devices" 표시 | No registered devices | PASS |
| TE-03 | 가전 검색 "TV" 입력 | TV 타입만 표시 | 2개 ['D001', 'D004'] | PASS |
| TE-04 | 가전 상태 필터 "Online" 선택 | Online 가전만 표시 | 5개 ['D001', 'D003', 'D004', 'D005', 'D007'] | PASS |
| API-04 | /api/devices/D001/usage 호출 | D001 사용 현황 JSON 반환 | status=200, keys=['deviceId', 'deviceName', 'healthStatus', 'lastUsedAt', 'powerStatus', 'remark', 'totalUsageHours', 'weeklyUsageCount', 'weeklyUsageTrend'] | PASS |
| API-05 | /api/devices/D999/usage 호출 | 404 에러 반환 | status=404, body={'detail': 'Device not found'} | PASS |
| TE-05 | D001 클릭 시 사용 현황 표시 | 전원상태, 누적시간, 주간 사용 횟수, 건강 상태 표시 | Power=On, Hours=152, Weekly=18 | PASS |
| TE-06 | D001 클릭 시 Bar Chart 표시 | 요일별 사용량 차트 표시 | labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], data=[2, 3, 1, 4, 2, 3, 3] | PASS |
| TE-07 | 다른 가전 D002 클릭 시 차트 갱신 | 이전 차트 제거 후 새 차트 표시 | destroyed_previous=True, data=[0, 1, 0, 1, 1, 0, 1] | PASS |

> 본 Report는 `tests/req2_test_template.py`로 생성되었습니다.
