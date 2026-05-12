# SiteGuard Infra — Agent Behavioral Contract

## WHY (핵심 철학)

이동형 CCTV 관제 솔루션 상용화 — 인프라 레이어. 1인 개발.

**불변 원칙 2가지:**
1. **에지 자립**: 클라우드 장애 시에도 감지·저장·관제 완결
2. **클라우드 경량**: 요약 이벤트·상태만 상시 수신, 상세는 필요 시 pull

> 모든 설계 결정은 이 두 원칙을 기준으로 판단한다.

---

## WHAT (기술 스택)

| 레이어 | 서비스 | 실행 위치 |
|--------|--------|----------|
| 관제 플랫폼 | Thingsboard 4.2.1.1 (Docker) | Hetzner |
| 라이브뷰 | go2rtc + Nginx 역방향 프록시 | Hetzner |
| 커스텀 UI | HTML/JS → TB jar 패치 | Hetzner 작성, jar에 삽입 |
| 감지·녹화 | Frigate (Docker) | 에지 PC (visionlinux) |
| 텔레메트리 브리지 | Python MQTT 스크립트 | 에지 PC |

**언어·도구:** Python 3, Vanilla JS (빌드 도구 없음), Docker, paho-mqtt, requests

---

## HOW (워크플로우)

### 세션 분리 규칙 — 작업 시작 전 반드시 확인
```
에지 PC에서 실행되는 서비스?  →  visionlinux 세션
클라우드에서 실행되는 서비스? →  이 세션 (Hetzner root@46.62.155.122)
```
코드는 항상 Hetzner에서 작성 → `git push` → 에지 PC `git pull` → 실행

### UI 변경 워크플로우 (TB jar 패치)
```bash
# 1. siteguard-ui/ 파일 수정
# 2. 패치 실행
python3 temp/patch_siteguard_ui.py
# 3. TB 재시작
docker restart thingsboard
# 4. 검증 (아래 Verification 참고)
```

### 파일 생성 규칙
- `"만들어줘"` → 바로 생성
- 그 외 신규 파일 → 먼저 의견 제시 후 확인받고 생성

### 응답 언어
한국어

---

## Verification (자가 검증)

작업 완료 후 반드시 아래 명령으로 성공 여부 확인:

```bash
# TB 정상 기동 확인
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/

# sg-inject.js 서빙 확인
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/sg-inject.js

# UI 변경 반영 확인 (Playwright)
python3 -c "
from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox'])
    pg = b.new_page()
    pg.goto('http://localhost:8080/login')
    pg.fill('input[formcontrolname=\"username\"]', 'tenant@thingsboard.org')
    pg.fill('input[formcontrolname=\"password\"]', 'tenant')
    pg.click('button[type=\"submit\"]')
    pg.wait_for_url('**/home', timeout=20000)
    pg.goto('http://localhost:8080/entities/devices')
    pg.wait_for_load_state('networkidle', timeout=20000)
    time.sleep(2)
    pg.locator('mat-row').filter(has_text='cctv-1').first.click()
    time.sleep(5)
    r = pg.evaluate(\"({hidden: !!document.querySelector('mat-tab-group[style*=none]'), iframe: !!document.querySelector('iframe.sg-cam-frame')})\")
    print('탭 숨김:', r['hidden'], '| iframe:', r['iframe'])
    b.close()
"

# Docker 서비스 전체 상태
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

**UI 변경 검증 기준:** `탭 숨김: True | iframe: True`

---

## Stop Conditions (인간 개입 요청)

다음 상황에서는 **반드시 중단하고 확인 요청:**

- `git push` / `git push --force` 실행 전
- `docker rm`, `docker rmi`, 볼륨 삭제 등 복구 불가 작업
- TB 서비스가 재시작 후 3분 내 200 응답 안 할 때
- 에지 PC 대상 스크립트를 Hetzner에서 직접 실행하려 할 때
- API 키·비밀번호·토큰이 코드에 하드코딩되려 할 때

---

## Progressive Disclosure (상세 참고)

| 궁금한 것 | 참고 문서 |
|----------|----------|
| 전체 작업 이력·현황 | `doc/walkthrough.md` |
| 아키텍처 로드맵 | `doc/system-architecture-roadmap.md` |
| LTE 라우터 제약 | `doc/lte-router-considerations.md` |
| 카메라 UI 설계 의도 | `doc/camera-management-ui-design.md` |
| 현재 기기 목록·속성 | `thingsboard/scripts/tb_siteguard_full_setup.py` > `CAMERAS` |
