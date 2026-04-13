# 프로젝트 컨텍스트 (Claude 자동 로드)

이동형 CCTV 관제 솔루션 상용화 — 인프라 레이어. 1인 개발, 독립 검증 후 통합.

## 프로젝트 현황

| 프로젝트 | 상태 | 핵심 내용 |
|---------|------|---------|
| `frigate/` | ✅ Step 1 완료 (2026-04-08) | Frigate 0.17.1 + OpenVINO + 카메라 3대 |
| `thingsboard/` | ✅ TB-1 완료 (2026-04-09) | Device Profile 3종 + 가상기기 3대 PASS |
| TB-2 브리지 | ✅ 완료 (2026-04-13) | Frigate REST→클라우드TB MQTT, 60초 주기 |

**다음 단계:** Phase C (go2rtc, 에지 기기 연동) — 명시적 지시 후 시작
**상세 현황:** `doc/walkthrough.md` 참조

## 작업 규칙

- 응답 언어: 한국어
- 테스트 코드: 각 프로젝트 `temp_test/` 폴더, 상단 목적 주석 필수
- 문서 업데이트: 작업 완료 시 해당 프로젝트 `doc/walkthrough.md` 변경 이력 추가
- temp_test/ 변경 시: walkthrough.md의 PASS 횟수도 함께 업데이트
- Frigate↔Thingsboard 통합: 명시적 지시 전까지 시작 안함
- 새 파일 생성: 먼저 의견 묻고 확인 후 생성 ("만들어줘"는 바로 생성)
