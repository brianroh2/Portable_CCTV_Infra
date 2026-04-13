# 인프라 전체 운영 문서 (Infra Walkthrough)

> 문서 성격: 패키지 경계를 넘는 인프라 전체 변경 이력 + 진척 관리
> 섹션 1 (현황 스냅샷)은 작업할 때마다 **덮어쓴다.**
> 섹션 2 (변경 이력)은 **위에 추가만** 한다. 수정하지 않는다.

---

## 섹션 1 — 현재 인프라 현황 스냅샷

> 마지막 업데이트: 2026-04-13

### 1-1. 환경별 역할

| 환경 | 위치 | 역할 | 상태 |
|------|------|------|------|
| **클라우드** | Hetzner CX33, 46.62.155.122 (Helsinki) | Thingsboard 운영, 코드 관리 | ✅ 운영 중 |
| **로컬 PC** | 192.168.0.15 | Frigate + 카메라 3대, 테스트용 TB | ✅ 운영 중 |
| **에지 기기** | settop, edge-controller | 미준비 | 🔲 예정 |

### 1-2. 서비스 현황

| 서비스 | 위치 | 포트 | 상태 |
|--------|------|------|------|
| Frigate 0.17.1 | 로컬 PC | 5000, 8554, 8555 | ✅ 운영 중 |
| Mosquitto (Frigate용) | 로컬 PC | 1883 | ✅ 운영 중 |
| Thingsboard 4.2.1.1 | **클라우드** | 8080, 1884, 7070 | ✅ 운영 중 |
| Thingsboard 4.2.1.1 | 로컬 PC | 8080, 1884, 7070 | 🔲 필요 시 기동 |
| go2rtc | 클라우드 | 1984 | 🔲 Phase C 예정 |

### 1-3. 클라우드 서버 구성

| 항목 | 내용 |
|------|------|
| 서버 | Hetzner CX33 (ubuntu-8gb-hel1-1) |
| OS | Ubuntu 24.04 LTS |
| IP | 46.62.155.122 |
| 접속 | `ssh hetzner` (~/.ssh/config 등록) |
| 코드 위치 | `/root/projects/siteguard-infra/` |
| Python venv | `/root/projects/siteguard-infra/thingsboard/.venv/` |

### 1-4. Phase 진행 현황

| Phase | 내용 | 상태 |
|-------|------|------|
| **Phase A** | GitHub 연동, Tailscale 준비 | ✅ GitHub 완료, Tailscale 미설치 |
| **Phase B** | Hetzner 서버 구축 + Thingsboard 이전 | ✅ 완료 (2026-04-13) |
| **TB-2** | Frigate → Thingsboard MQTT 연동 | 🔲 다음 단계 |
| **Phase C** | go2rtc, 에지 기기 연동 | 🔲 예정 |

### 1-5. 빠른 접속 명령어

