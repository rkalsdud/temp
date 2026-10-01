"""
requirement_2.md 검증 템플릿 스크립트

실행 방법
--------
    # 프로젝트 루트에서
    python tests/req2_test_template.py

결과
----
    tests/reports/req2_report_template.md
"""

import os
import sys
import time
import json
import socket
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
REPORT_DIR = os.path.join(THIS_DIR, "reports")
REPORT_PATH = os.path.join(REPORT_DIR, "req2_report_template.md")

os.chdir(PROJECT_ROOT)
BASE_URL = None

results = []


def check(tc_id, scenario, expected, actual, passed):
    """검증 결과 1건을 기록한다."""
    results.append((tc_id, scenario, expected, actual, passed))
    tag = "PASS" if passed else "FAIL"
    print(f"  [{tag}] {tc_id}  {scenario}")


def http_get(path, timeout=5):
    """(status_code, json_data) 반환. 실패 시 (None, None)."""
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            return e.code, json.loads(body) if body else None
        except Exception:
            return e.code, None
    except Exception:
        return None, None


def filter_devices(devices, search="", status=""):
    """app.js renderDevices()와 같은 검색/상태 필터 규칙을 데이터로 재현한다."""
    s = (search or "").lower()
    out = []
    for d in devices:
        matches_search = (
            s in d["type"].lower()
            or s in d["model"].lower()
            or s in d["status"].lower()
            or s in d["deviceId"].lower()
            or s in d["location"].lower()
        )
        matches_status = (not status) or d["status"] == status
        if matches_search and matches_status:
            out.append(d)
    return out


def device_empty_message(original_devices, filtered_devices):
    """renderDevices()에서 보여야 하는 안내 메시지를 데이터로 계산한다."""
    if len(original_devices) == 0:
        return "No registered devices"
    if len(filtered_devices) == 0:
        return "No devices matched"
    return ""


def usage_detail_fields(usage):
    """selectDevice()가 화면에 표시해야 하는 주요 사용 현황 필드."""
    if not isinstance(usage, dict):
        return {}
    return {
        "Device ID": usage.get("deviceId"),
        "Device Name": usage.get("deviceName"),
        "Power Status": usage.get("powerStatus"),
        "Last Used": usage.get("lastUsedAt"),
        "Total Usage Hours": usage.get("totalUsageHours"),
        "Weekly Usage Count": usage.get("weeklyUsageCount"),
        "Health Status": usage.get("healthStatus"),
        "Remark": usage.get("remark"),
    }


