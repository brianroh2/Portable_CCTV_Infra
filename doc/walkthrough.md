# 인프라 전체 운영 문서 (Infra Walkthrough)

> 문서 성격: 패키지 경계를 넘는 인프라 전체 변경 이력 + 진척 관리
> 섹션 1 (현황 스냅샷)은 작업할 때마다 **덮어쓴다.**
> 섹션 2 (변경 이력)은 **위에 추가만** 한다. 수정하지 않는다.

---

## 섹션 1 — 현재 인프라 현황 스냅샷

> 마지막 업데이트: 2026-05-11 (Nginx 프록시 적용, 내부·외부 영상 정상 확인)

### 1-1. 환경별 역할

| 환경 | 위치 | 역할 | 상태 |
|------|------|------|------|
| **클라우드** | Hetzner CX33, 46.62.155.122 (Helsinki) | Thingsboard, go2rtc 운영, 코드 관리 | ✅ 운영 중 |
| **LTE 현장** | 192.168.1.x (M2MNet LT7) | CCTV-1(TVT), CCTV-3(VHT) | ✅ 운영 중 |
| **로컬 개발PC** | 192.168.1.111 (Linux) / 192.168.1.179 (Windows) | 개발·테스트 | ✅ 임시 연결 |
| **에지 기기** | RPi 등 | Phase D 예정 | 🔲 예정 |

### 1-2. 서비스 현황

| 서비스 | 위치 | 포트 | 상태 |
|--------|------|------|------|
| Frigate 0.17.1 | 로컬 PC | 5000, 8554, 8555 | ✅ 운영 중 |
| Mosquitto (Frigate용) | 로컬 PC | 1883 | ✅ 운영 중 |
| TB-2 브리지 | 로컬 PC (백그라운드) | — | ✅ 운영 중 |
| Thingsboard 4.2.1.1 | **클라우드** | 8080, 1884, 7070 | ✅ 운영 중 |
| go2rtc 1.9.9 | **클라우드** | 1984(UI/API), 8555(RTSP) | ✅ 운영 중 |
| **Nginx** | **클라우드** | **80 (go2rtc 프록시)** | ✅ 운영 중 |
| Thingsboard 4.2.1.1 | 로컬 PC | 8080, 1884, 7070 | 🔲 필요 시 기동 |

### 1-3. 클라우드 서버 구성

| 항목 | 내용 |
|------|------|
| 서버 | Hetzner CX33 (ubuntu-8gb-hel1-1) |
| OS | Ubuntu 24.04 LTS |
| IP | 46.62.155.122 (공인) / 100.105.211.82 (Tailscale) |
| 접속 | `ssh hetzner` (~/.ssh/config 등록) |
| 코드 위치 | `/root/projects/siteguard-infra/` |
| Python venv | `/root/projects/siteguard-infra/thingsboard/.venv/` |

### 1-4. Tailscale 네트워크

| 기기 | Tailscale IP | 상태 |
|------|-------------|------|
| ubuntu-8gb-hel1-1 (Hetzner) | 100.105.211.82 | ✅ 연결됨 |
| visionlinux-alien (로컬 PC) | 100.118.143.92 | ✅ 연결됨 |

- 로컬 PC가 `192.168.0.0/24` 서브넷 라우팅 광고 → Hetzner에서 `192.168.0.x` 카메라 직접 접근 가능
- Hetzner에서 로컬 PC SSH: `ssh visionlinux` (`~/.ssh/config` 등록)
- Tailscale SSH 사용 (키 관리 불필요, 계정 인증으로 통합)

### 1-5. Phase 진행 현황

