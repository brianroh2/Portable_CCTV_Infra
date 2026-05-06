# go2rtc 운영 문서 (Walkthrough)

> 문서 성격: go2rtc 설정 이력 + 트러블슈팅 모음
> 섹션 1 (현황 스냅샷)은 작업할 때마다 **덮어쓴다.**
> 섹션 2 (지식 베이스)와 섹션 3 (변경 이력)은 **위에 추가만** 한다.

---

## 섹션 1 — 현재 운영 현황 스냅샷

> 마지막 업데이트: 2026-04-14

### 1-1. 서비스 상태

| 항목 | 내용 |
|------|------|
| 버전 | alexxit/go2rtc:1.9.9 |
| 위치 | Hetzner (46.62.155.122) |
| Web UI / API | http://46.62.155.122:1984 |
| RTSP 재스트리밍 | rtsp://46.62.155.122:8555/{stream_name} |
| 설정 파일 | `go2rtc/go2rtc.yaml` |
| 네트워크 | host 모드 (Tailscale 접근 필수) |

### 1-2. 카메라 스트림 현황

| 스트림명 | 카메라 | 해상도 | 소스 경로 |
|---------|--------|--------|----------|
| cctv_1 | TBT-Dome 765E (192.168.0.6) | 640x480 | profile2 (sub stream) |
| cctv_2 | Vision Hitech F977 (192.168.0.7) | 640x480 / 10fps | Ch2 (sub stream) |
| cctv_3 | Vision Hitech F99D (192.168.0.8) | 640x480 / 10fps | Ch2 (sub stream) |

> Frigate(로컬)는 main stream 사용. go2rtc(클라우드)는 sub stream으로 대역폭 절감.

### 1-3. 카메라 연결 표준 패턴

```yaml
# 신규 카메라 추가 시 반드시 이 패턴 사용
# 이유: Tailscale 서브넷 경유 시 UDP RTP 불통 + 제조사 비트스트림 포맷 차이
camera_name: exec:ffmpeg -hide_banner -rtsp_transport tcp \
  -i rtsp://user:pass@192.168.0.x:554/substream_path \
  -c:v copy -f mpegts -
```

### 1-4. 빠른 상태 확인 명령어

```bash
# 컨테이너 상태
docker ps --format "table {{.Names}}\t{{.Status}}"

# 스트림 등록 상태
curl -s http://localhost:1984/api/streams | python3 -m json.tool

# 로그 확인
docker logs go2rtc --tail 30

# 신규 카메라 사전 검증 (Hetzner에서 실행)
docker run --rm --network host alexxit/go2rtc:1.9.9 \
  ffprobe -v quiet -rtsp_transport tcp \
  -i "rtsp://user:pass@192.168.0.x:554/substream" -show_streams
```

---

## 섹션 2 — 운영 지식 (Knowledge Base)

### 2-A. 로컬 vs 클라우드 카메라 연결 차이

로컬 PC(Frigate)에서 정상 동작하는 카메라 설정이 클라우드(Hetzner)에서 그대로 통하지 않는다.

| 조건 | 로컬 직접 연결 | 클라우드 (Tailscale 서브넷 경유) |
|------|-------------|-------------------------------|
| RTSP 전송 | UDP/TCP 모두 가능 | TCP 강제 필수 |
| 영상 전송(RTP) | UDP 정상 | UDP 역방향 차단 → TCP interleaved 필수 |
| 비트스트림 | 카메라 원본 OK | 제조사 포맷 차이 → MPEG-TS 래핑 |
| 테스트 도구 | ffplay (로컬 터미널) | ffprobe -rtsp_transport tcp (Hetzner에서) |

**검증 순서:**
```
1. 로컬 PC: ffplay rtsp://... → 카메라 동작 확인
2. Hetzner: ffprobe -rtsp_transport tcp ... → 클라우드 접근 가능 여부 확인
3. go2rtc.yaml: exec:ffmpeg 패턴으로 작성 → 브라우저에서 최종 확인
```

### 2-B. 카메라 제조사별 연결 방식 정리

| 제조사 | 기본 전송 | Tailscale 경유 | 비고 |
|--------|---------|--------------|------|
| TBT-Dome (765E) | TCP 호환 | plain RTSP 가능 | profile1(main), profile2(sub) |
| Vision Hitech (F977, F99D) | UDP 기본 | exec:ffmpeg 필수 | Ch1(main), Ch2(sub), `-f mpegts` 필수 |
| **신규 (미검증)** | 모름 | exec:ffmpeg 템플릿으로 시작 | 검증 후 최적화 |

---

## 섹션 3 — 변경 이력 (Changelog)

---

### [2026-04-14] go2rtc 최초 구축 — 카메라 3대 클라우드 스트리밍

**배경:** Hetzner 클라우드에서 에지 PC 카메라를 라이브 뷰하기 위한 go2rtc 구축.
Tailscale 서브넷 경유로 카메라(192.168.0.x)에 직접 접근.

**완료 항목:**
- `go2rtc/docker-compose.yml` 신규 작성 (network_mode: host)
- `go2rtc/go2rtc.yaml` 신규 작성 — 카메라 3대 sub stream 연결
- cctv_1: profile2, cctv_2/3: Ch2 (640x480, 10fps)
- 모든 카메라 `exec:ffmpeg -rtsp_transport tcp -f mpegts` 패턴으로 통일

**시행착오:**

| 시도 | 오류 | 원인 |
|------|------|------|
| `rtsp://...` plain RTSP (cctv_2/3) | 17초 후 스트림 종료 | UDP RTP 역방향 차단 |
| `rtsp://...?transport=tcp` | DESCRIBE 404 | `?transport=tcp`가 카메라 경로로 전달됨 |
| `exec:ffmpeg -f h264` | unsupported header | Vision Hitech 비트스트림이 Annex B 아님 |
| `exec:ffmpeg -bsf:v h264_mp4toannexb -f h264` | 동일 오류 | 변환 필터 효과 없음 |
| `exec:ffmpeg -f mpegts` | **성공** | MPEG-TS가 포맷 차이 흡수 |

**결론:** cctv_1(TBT-Dome)도 plain RTSP로 동작하지만 통일성·신규 카메라 일관성을 위해 exec:ffmpeg 패턴으로 통일.