```bash
# 클라우드 서버 SSH 접속
ssh hetzner

# 클라우드 Thingsboard 상태 확인
ssh hetzner 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# 클라우드 Thingsboard 로그
ssh hetzner 'docker logs thingsboard --tail 50'

# 로컬 Frigate 상태
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 섹션 2 — 변경 이력 (Changelog)

> 최신 항목이 위에 온다. 완료된 항목은 수정하지 않는다.

---

### [2026-04-13] Phase B 완료 — 클라우드 서버 구축 + Thingsboard 이전

**배경:** 개발 PC가 자주 바뀌는 환경 + 여러 서비스 클라우드 운영을 감안하여
Hetzner CX33 서버를 구축하고 Thingsboard를 클라우드 운영 기준으로 이전.

**완료 항목:**

- Hetzner CX33 서버 생성 (Ubuntu 24.04, Helsinki, 46.62.155.122)
- SSH 키 생성 및 등록 (hetzner-fieldwatch-visionlinux)
- SSH config 등록 → `ssh hetzner` 한 줄 접속
- 서버 기본 설치: Git 2.43, Docker 29.4, Docker Compose v5.1.2, Node.js v22.14, Claude Code CLI 2.1.104
- Python 환경: python3.12-venv + paho-mqtt (thingsboard/.venv/)
- GitHub clone → `/root/projects/siteguard-infra/`
- Thingsboard 4.2.1.1 클라우드 기동 완료
- test_01~05 전 항목 클라우드에서 통과 (PASS 70/70)
- 클라우드 TB MQTT 토큰 문서화

**클라우드 Thingsboard 등록 기기:**

| 기기명 | Profile | MQTT Token |
|--------|---------|-----------|
| mobile-cctv-site-001 | mobile-cctv | Xl8KVvfv6Gj7DAxEXNz3 |
| virtual_settop1 | settop | eMx3nS1nhXnI1CFFhLM7 |
| virtual_cctv1 | ip-camera | 8SOsGhAdlVwXoXkaKzuh |
| virtual_edge1 | edge-controller | A3TPceILZWFqZGogYQ3j |

---

### [2026-04-13] 정기 검토 — 즉시 조치 항목 반영

**배경:** 제3자 관점 전체 검토 후 즉시 조치 5개 항목 처리.

**변경 항목:**
- `CLAUDE.md`: TB-1 완료 상태 반영, 표 형식으로 압축 (32줄→27줄)
- `frigate/docker-compose.yml`: 이미지 버전 고정 (`stable` → `0.17.1`)
- `thingsboard/docker-compose.yml`: 이미지 버전 고정 (`latest` → `4.2.1.1`)
- `doc/platform-strategy.md`: 미결사항 #1 GitHub 완료 처리
- `thingsboard/doc/architecture.md`: 상태 표시 수정 (Step 2 진행 중 → TB-1 완료)
- `thingsboard/doc/project-overview.md`: 텔레메트리 항목 "초안" → "TB-1 검증 완료"

**잔여 조치 항목 (나중에):**
- RTSP 자격증명 `.env` 분리 → Hetzner 구축 시점에 처리
- go2rtc 검증 → Phase C
- 컨테이너 네트워크 명시 → 통합 단계

---

### [2026-04-13] 외부 AI 2차 검토 반영 — 문서·설정 정확도 개선

**배경:** 두 번째 외부 AI 검토 결과를 반영하여 문서 및 설정 파일 정확도 개선.

**변경 항목:**
- `thingsboard/docker-compose.yml`: CoAP 포트 주석 처리
- `thingsboard/doc/architecture.md`: 포트 표기 명확화, MQTT 브릿지 확정
- `thingsboard/doc/project-overview.md`: MQTT 브릿지 `1순위 검토` → `확정`
- `frigate/doc/architecture.md`: Layer 1~3 미래 설계안 표기, Step 상태 현행화
- `frigate/doc/project-overview.md`: 네트워크 구성 2·3번 Hetzner 참조 추가
- `CLAUDE.md`: temp_test 변경 시 walkthrough PASS 횟수 동기화 규칙 추가

---

### [2026-04-09] Thingsboard TB-1 독립 검증 완료 (PASS 70/70)

**배경:** Fleet Management 백엔드(Thingsboard CE) 독립 검증 완료.
Frigate 통합 전 단독 기동·기기 모델·MQTT·알람·Device Profile 전 항목 검증.

**완료 항목:**
- Thingsboard CE 4.2.1.1 로컬 기동
- Device Profile 3종: settop(Android, USB 1대), ip-camera, edge-controller
- 가상기기 3대: virtual_settop1, virtual_cctv1, virtual_edge1
- MQTT 텔레메트리 6개 키, 알람 규칙 2종 검증
- 주요 API 차이 발견: TB 4.x `/ack` 엔드포인트, `DEVICE/` 엔티티 타입 필수
- `infra/doc/` 폴더 신설, `platform-strategy.md` 작성
- GitHub 저장소 연동 (brianroh2/Portable_CCTV_Infra)

**상세 내용:** `thingsboard/doc/walkthrough.md` 참조

---

### [2026-04-08] Frigate VMS Step 1 완료

**배경:** VMS 인프라 레이어 안정화 완료.

**완료 항목:**
- Frigate 0.17.1 + Mosquitto, Intel OpenVINO GPU 가속 (renderD129)
- 카메라 3대 이벤트 녹화 (pre 3초 + post 5초, 7일 보관)
- cctv_2 과감지 필터 (min_score 0.8, min_area 3600)
- 감지 시간 KST 08:00~19:00 (cron + MQTT 제어)
- 스토리지 200GB 상한 자동 정리 (6시간마다)
- WAL 체크포인트 매일 04:00

**상세 내용:** `frigate/doc/walkthrough.md` 참조