| Phase | 내용 | 상태 |
|-------|------|------|
| **Phase A** | GitHub 연동, Tailscale 설치 | ✅ 완료 (GitHub 04-09, Tailscale 04-14) |
| **Phase B** | Hetzner 서버 구축 + Thingsboard 이전 | ✅ 완료 (2026-04-13) |
| **TB-2** | Frigate → Thingsboard MQTT 연동 | ✅ 완료 (2026-04-13) |
| **Phase C** | go2rtc 카메라 스트리밍 | ✅ 완료 (2026-04-14) |
| **LTE 현장 연동** | NAT Free, M2MNet DDNS, 포트포워딩, LTE 카메라 → go2rtc | ✅ 완료 (2026-05-11) |
| **Phase C 잔여** | Thingsboard 대시보드, 기기 상태 연동, 서브스트림 | ✅ 완료 (2026-05-11) |
| **Nginx 프록시** | ISP DPI 우회 — 외부망 MSE 스트리밍 정상화 | ✅ 완료 (2026-05-11) |
| **Phase D** | RPi 에지 기기 연동 | 🔲 예정 |

### 1-6. SiteGuard 관제 화면 접속

| 화면 | URL |
|------|-----|
| TB 통합 관리 UI | http://46.62.155.122:8080 (tenant@thingsboard.org / tenant) |
| 메인 관제 그리드 | http://46.62.155.122:8080/dashboard/bd0e61b0-4d1e-11f1-bb6f-7d7ca6d1fbf3 |
| CCTV-1 개별 | http://46.62.155.122:8080/dashboard/bd14a340-4d1e-11f1-bb6f-7d7ca6d1fbf3 |
| CCTV-3 개별 | http://46.62.155.122:8080/dashboard/bd1ce0a0-4d1e-11f1-bb6f-7d7ca6d1fbf3 |
| go2rtc Web UI (직접) | http://46.62.155.122:1984 |
| go2rtc (Nginx 경유) | http://46.62.155.122/go2rtc/ |

> **영상 스트리밍 방식:** MSE (Nginx 포트 80 → go2rtc 1984 프록시)  
> 영상 좌측 상단 "MSE" 레이블은 정상 — 현재 스트리밍 방식 표시

### 1-7. 빠른 접속 명령어

