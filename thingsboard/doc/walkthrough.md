# Thingsboard 운영 문서 (Walkthrough)

> 문서 성격: 운영 변경 이력 + 트러블슈팅 모음
> 섹션 1 (현황 스냅샷)은 작업할 때마다 **덮어쓴다.**
> 섹션 3 (변경 이력)은 **위에 추가만** 한다. 수정하지 않는다.
> 섹션 2, 4는 새로운 교훈·문제가 생길 때만 추가한다.

---

## 섹션 1 — 현재 운영 현황 스냅샷

> 마지막 업데이트: 2026-04-13
> 이 섹션만 읽으면 현재 시스템 상태를 파악할 수 있다.

### 1-1. 컨테이너 상태

```
[클라우드: Hetzner 46.62.155.122]  ← 운영 기준
thingsboard  Up  — 포트 8080(웹/REST), 1884(MQTT), 7070(Edge RPC)

[로컬 PC: 192.168.0.15]  ← 테스트 전용
thingsboard  (필요 시 기동)
```

### 1-2. 핵심 설정값

| 항목 | 현재 값 |
|---|---|
| 이미지 | thingsboard/tb-postgres:4.2.1.1 |
| 큐 방식 | in-memory |
| 웹 UI (클라우드) | http://46.62.155.122:8080 |
| 웹 UI (로컬) | http://localhost:8080 |
| MQTT 포트 | 1884 (Frigate Mosquitto 1883과 분리) |
| 데이터 경로 | ./data/db |
| 로그 경로 | ./data/logs (권한: 777) |

### 1-3. 등록 기기 — 클라우드 TB 기준 (운영)

| Profile | 기기명 | MQTT Token | 용도 |
|---------|--------|-----------|------|
| mobile-cctv | mobile-cctv-site-001 | Xl8KVvfv6Gj7DAxEXNz3 | TB-1 초기 검증용 |
| settop | virtual_settop1 | eMx3nS1nhXnI1CFFhLM7 | S1/S2 가상 기기 (Android) |
| ip-camera | virtual_cctv1 | 8SOsGhAdlVwXoXkaKzuh | S2/S3 가상 기기 |
| edge-controller | virtual_edge1 | A3TPceILZWFqZGogYQ3j | S3 가상 기기 |

### 1-4. 현재 폴더 구조

```
infra/thingsboard/
├── docker-compose.yml
├── README.md
├── config/               ← 추가 설정 (현재 미사용)
├── data/
│   ├── db/               ← PostgreSQL 데이터 (영속화)
│   └── logs/             ← Thingsboard 로그 (권한 777)
├── scripts/              ← cron 운영 스크립트 (현재 미사용)
├── temp_test/            ← 검증 테스트 코드
│   ├── test_01_startup_check.sh   ← 기동 검증 (PASS 4/4)
│   ├── test_02_device_model.sh    ← 기기 모델 검증 (PASS 7/7)
│   ├── test_03_mqtt_telemetry.py  ← MQTT 텔레메트리 (PASS 14/14)
│   ├── test_04_alarm_rule.py      ← 알람 규칙 (PASS 7/7)
│   └── test_05_virtual_devices.py ← 가상 기기 3종 (PASS 38/38)
└── doc/
    ├── architecture.md   ← 아키텍처 + Device Profile 스키마
    ├── project-overview.md
    ├── setup-guide.md
    └── walkthrough.md    ← 이 파일
```

### 1-4. 빠른 상태 확인 명령어

```bash
# 컨테이너 상태
docker ps --format "table {{.Names}}\t{{.Status}}"

# 로그 확인 (기동 중일 때)
docker compose logs -f thingsboard

# REST API 상태 확인
curl -s http://localhost:8080/api/noauth/activate | head -c 100

# 테넌트 토큰 발급 (API 사용 시)
curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"tenant@thingsboard.org","password":"tenant"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])"
```

---

## 섹션 2 — 운영 지식 (Knowledge Base)

> 새로운 교훈이 생길 때만 추가한다.

### 2-A. 초기 설치 시 반드시 확인할 것

