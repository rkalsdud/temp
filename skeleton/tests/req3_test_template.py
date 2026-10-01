"""
requirement_3.md 검증 템플릿 스크립트

실행 방법
--------
    # 프로젝트 루트에서
    python tests/req3_test_template.py

선택 환경변수
------------
    CI_MAIN_PUSH_CONFIRMED=true
    CI_HEALTH_CHECK_PASSED=true
    CI_API_TESTS_PASSED=true
    RENDER_DEPLOY_URL=https://your-service.onrender.com

결과
----
    tests/reports/req3_report_template.md
"""

import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
REPORT_DIR = os.path.join(THIS_DIR, "reports")
REPORT_PATH = os.path.join(REPORT_DIR, "req3_report_template.md")
APP_JS_PATH = os.path.join(PROJECT_ROOT, "app", "static", "app.js")
STYLE_CSS_PATH = os.path.join(PROJECT_ROOT, "app", "static", "style.css")

os.chdir(PROJECT_ROOT)
BASE_URL = None

results = []


def check(tc_id, scenario, expected, actual, passed):
    """검증 결과 1건을 기록한다."""
    results.append((tc_id, scenario, expected, actual, passed))
    tag = "PASS" if passed else "FAIL"
    print(f"  [{tag}] {tc_id}  {scenario}")


def http_get(path_or_url, timeout=5):
    """(status_code, json_data/text) 반환. 실패 시 (None, None)."""
    url = path_or_url if path_or_url.startswith("http") else BASE_URL + path_or_url
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            return e.code, json.loads(body) if body else None
        except Exception:
            return e.code, None
    except Exception as e:
        return None, str(e)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_badge_class_function(js_text):
    match = re.search(r"function\s+badgeClass\s*\([^)]*\)\s*\{(?P<body>.*?)\n\}", js_text, re.S)
    return match.group("body") if match else ""


def strip_js_comments(js_text):
    without_block = re.sub(r"/\*.*?\*/", "", js_text, flags=re.S)
    return re.sub(r"//.*", "", without_block)


def css_rule_block(css_text, selector):
    pattern = re.compile(r"(?P<selectors>[^{}]*" + re.escape(selector) + r"[^{}]*)\{(?P<body>[^{}]+)\}", re.S)
    match = pattern.search(css_text)
    if not match:
        return ""
    return match.group("selectors") + "{" + match.group("body") + "}"


def badge_source_maps_value(js_text, value, expected_class):
    body = strip_js_comments(extract_badge_class_function(js_text))
    value_lower = value.lower()
    return value_lower in body.lower() and expected_class in body


def css_has_color_rule(css_text, selector, background, color):
    block = css_rule_block(css_text, selector)
    compact = re.sub(r"\s+", "", block).lower()
    return selector in block and f"background:{background.lower()}" in compact and f"color:{color.lower()}" in compact


