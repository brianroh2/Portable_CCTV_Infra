# 프로젝트 현황 요약 (2026-04-09)

> 목적: 새 대화 세션 시작 시 Claude가 현재 상태를 빠르게 파악하기 위한 온보딩 문서.
> 이 파일 하나를 먼저 읽고, 하단 "문서 읽기 순서"에 따라 세부 문서를 순서대로 열면 된다.

---

## 1. 프로젝트 한 줄 정의

**이동형 CCTV 현장 관제 솔루션 상용화** — 카메라 영상 관리(VMS) + 현장 기기 상태 관리(Fleet)를
하나의 자체 브랜드 UI로 제공하는 제품. 현재는 인프라 레이어 패키지 검증 단계.

---

## 2. 현재 개발 환경

### 개발 PC (고정 위치)
| 항목 | 내용 |
|------|------|
| OS | Ubuntu 22.04 LTS |
| CPU | Intel Core i7-7820HK |
| RAM | 16GB |
| GPU | Intel HD 630 (renderD129) — Frigate AI 감지용 OpenVINO |
| 내부 IP | 192.168.0.15 |

### 네트워크 현황
```
무선 인터넷
  └─ LTE 라우터
       └─ 공유기 A
            └─ 공유기 B (3중 NAT)
                 ├─ 개발 PC     192.168.0.15
                 ├─ cctv_1     192.168.0.6
                 ├─ cctv_2     192.168.0.7
                 └─ cctv_3     192.168.0.8
```
외부 접속: **Tailscale 메시 VPN** (3중 NAT 환경에서 포트포워딩 없이 원격 접속)

### 카메라 3대
| 이름 | IP | 비고 |
|------|----|------|
| cctv_1 | 192.168.0.6 | TBT-Dome 765E |
| cctv_2 | 192.168.0.7 | Vision-Hightech F977, 과감지 필터 적용 |
| cctv_3 | 192.168.0.8 | Vision-Hightech F99D |

---

## 3. 워크스페이스 구조

```
/home/visionlinux/workspace/infra/     ← GitHub: brianroh2/Portable_CCTV_Infra
├── CLAUDE.md                          ← Claude 자동 로드 지시사항
├── infra.code-workspace               ← VS Code 멀티루트 워크스페이스
├── .gitignore                         ← 민감파일·대용량 파일 제외
├── doc/                               ← 인프라 전체 전략 문서 (VS Code: infra docs)
│   ├── platform-strategy.md           ← 플랫폼 전략 확정안 ★ 필독
│   └── temp_project_summary_0409.md   ← 이 파일
├── frigate/                           ← VMS 인프라 (VS Code: frigate VMS)
│   ├── docker-compose.yml
│   ├── config/config.yml
│   ├── mosquitto/
│   ├── scripts/                       ← cron 운영 스크립트 3개
│   ├── temp_test/                     ← 검증 테스트 5개
│   └── doc/
│       ├── project-overview.md        ← 하드웨어·네트워크·스택 전반
│       ├── architecture.md            ← VMS+Fleet 통합 아키텍처 설계
│       ├── setup-guide.md             ← 처음부터 설치하는 절차
│       └── walkthrough.md             ← 운영 변경 이력 + 트러블슈팅
└── thingsboard/                       ← Fleet Management (VS Code: thingsboard Fleet)
    ├── docker-compose.yml
    ├── temp_test/                     ← 검증 테스트 5개
    └── doc/
        ├── project-overview.md        ← 데이터 모델·연동 계획·로드맵
        ├── architecture.md            ← Device Profile·시나리오·MQTT 구조
        ├── setup-guide.md             ← 설치 절차
        └── walkthrough.md             ← 운영 변경 이력 + 트러블슈팅 + API 차이
```

---

## 4. 패키지 검증 완료 현황

### Step 1 — Frigate VMS ✅ 완료 (2026-04-08)
| 항목 | 내용 |
|------|------|
| 버전 | Frigate 0.17.1 + Mosquitto 2.x |
| GPU 가속 | Intel HD 630 OpenVINO (추론 9ms, CPU 21%) |
| 카메라 | 3대 이벤트 녹화 (pre 3초 + post 5초, 7일 보관) |
| 과감지 필터 | cctv_2: min_score 0.8, min_area 3600 |
| 감지 시간 | KST 08:00~19:00 (cron + MQTT) |
| 스토리지 | 200GB 상한 자동 정리 (6시간마다) |
| DB | WAL 체크포인트 매일 04:00 |