def render_chart_state(previous_chart, trend):
    """renderUsageChart()의 핵심 동작을 검증하기 위한 차트 상태 시뮬레이션."""
    destroyed_previous = previous_chart is not None
    return {
        "destroyed_previous": destroyed_previous,
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "data": trend,
    }


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(port):
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for _ in range(40):
        if proc.poll() is not None:
            return proc, False
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as r:
                if r.status == 200:
                    return proc, True
        except Exception:
            time.sleep(0.5)
    return proc, False


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def run_tests():
    # 1. /api/subscribers/U001/devices 호출 > 2개 가전 JSON 반환
    u001_status, u001_devices = http_get("/api/subscribers/U001/devices")
    u001_devices = u001_devices if isinstance(u001_devices, list) else []
    ids = [d.get("deviceId") for d in u001_devices]
    passed = u001_status == 200 and len(u001_devices) == 2 and ids == ["D001", "D002"]
    check("API-01", "/api/subscribers/U001/devices 호출",
          "D001, D002 2개 가전 JSON 반환", f"status={u001_status}, {len(u001_devices)}개 {ids}", passed)

    # 2. /api/subscribers/U005/devices 호출 > 빈 배열 [] 반환
    u005_status, u005_devices = http_get("/api/subscribers/U005/devices")
    passed = u005_status == 200 and u005_devices == []
    check("API-02", "/api/subscribers/U005/devices 호출",
          "빈 배열 [] 반환", f"status={u005_status}, body={u005_devices}", passed)

    # 3. /api/subscribers/U999/devices 호출 > 404 에러 반환
    status, body = http_get("/api/subscribers/U999/devices")
    passed = status == 404
    check("API-03", "/api/subscribers/U999/devices 호출",
          "404 에러 반환", f"status={status}, body={body}", passed)

    # 4. U001 클릭 시 가전 Table 표시 > D001, D002 표시
    filtered = filter_devices(u001_devices)
    ids = [d["deviceId"] for d in filtered]
    passed = u001_status == 200 and len(filtered) == 2 and ids == ["D001", "D002"]
    check("TE-01", "U001 클릭 시 가전 Table 표시",
          "D001, D002 표시", f"{len(filtered)}개 {ids}", passed)

    # 5. U005 클릭 시 안내 메시지 > "No registered devices" 표시
    safe_u005_devices = u005_devices if isinstance(u005_devices, list) else []
    filtered = filter_devices(safe_u005_devices)
    msg = device_empty_message(safe_u005_devices, filtered)
    passed = u005_status == 200 and u005_devices == [] and msg == "No registered devices"
    check("TE-02", "U005 클릭 시 안내 메시지 표시",
          '"No registered devices" 표시', msg or "(메시지 없음)", passed)

    # 6. 가전 검색 "TV" 입력 > TV 타입만 표시
    all_devices = []
    for user_id in ["U001", "U002", "U003", "U004", "U005"]:
        status, body = http_get(f"/api/subscribers/{user_id}/devices")
        if status == 200 and isinstance(body, list):
            all_devices.extend(body)
    filtered = filter_devices(all_devices, search="TV")
    ids = [d["deviceId"] for d in filtered]
    passed = len(filtered) == 2 and set(ids) == {"D001", "D004"} and all(
        d["type"] == "TV" for d in filtered
    )
    check("TE-03", '가전 검색 "TV" 입력',
          "TV 타입만 표시", f"{len(filtered)}개 {ids}", passed)

    # 7. 가전 상태 필터 "Online" 선택 > Online 가전만 표시
    filtered = filter_devices(all_devices, status="Online")
    ids = [d["deviceId"] for d in filtered]
    passed = len(filtered) == 5 and set(ids) == {"D001", "D003", "D004", "D005", "D007"} and all(
        d["status"] == "Online" for d in filtered
    )
    check("TE-04", '가전 상태 필터 "Online" 선택',
          "Online 가전만 표시", f"{len(filtered)}개 {ids}", passed)

    # 8. /api/devices/D001/usage 호출 > 사용 현황 JSON 반환
    status, d001_usage = http_get("/api/devices/D001/usage")
    required = {
        "deviceId",
        "deviceName",
        "powerStatus",
        "lastUsedAt",
        "totalUsageHours",
        "weeklyUsageCount",
        "healthStatus",
        "remark",
        "weeklyUsageTrend",
    }
    passed = (
        status == 200
        and isinstance(d001_usage, dict)
        and d001_usage.get("deviceId") == "D001"
        and required.issubset(d001_usage.keys())
    )
    actual = f"status={status}, keys={sorted(d001_usage.keys())}" if isinstance(d001_usage, dict) else f"status={status}, body={d001_usage}"
    check("API-04", "/api/devices/D001/usage 호출",
          "D001 사용 현황 JSON 반환", actual, passed)

    # 9. /api/devices/D999/usage 호출 > 404 에러 반환
    status, body = http_get("/api/devices/D999/usage")
    passed = status == 404
    check("API-05", "/api/devices/D999/usage 호출",
          "404 에러 반환", f"status={status}, body={body}", passed)

    # 10. D001 클릭 시 사용 현황 표시 > 전원상태, 누적시간 등 표시
    fields = usage_detail_fields(d001_usage)
    passed = (
        fields.get("Power Status") == "On"
        and fields.get("Total Usage Hours") == 152
        and fields.get("Weekly Usage Count") == 18
        and fields.get("Health Status") == "Normal"
    )
    check("TE-05", "D001 클릭 시 사용 현황 표시",
          "전원상태, 누적시간, 주간 사용 횟수, 건강 상태 표시",
          f"Power={fields.get('Power Status')}, Hours={fields.get('Total Usage Hours')}, Weekly={fields.get('Weekly Usage Count')}",
          passed)

    # 11. D001 클릭 시 Bar Chart 표시 > 요일별 사용량 차트
    trend = d001_usage.get("weeklyUsageTrend") if isinstance(d001_usage, dict) else None
    chart = render_chart_state(None, trend)
    passed = (
        isinstance(trend, list)
        and len(trend) == 7
        and chart["labels"] == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        and chart["data"] == [2, 3, 1, 4, 2, 3, 3]
    )
    check("TE-06", "D001 클릭 시 Bar Chart 표시",
          "요일별 사용량 차트 표시", f"labels={chart['labels']}, data={chart['data']}", passed)

    # 12. 다른 가전 클릭 시 차트 갱신 > 이전 차트 제거, 새 차트 표시
    status, d002_usage = http_get("/api/devices/D002/usage")
    d002_trend = d002_usage.get("weeklyUsageTrend") if isinstance(d002_usage, dict) else None
    next_chart = render_chart_state(chart, d002_trend)
    passed = (
        status == 200
        and next_chart["destroyed_previous"] is True
        and next_chart["data"] == [0, 1, 0, 1, 1, 0, 1]
        and next_chart["data"] != chart["data"]
    )
    check("TE-07", "다른 가전 D002 클릭 시 차트 갱신",
          "이전 차트 제거 후 새 차트 표시",
          f"destroyed_previous={next_chart['destroyed_previous']}, data={next_chart['data']}",
          passed)