| 순서 | 확인 항목 | 명령 / 방법 |
|---|---|---|
| 1 | 포트 충돌 (frigate MQTT 1883) | Thingsboard MQTT를 1884로 설정 |
| 2 | 최초 기동 1~2분 소요 | `docker compose logs -f` 로 `Started ThingsboardServerApplication` 메시지 확인 |
| 3 | data/logs 폴더 권한 | `chmod 777 data/logs` — 컨테이너 내부 UID 799(thingsboard)가 쓸 수 있어야 함 |
| 4 | 기본 비밀번호 변경 | sysadmin / tenant 계정 첫 접속 후 변경 |

### 2-B. Thingsboard 4.x API 변경 사항

| 기능 | 구 API (3.x) | 신 API (4.x) | 비고 |
|---|---|---|---|
| 알람 acknowledge | `POST /api/alarm/{id}/acknowledge` | `POST /api/alarm/{id}/ack` | 경로 단축 |
| 속성 조회 | `/api/plugins/telemetry/{id}/...` | `/api/plugins/telemetry/DEVICE/{id}/...` | 엔티티 타입 명시 필수 |

---

## 섹션 3 — 변경 이력 (Changelog)

> 최신 항목이 위에 온다. 완료된 항목은 수정하지 않는다.

---

### [2026-04-13] 클라우드 Thingsboard 기동 및 전체 검증 완료 (PASS 70/70)

**배경:** Hetzner CX33 서버(46.62.155.122)에 Thingsboard를 이전하여 운영 기준 환경 구축.
로컬 Thingsboard는 테스트 전용으로 유지.

**완료 항목:**
- Hetzner 서버 기본 설정: Docker, Git, Node.js, Claude Code CLI 설치
- GitHub clone → `/root/projects/siteguard-infra/`
- Thingsboard 4.2.1.1 클라우드 기동 확인
- test_01~05 전 항목 통과 — 로컬과 동일한 구조 클라우드에 재현
- test_03/04 MQTT 토큰·Device ID 클라우드 기준으로 수정

**클라우드 TB MQTT 토큰:**
| 기기명 | MQTT Token |
|--------|-----------|
| mobile-cctv-site-001 | Xl8KVvfv6Gj7DAxEXNz3 |
| virtual_settop1 | eMx3nS1nhXnI1CFFhLM7 |
| virtual_cctv1 | 8SOsGhAdlVwXoXkaKzuh |
| virtual_edge1 | A3TPceILZWFqZGogYQ3j |

**테스트 결과:**
| 파일 | PASS | FAIL |
|------|------|------|
| test_01_startup_check.sh | 4 | 0 |
| test_02_device_model.sh | 7 | 0 |
| test_03_mqtt_telemetry.py | 14 | 0 |
| test_04_alarm_rule.py | 7 | 0 |
| test_05_virtual_devices.py | 38 | 0 |

---

### [2026-04-13] 외부 AI 검토 반영 — 문서·설정 정확도 개선

**배경:** 두 번째 외부 AI(Claude) 검토 결과를 반영하여 문서 및 설정 파일 정확도 개선.

**변경 항목:**
- `docker-compose.yml`: CoAP 포트(5683-5688/udp) 주석 처리 (이동형 CCTV 시나리오에 불필요)
- `doc/architecture.md`:
  - Section 2 포트 표기 명확화: `(포트 9090)` → `(컨테이너 9090)`, 포트 매핑 주석 보완
  - Section 4 연동 방식: `MQTT 브릿지 1순위 또는 REST poll 2순위` → `MQTT 브릿지 (확정)` + 이유 명시
- `doc/project-overview.md`: MQTT 브릿지 검토 상태 `1순위 검토` → `**확정**`

---

### [2026-04-09] Device Profile 3종 + 가상 기기 3대 등록 완료 (PASS 38/38)

**배경:** 실배포 3종 시나리오 대응 Device Profile 설계 및 가상 기기 검증.
settop = Android OS 기반 확인 → Profile 서버 속성에 반영.

**완료 항목:**
- Device Profile 3종 생성: `settop` (Android, USB 카메라 1대 제한), `ip-camera`, `edge-controller`
- 가상 기기 3대: `virtual_settop1`, `virtual_cctv1`, `virtual_edge1`
- 기기별 서버/공유 속성 + MQTT 텔레메트리 + 알람 트리거 전 항목 검증
- `doc/architecture.md` 배포 시나리오·Device Profile 스키마 전면 업데이트

**MQTT 토큰 (가상 기기):**
| 기기명 | MQTT Token |
|--------|-----------|
| virtual_settop1 | ySaPv4sU2ZQPJuVYpwK9 |
| virtual_cctv1   | g19dPQxZArjsACP02kRS |
| virtual_edge1   | Tdsw3bDUmzRc1Yd3cl3x |