### Step 2 — Thingsboard CE TB-1 독립 검증 ✅ 완료 (2026-04-09)
| 항목 | 내용 |
|------|------|
| 버전 | Thingsboard CE 4.2.1.1 (tb-postgres) |
| 포트 | 8080(UI/REST), 1884(MQTT), 7070(Edge RPC) |
| 기동 검증 | PASS 4/4 |
| 기기 모델 | mobile-cctv-site-001, 서버/공유 속성, MQTT 텔레메트리 |
| MQTT | 텔레메트리 6개 키 전송·조회 PASS 14/14 |
| 알람 규칙 | CPU>90, 디스크>180 트리거 PASS 7/7 |

### Device Profile 3종 + 가상 기기 3대 ✅ 완료 (2026-04-09)
| Profile | 기기명 | OS | 시나리오 | MQTT Token |
|---------|--------|-----|---------|-----------|
| settop | virtual_settop1 | **Android** | S1/S2 (USB 카메라 최대 1대) | ySaPv4sU2ZQPJuVYpwK9 |
| ip-camera | virtual_cctv1 | 임베디드 Linux | S2/S3 | g19dPQxZArjsACP02kRS |
| edge-controller | virtual_edge1 | Linux x86 | S3 (Frigate+로컬TB) | Tdsw3bDUmzRc1Yd3cl3x |

---

## 5. 확정된 플랫폼 전략

### 최상단 관제 솔루션
- **Thingsboard CE** — 기기·사용자·알람 관리 핵심
- **go2rtc** — 라이브 영상 중계 (저장 없음)
- Frigate는 에지(현장)에서만 — 영상 저장·AI 감지 전담
- 나중에 커스텀 UI(mobile-cctv-vms)가 Thingsboard REST API 호출

### 개발 환경 (두 가지 병행)
```
방법 A (즉시): Tailscale → 로컬 개발 PC 원격 접속
방법 B (구축 후): VS Code Remote SSH → Hetzner 클라우드 서버
```

### 클라우드 서버 (확정)
- **Hetzner CX32** — 4 vCPU / 8GB RAM / Ubuntu 24.04
- 월 약 13,000원 (€8.9), 싱가포르 리전
- 현재 docker-compose.yml 그대로 이전 가능

### 도구 스택 (최소화)
```
Tailscale + GitHub + Docker Compose + VS Code (Remote SSH) + Claude Code
```

---

## 6. 현재 미완료 / 다음 단계

| 단계 | 내용 | 선행 조건 |
|------|------|---------|
| **Phase A** | GitHub 연동 완료 ✅, Tailscale 설치 | 즉시 가능 |
| **Phase B** | Hetzner 서버 구축 + Thingsboard 이전 | Phase A 후 |
| **TB-2** | Frigate → Thingsboard 텔레메트리 연동 | 명시적 지시 후 시작 |
| **에지 기기** | 실제 settop/CCTV 연결 | 기기·네트워크 준비 후 |
| **커스텀 UI** | mobile-cctv-vms React 개발 | TB-2 이후 |

---

## 7. GitHub 저장소

```
저장소: github.com/brianroh2/Portable_CCTV_Infra
브랜치: main
로컬:   /home/visionlinux/workspace/infra
```

앞으로 파일 수정 후 백업:
```bash
cd /home/visionlinux/workspace/infra
git add .
git commit -m "변경 내용 설명"
git push
```

---

## 8. 새 대화 세션 — 문서 읽기 순서

Claude에게 다음 순서로 읽도록 지시:

```
1. infra/doc/temp_project_summary_0409.md     ← 이 파일 (전체 현황)
2. infra/doc/platform-strategy.md             ← 플랫폼 전략 확정안
3. infra/frigate/doc/project-overview.md      ← 하드웨어·네트워크·스택
4. infra/thingsboard/doc/architecture.md      ← Device Profile·시나리오 구조
5. infra/thingsboard/doc/walkthrough.md       ← API 차이·트러블슈팅 이력
```

세부 작업 시 추가로 읽을 문서:
```
frigate/doc/walkthrough.md     ← Frigate 운영 이력
frigate/doc/architecture.md    ← VMS+Fleet 통합 설계 (UI 개발 시 참조)
thingsboard/doc/project-overview.md ← 데이터 모델·연동 계획
```

---

## 9. 작업 규칙 (CLAUDE.md 요약)

| 규칙 | 내용 |
|------|------|
| 응답 언어 | 한국어 |
| 테스트 코드 위치 | 각 프로젝트 `temp_test/` 폴더 |
| 테스트 파일 상단 | 목적·배경·검증 항목 주석 필수 |
| 문서 업데이트 | 작업 완료 시 해당 프로젝트 `walkthrough.md` 변경 이력 추가 |
| Frigate↔Thingsboard 통합 | 명시적 지시 전까지 시작 안함 |
| 새 파일 제안 | 먼저 의견 묻고 확인 후 생성 ("만들어줘"면 바로 생성) |