def env_true(name):
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "y", "pass", "passed"}


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
    js_text = read_text(APP_JS_PATH)
    css_text = read_text(STYLE_CSS_PATH)

    badge_cases = [
        (
            "TE-01",
            "Active 상태 구독자 확인",
            "초록 badge",
            "Active",
            "badge status-active",
            ".status-active",
            "#dcfce7",
            "#166534",
        ),
        (
            "TE-02",
            "Paused 상태 구독자 확인",
            "파랑 badge",
            "Paused",
            "badge status-paused",
            ".status-paused",
            "#e0e7ff",
            "#3730a3",
        ),
        (
            "TE-03",
            "Expired 상태 구독자 확인",
            "빨강 badge",
            "Expired",
            "badge status-expired",
            ".status-expired",
            "#fee2e2",
            "#991b1b",
        ),
        (
            "TE-04",
            "Online 상태 가전 확인",
            "초록 badge",
            "Online",
            "badge status-active",
            ".status-active",
            "#dcfce7",
            "#166534",
        ),
        (
            "TE-05",
            "Offline 상태 가전 확인",
            "회색 badge",
            "Offline",
            "badge status-offline",
            ".status-offline",
            "#e5e7eb",
            "#374151",
        ),
        (
            "TE-06",
            "Error 상태 가전 확인",
            "빨강 badge",
            "Error",
            "badge status-expired",
            ".status-expired",
            "#fee2e2",
            "#991b1b",
        ),
        (
            "TE-07",
            "Power On 상태 확인",
            "노랑 badge",
            "On",
            "badge status-on",
            ".status-on",
            "#fef3c7",
            "#92400e",
        ),
        (
            "TE-08",
            "Health Normal 상태 확인",
            "초록 badge",
            "Normal",
            "badge status-active",
            ".status-active",
            "#dcfce7",
            "#166534",
        ),
        (
            "TE-09",
            "Health Warning 상태 확인",
            "빨강 badge",
            "Warning",
            "badge status-expired",
            ".status-expired",
            "#fee2e2",
            "#991b1b",
        ),
    ]

    for tc_id, scenario, expected, value, expected_class, selector, bg, fg in badge_cases:
        has_js_mapping = badge_source_maps_value(js_text, value, expected_class)
        has_css_rule = css_has_color_rule(css_text, selector, bg, fg)
        passed = has_js_mapping and has_css_rule
        actual = (
            f'badgeClass("{value}") -> {expected_class} 매핑: {has_js_mapping}, '
            f"CSS {selector} 색상 규칙: {has_css_rule}"
        )
        check(tc_id, scenario, expected, actual, passed)

    # 10. main push 시 CI 자동 실행 > Actions 탭에서 실행 확인
    passed = env_true("CI_MAIN_PUSH_CONFIRMED")
    actual = "확인됨" if passed else "확인 필요: CI_MAIN_PUSH_CONFIRMED=true 설정 후 실행"
    check("CI-01", "main push 시 CI 자동 실행",
          "Actions 탭에서 실행 확인", actual, passed)

    # 11. CI 에서 health 체크 통과 > 초록 체크마크
    local_status, local_body = http_get("/health")
    env_passed = env_true("CI_HEALTH_CHECK_PASSED")
    passed = env_passed and local_status == 200
    actual = (
        f"로컬 /health status={local_status}, body={local_body}, "
        f"CI 확인={env_passed}"
    )
    check("CI-02", "CI에서 health 체크 통과",
          "초록 체크마크", actual, passed)

    # 12. CI 에서 API 테스트 통과 > 3개 엔드포인트 모두 통과
    api_paths = [
        "/api/subscribers",
        "/api/subscribers/U001/devices",
        "/api/devices/D001/usage",
    ]
    statuses = {}
    for path in api_paths:
        status, _ = http_get(path)
        statuses[path] = status
    env_passed = env_true("CI_API_TESTS_PASSED")
    passed = env_passed and all(statuses[path] == 200 for path in api_paths)
    actual = f"로컬 API statuses={statuses}, CI 확인={env_passed}"
    check("CI-03", "CI에서 API 테스트 통과",
          "3개 엔드포인트 모두 통과", actual, passed)

    # 13. CI 통과 후 Render 배포 확인 > 배포 URL 접속 가능
    deploy_url = os.environ.get("RENDER_DEPLOY_URL", "").strip()
    if deploy_url:
        status, body = http_get(deploy_url.rstrip("/") + "/health")
        passed = status == 200
        actual = f"{deploy_url}/health status={status}, body={body}"
    else:
        passed = False
        actual = "확인 필요: RENDER_DEPLOY_URL 환경변수에 배포 URL 설정 후 실행"
    check("DEPLOY-01", "CI 통과 후 Render 배포 확인",
          "배포 URL 접속 가능", actual, passed)


def render_report():
    total = len(results)
    passed = sum(1 for *_, p in results if p)
    failed = total - passed
    rate = (passed / total * 100) if total else 0.0

    lines = []
    lines.append("# requirement_3 검증 Report (TE 실습)")
    lines.append("")
    lines.append("| 항목 | 내용 |")
    lines.append("|------|------|")
    lines.append("| **프로젝트** | webOS Subscription Management Dashboard |")
    lines.append("| **검증 대상** | requirement_3.md |")
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
    lines.append("> 본 Report는 `tests/req3_test_template.py`로 생성되었습니다.")

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return passed, failed, total, rate


def main():
    global BASE_URL
    print("=" * 60)
    print(" requirement_3 검증 (학생용 템플릿)")
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