---

### [2026-04-09] TB-1 독립 검증 완료 — 기기 모델·MQTT·알람 전 항목 PASS

**배경:** Fleet Management 백엔드 독립 검증 완료. 4개 테스트 파일 전 항목 통과.

**완료 항목:**
- Thingsboard CE 4.2.1.1 (`thingsboard/tb-postgres:latest`) 기동 확인
- `data/logs` 권한 777 설정 (컨테이너 UID 799 쓰기 권한)
- 기기 `mobile-cctv-site-001` 생성, 서버/공유 속성 설정 완료
- MQTT 텔레메트리 6개 키 전송 및 REST API 조회 검증 완료
- 알람 규칙 2개 (CPU 과부하 >90, 디스크 초과 >180) 생성 및 트리거 확인
- `doc/architecture.md` 신규 생성
- API 차이 문서화: Thingsboard 4.x에서 알람 ack 경로 `/ack`로 변경

**테스트 결과:**
| 파일 | PASS | FAIL |
|------|------|------|
| test_01_startup_check.sh | 4 | 0 |
| test_02_device_model.sh | 7 | 0 |
| test_03_mqtt_telemetry.py | 14 | 0 |
| test_04_alarm_rule.py | 7 | 0 |

---

### [2026-04-09] 초기 설치 및 기본 구성

**배경:** Fleet Management 백엔드 독립 검증 시작. Frigate 통합 전 단독 기동·데이터 모델 검증.

**설치 항목:**
- Thingsboard CE (`thingsboard/tb-postgres:latest`)
- docker-compose.yml — 포트 8080(UI), 1884(MQTT, frigate 1883 충돌 방지)
- 폴더 구조: frigate와 동일 기준 적용
- 문서 체계: README.md, project-overview.md, setup-guide.md, walkthrough.md

---

## 섹션 4 — 트러블슈팅 모음

> 문제 유형별로 분류. 재발 가능성 기준으로 관리.

---

### [TS-01] 최초 기동 후 웹 UI 접속 안됨

- **현상:** `docker compose up -d` 후 `http://localhost:8080` 접속 안됨
- **원인:** DB 초기화 시간 필요 (1~2분)
- **해결:** `docker compose logs -f thingsboard` 에서 `Started ThingsboardServerApplication` 확인 후 접속

---

### [TS-02] MQTT 포트 충돌

- **현상:** Thingsboard MQTT 1883 기동 실패
- **원인:** frigate의 Mosquitto가 이미 1883 점유
- **해결:** `docker-compose.yml` 에서 `"1884:1883"` 으로 매핑 (이미 적용됨)

---

### [TS-03] 컨테이너 기동 직후 GC 로그 Permission Denied로 JVM 실패

- **현상:** `docker compose up` 후 컨테이너가 즉시 종료, 로그에 `gc.log: Permission denied` + `Error: Could not create the Java Virtual Machine`
- **원인:** `data/logs` 폴더 소유자가 호스트 사용자(visionlinux, UID 1000)이고, 컨테이너 내부 Thingsboard 프로세스(UID 799)가 쓸 수 없음
- **해결:** `chmod 777 data/logs` 후 컨테이너 재시작
- **주의:** `sudo chown -R 799:799 data/logs` 도 가능하지만 sudo 필요

---

### [TS-04] Thingsboard 4.x 알람 acknowledge API 경로 변경

- **현상:** `POST /api/alarm/{id}/acknowledge` → HTTP 405 (Allow: GET)
- **원인:** Thingsboard 4.x에서 API 경로 변경
- **해결:** `POST /api/alarm/{id}/ack` 사용 (경로 단축)
- **추가:** 이미 ack된 알람 재ack 시 HTTP 400 `"Alarm was already acknowledged!"` 반환 — 정상 동작임

---

### [TS-05] 속성 조회 API에 엔티티 타입 명시 필요

- **현상:** `GET /api/plugins/telemetry/{deviceId}/values/attributes/SERVER_SCOPE` → 빈 배열 반환
- **원인:** Thingsboard 4.x에서 엔티티 타입을 경로에 명시해야 함
- **해결:** `GET /api/plugins/telemetry/DEVICE/{deviceId}/values/attributes/SERVER_SCOPE` 로 변경