```bash
# 클라우드 서버 SSH 접속
ssh hetzner

# 클라우드 전체 서비스 상태
docker ps --format "table {{.Names}}\t{{.Status}}"

# go2rtc 스트림 상태
curl -s http://localhost/go2rtc/api/streams | python3 -m json.tool

# 로컬 PC SSH (Hetzner에서)
ssh visionlinux

# 로컬 PC Frigate 상태 (Hetzner에서 원격 확인)
ssh visionlinux "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

---

## 섹션 2 — 변경 이력 (Changelog)

> 최신 항목이 위에 온다. 완료된 항목은 수정하지 않는다.

---

### [2026-05-11] Nginx 역방향 프록시 — 외부망 영상 정상화 완료

**배경:** 외부 PC(LTE망, 기업망 등)에서 go2rtc MSE 스트리밍이 "loading" 상태로 멈추는 현상 발생.  
원인: ISP/기업망 DPI(딥패킷검사)가 비표준 포트(1984) WebSocket을 차단.

**해결 방법:**  
Nginx를 포트 80 역방향 프록시로 설치 → `/go2rtc/*` 요청을 `127.0.0.1:1984`로 포워딩.  
WebSocket Upgrade 헤더를 그대로 통과시켜 MSE 스트리밍 정상화.

**완료 항목:**
- Nginx 설치 + `/etc/nginx/conf.d/go2rtc.conf` 작성 (WebSocket 프록시 포함)
- go2rtc STUN: Google → Cloudflare(`stun.cloudflare.com:3478`)
- camera-grid.html: 접속 URL `http://46.62.155.122/go2rtc`, mode=mse
- TB jar 재패치(clean replace) + 대시보드 3개 재생성
- **내부·외부 PC 모두 MSE 영상 정상 재생 확인**

**MSE 레이블:** go2rtc 플레이어 좌측 상단 "MSE" 표시는 현재 스트리밍 방식 안내 — 정상 동작

---

### [2026-05-11] Phase C 완료 — SiteGuard 대시보드 + go2rtc 서브스트림

**배경:** LTE 현장 카메라를 Thingsboard 관제 UI에 완전 통합. Phase C 잔여 작업 전체 완료.

**완료 항목:**

1. **실제 CCTV 기기 등록 (ip-camera 프로파일)**
   - cctv-1 (TVT TD-9421S4C), cctv-3 (Vision Hitech TBT-Dome F977)
   - 서버 속성 16개: 메인/서브 스트림 정보 분리 저장

2. **SiteGuard 로고 + camera-grid.html TB 임베드**
   - Thingsboard ui-ngx jar 패치로 로고 교체 및 정적 HTML 배포
   - go2rtc MSE 모드 멀티카메라 그리드 UI (2×2~4×5 레이아웃)

3. **대시보드 3개 구축**
   - 메인 관제 그리드: camera-grid.html iframe
   - CCTV-1/3 개별: 영상 + 메인/서브 스트림 스펙 나란히 표시
   - ip-camera 프로파일 기본 대시보드 연결

4. **CCTV 상태 모니터**
   - TCP 포트 체크 → TB MQTT 60초 주기 (`cctv_status_monitor.py`)

5. **go2rtc 서브스트림 전환**
   - cctv_1: profile2 (640×480/10fps), cctv_3: Ch2 (640×480/10fps)
   - 대역폭 20~30배 절감, lazy loading 유지

**접속 링크:**
- 메인: http://46.62.155.122:8080/dashboard/d665a8e0-4d13-11f1-839b-7d7ca6d1fbf3
- CCTV-1: http://46.62.155.122:8080/dashboard/d66a63d0-4d13-11f1-839b-7d7ca6d1fbf3
- CCTV-3: http://46.62.155.122:8080/dashboard/d67168b0-4d13-11f1-839b-7d7ca6d1fbf3

---

### [2026-05-11] LTE 현장 네트워크 구성 확정 및 go2rtc 연동 완료

**배경:** SKT LTE 인바운드 차단 문제를 NAT Free 설정으로 해소하고, 현장 네트워크 구성을 확정.

**완료 항목:**

1. **NAT Free 설정**
   - SKT 통신사에 NAT Free 요청 적용
   - 이전: 통신사 인바운드 차단으로 포트포워딩 불가
   - 이후: DDNS + 포트포워딩으로 외부 직접 접근 가능

2. **M2MNet DDNS 전환**
   - No-IP(siteguard01.ddns.net) → M2MNet 자체 DDNS(0004312.m2mnet.kr)
   - LT7 라우터 자체 갱신, 30일 이메일 확인 불필요

3. **현장 네트워크 구성 확정**
   - LT7 LAN 포트 2개 제약: AP 모드 공유기(ipTIME A2004MU) + POE 스위치로 확장
   - 모든 기기 192.168.1.x 단일 대역 (이중 NAT 제거)
   - CCTV-1 (TVT Dome, 192.168.1.51), CCTV-3 (VHT Dome F977, 192.168.1.53)

4. **포트포워딩 설정**
   - RTSP_TCP1: WAN:554 → 192.168.1.51:554 (CCTV-1)
   - RTSP_TCP3: WAN:555 → 192.168.1.53:554 (CCTV-3)

5. **go2rtc.yaml 업데이트**
   - 기존 cctv_1/2/3 (로컬 192.168.0.x) 제거
   - 신규 cctv_1, cctv_3 (0004312.m2mnet.kr 경유) 설정

6. **문서 업데이트**
   - `doc/system-architecture-roadmap.md`: 실제 네트워크 구성 반영
   - `doc/lte-router-considerations.md`: NAT Free 해결, M2MNet DDNS, 실제 포트포워딩 규칙 반영
   - `go2rtc/go2rtc.yaml`: 신규 스트림 적용

**영상 테스트 결과:**
| 항목 | 결과 |
|------|------|
| CCTV-1 VLC 로컬 재생 | ✅ |
| CCTV-3 VLC 로컬 재생 | ✅ |
| 외부 DDNS 접근 | ✅ |

**잔여 항목:**
- CCTV-1 비밀번호 변경 (보안 ⚠️)
- Phase C: Thingsboard 대시보드 구성

---

### [2026-04-14] Phase C — Tailscale + go2rtc 카메라 스트리밍 구축

**배경:** 클라우드에서 에지 PC 카메라를 라이브 스트리밍으로 접근하기 위한 네트워크·영상 중계 레이어 구축.

**완료 항목:**

1. **Tailscale 설치 (Hetzner)**
   - `curl -fsSL https://tailscale.com/install.sh | sh` 설치
   - `tailscale up --ssh --accept-routes` 로 인증 및 서브넷 라우트 수락
   - `frontiera333@gmail.com` 계정 테일넷에 합류
   - Hetzner Tailscale IP: `100.105.211.82`

2. **Tailscale SSH 활성화 (로컬 PC)**
   - `sudo tailscale up --ssh --advertise-routes=192.168.0.0/24` (로컬 PC에서 실행)
   - Tailscale 관리 콘솔에서 서브넷 라우트 승인
   - Hetzner → 로컬 PC SSH 연결 확인: `ssh visionlinux`
   - Hetzner → 카메라(192.168.0.x) 직접 접근 확인

3. **go2rtc 1.9.9 설치 및 카메라 연결**
   - `go2rtc/docker-compose.yml` + `go2rtc/go2rtc.yaml` 신규 작성
   - 카메라 3대 sub stream 연결 (640x480)
   - 접속: `http://46.62.155.122:1984`

**핵심 발견 — 로컬 vs 클라우드 카메라 연결 차이:**

| 항목 | 로컬 (Frigate) | 클라우드 (go2rtc) |
|------|--------------|----------------|
| 스트림 | main stream (고화질, 감지·녹화용) | sub stream (640x480, 라이브 뷰용) |
| 연결 방식 | 직접 LAN | Tailscale 서브넷 경유 |
| RTSP 전송 | UDP/TCP 모두 가능 | **TCP 강제 필수** (UDP RTP 역방향 불통) |
| 비트스트림 | 카메라 원본 그대로 | **MPEG-TS 래핑 필수** (제조사 포맷 차이 흡수) |

**시행착오 요약:**

| 시도 | 결과 | 원인 |
|------|------|------|
| `rtsp://...` plain RTSP | cctv_1만 성공, cctv_2/3 17초 후 종료 | Vision Hitech 카메라 UDP RTP가 Tailscale 경유 역방향 차단 |
| `?transport=tcp` URL 파라미터 | "wrong response on DESCRIBE" | 파라미터가 카메라에 그대로 전달되어 경로 오류 |
| `exec:ffmpeg -rtsp_transport tcp -f h264` | "unsupported header: 0000000100000000" | Vision Hitech 출력 포맷이 Annex B 아님 |
| `exec:ffmpeg -rtsp_transport tcp -f mpegts` | **성공** | MPEG-TS 컨테이너가 포맷 차이 흡수 |

**신규 카메라 추가 시 표준 템플릿:**
```yaml
# 제조사 무관 안전한 기본 패턴
new_cam: exec:ffmpeg -hide_banner -rtsp_transport tcp \
  -i rtsp://user:pass@192.168.0.x:554/substream \
  -c:v copy -f mpegts -
```

---

### [2026-04-13] TB-2 완료 — Frigate → 클라우드 Thingsboard 텔레메트리 브리지

**배경:** Frigate VMS 상태를 클라우드 Thingsboard(virtual_edge1)에 실시간 전달하는 MQTT 브리지 구축.
로컬 PC Frigate → 클라우드 TB(46.62.155.122:1884) 직접 연결.

**완료 항목:**
- `frigate/scripts/frigate_tb_bridge.py` 신규 작성 (REST API 폴링 + MQTT 이벤트 구독)
- `frigate/temp_test/test_tb2_bridge.py` 검증 통과 (PASS 11/11)
- 브리지 백그라운드 기동, 60초 주기 텔레메트리 전송 확인

**핵심 수집 방식:**
- Frigate REST API `/api/stats` → inference_ms, cameras_online, cpu_usage (60초 주기)
- Frigate MQTT `frigate/events` → person 감지 카운트 (실시간)
- 클라우드 TB MQTT `v1/devices/me/telemetry` → 7개 키 전송

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
