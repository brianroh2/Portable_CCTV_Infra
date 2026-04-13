# 프로젝트 현황 요약 (2026-04-13 기준)

> 성격: 0409 이후 0413까지 완료 작업 + 앞으로 할 일 정리
> 다음 요약 파일: `temp_project_summary_MMDD.md` 형식으로 주요 마일스톤마다 생성

---

## 1. 전체 진행 현황

| Phase | 내용 | 상태 | 완료일 |
|-------|------|------|--------|
| Frigate Step 1 | VMS 기본 구축 (카메라 3대, OpenVINO, 스토리지) | ✅ 완료 | 2026-04-08 |
| TB-1 | Thingsboard 독립 검증 (기기 모델, MQTT, 알람) | ✅ 완료 | 2026-04-09 |
| Phase A | GitHub 연동 | ✅ 완료 | 2026-04-09 |
| Phase A | Tailscale 설치 | 🔲 미완 | — |
| Phase B | Hetzner 서버 구축 + TB 클라우드 이전 | ✅ 완료 | 2026-04-13 |
| TB-2 | Frigate → 클라우드 TB 텔레메트리 브리지 | ✅ 완료 | 2026-04-13 |
| Phase C | go2rtc, 에지 기기 연동 | 🔲 예정 | — |

---

## 2. 0409 이후 0413까지 완료 항목

### [TB-1 완료 후 문서·설정 정비]

- 외부 AI 2차 검토 결과 즉시 반영
  - `CLAUDE.md`: 현황 표 형식으로 압축 (32줄→27줄), TB-1 완료 반영
  - `frigate/docker-compose.yml`: 이미지 버전 고정 (`stable` → `0.17.1`)
  - `thingsboard/docker-compose.yml`: 이미지 버전 고정 (`latest` → `4.2.1.1`), CoAP 포트 주석 처리
  - `doc/platform-strategy.md`: GitHub 미결사항 완료 처리
  - `thingsboard/doc/architecture.md`: Step 상태 수정, 포트 표기 명확화, MQTT 브릿지 확정
  - `thingsboard/doc/project-overview.md`: MQTT 브릿지 `1순위 검토` → `**확정**`

### [Phase B — Hetzner 클라우드 서버 구축]

- Hetzner CX33 서버 생성 (Ubuntu 24.04, Helsinki, 46.62.155.122)
- SSH 키 생성 및 등록 (hetzner-fieldwatch-visionlinux, ed25519)
- SSH config 등록 → `ssh hetzner` 한 줄 접속
- 서버 기본 설치: Git 2.43, Docker 29.4, Docker Compose v5.1.2, Node.js v22.14, Claude Code CLI 2.1.104
- Python 환경: python3.12-venv + paho-mqtt (`thingsboard/.venv/`)
- GitHub clone → `/root/projects/siteguard-infra/`
- Thingsboard 4.2.1.1 클라우드 기동 완료
- test_01~05 클라우드에서 전 항목 통과 (PASS 70/70)
  - test_03/04 MQTT 토큰·Device ID 클라우드 기준으로 수정

### [infra 레벨 문서 신설]

- `infra/doc/walkthrough.md` 신규 생성
  - 패키지 경계를 넘는 전체 변경 이력 관리
  - 섹션1(현황 스냅샷) + 섹션2(변경 이력) 구조

### [TB-2 — Frigate → 클라우드 Thingsboard 브리지]

- `frigate/scripts/frigate_tb_bridge.py` 신규 작성
  - Frigate REST API(`/api/stats`) 60초 주기 폴링
  - Frigate MQTT(`frigate/events`) person 감지 카운트 실시간 구독
  - 클라우드 TB MQTT(46.62.155.122:1884) → virtual_edge1 텔레메트리 전송
- `frigate/temp_test/test_tb2_bridge.py` 신규 작성, PASS 11/11 확인
- 브리지 백그라운드 실행 중 (`python3 -u scripts/frigate_tb_bridge.py >> scripts/bridge.log 2>&1 &`)

**전송 텔레메트리 7개 키:**
`online`, `frigate_status`, `inference_ms`, `cameras_online`, `cpu_usage`, `detect_events_today`, `local_storage_gb`

**주요 발견:** Frigate는 `frigate/stats` MQTT 토픽 미발행. REST API만 통계 수집 경로.

### [세션 분리 원칙 수립]

- 로컬 PC 세션(visionlinux): Frigate, TB-2 브리지, 에지 스크립트
- Hetzner 세션(root@46.62.155.122): Thingsboard, go2rtc, 클라우드 서비스
- `CLAUDE.md`에 세션 분리 원칙 추가

---

## 3. 현재 시스템 상태

### 서비스 실행 현황

| 서비스 | 위치 | 상태 |
|--------|------|------|
| Frigate 0.17.1 + 카메라 3대 | 로컬 PC (192.168.0.15) | ✅ 운영 중 |
| Mosquitto | 로컬 PC | ✅ 운영 중 |
| TB-2 브리지 | 로컬 PC (백그라운드) | ✅ 운영 중 |
| Thingsboard 4.2.1.1 | Hetzner (46.62.155.122) | ✅ 운영 중 |

### 클라우드 TB 등록 기기

| 기기명 | Profile | MQTT Token |
|--------|---------|-----------|
| mobile-cctv-site-001 | mobile-cctv | Xl8KVvfv6Gj7DAxEXNz3 |
| virtual_settop1 | settop | eMx3nS1nhXnI1CFFhLM7 |
| virtual_cctv1 | ip-camera | 8SOsGhAdlVwXoXkaKzuh |
| virtual_edge1 | edge-controller | A3TPceILZWFqZGogYQ3j |

---

## 4. 앞으로 할 일

### 로컬 PC 세션에서 할 것 (에지/Frigate)

| 항목 | 우선순위 | 비고 |
|------|---------|------|
| RTSP 자격증명 `.env` 분리 | 중 | config.yml 하드코딩 상태 |
| TB-2 브리지 cron/systemd 등록 | 중 | PC 재부팅 시 자동 시작 |
| Tailscale 로컬 PC 설치 | 중 | go2rtc 연동 전 필요 |

### Hetzner 세션에서 할 것 (클라우드)

| 항목 | 우선순위 | 비고 |
|------|---------|------|
| Tailscale Hetzner 설치 | 중 | 로컬 PC와 쌍으로 |
| go2rtc 설치 + RTSP 중계 설정 | Phase C | 클라우드에서 카메라 스트림 접근 |
| Thingsboard 대시보드 구성 | Phase C | virtual_edge1 텔레메트리 시각화 |
| Hetzner 방화벽 설정 | Phase C | 필요 포트만 개방 |

### 별도 레포 (apps/)

| 항목 | 우선순위 | 비고 |
|------|---------|------|
| mobile-cctv-vms UI | Phase C 이후 | 에지용 관제 앱, 로컬 개발 |

---

## 5. 다음 세션 시작 가이드

```
이 문서 읽기 → 어느 세션(로컬/Hetzner)에서 작업할지 결정
→ 세션 분리 원칙 확인 (CLAUDE.md)
→ 작업 시작
```

**로컬 PC 세션 시작 시:**
```bash
cd /home/visionlinux/workspace/infra
# 브리지 실행 여부 확인
ps aux | grep frigate_tb_bridge | grep -v grep
```

**Hetzner 세션 시작 시:**
```bash
ssh hetzner
cd /root/projects/siteguard-infra
docker ps --format "table {{.Names}}\t{{.Status}}"
```