def render_report():
    total = len(results)
    passed = sum(1 for *_, p in results if p)
    failed = total - passed
    rate = (passed / total * 100) if total else 0.0

    lines = []
    lines.append("# requirement_2 검증 Report (TE 실습)")
    lines.append("")
    lines.append("| 항목 | 내용 |")
    lines.append("|------|------|")
    lines.append("| **프로젝트** | webOS Subscription Management Dashboard |")
    lines.append("| **검증 대상** | requirement_2.md |")
    lines.append(f"| **검증 일시** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    lines.append("| **작성자** | (여기에 이름을 적으세요) |")
    lines.append("")
    lines.append(f"**총 {total}건 중 PASS {passed} / FAIL {failed} - Pass Rate {rate:.1f}%**")
    lines.append("")
    lines.append("| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |")
    lines.append("|:-----:|----------------|-----------|-----------|:----:|")
    for tc_id, scenario, expected, actual, passed_ in results:
        mark = "PASS" if passed_ else "FAIL"
        lines.append(f"| {tc_id} | {scenario} | {expected} | {actual} | {mark} |")
    lines.append("")
    lines.append("> 본 Report는 `tests/req2_test_template.py`로 생성되었습니다.")

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return passed, failed, total, rate


def main():
    global BASE_URL
    print("=" * 60)
    print(" requirement_2 검증 (학생용 템플릿)")
    print("=" * 60)

    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

    port = find_free_port()
    print(f"[서버 기동] 127.0.0.1:{port} ...")
    proc, ok = start_server(port)
    if not ok:
        print("[오류] 서버 기동 실패. requirements 설치 및 app/main.py를 확인하세요.")
        stop_server(proc)
        sys.exit(1)

    BASE_URL = f"http://127.0.0.1:{port}"
    print("[서버 기동] 성공\n")

    try:
        run_tests()
    finally:
        stop_server(proc)

    passed, failed, total, rate = render_report()
    print("\n" + "=" * 60)
    print(f" 결과: PASS {passed} / FAIL {failed} (총 {total}) - {rate:.1f}%")
    print(f" Report 저장: {os.path.relpath(REPORT_PATH, PROJECT_ROOT)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
