# 프로젝트 컨텍스트 (Claude 자동 로드)

## 이 워크스페이스에 대해

이동형 CCTV 관제 솔루션 상용화 프로젝트의 **인프라 레이어**.
1인 개발자가 단계적으로 구축 중이며, 각 서비스는 독립 검증 후 통합한다.

```
infra/
├── frigate/       ← VMS 인프라 (Frigate 0.17.1) — Step 1 완료
└── thingsboard/   ← Fleet Management (Thingsboard CE) — Step 2 진행 중
```

## 각 프로젝트 현황

**frigate/** — 완료 (2026-04-08)
- Frigate 0.17.1 + Mosquitto, Intel OpenVINO GPU 가속, 카메라 3대
- 이벤트 녹화(8초 클립, 7일), 감지 시간대 KST 08~19시, 200GB 상한
- 문서: frigate/README.md 참조

**thingsboard/** — 독립 검증 중 (2026-04-09 시작)
- Thingsboard CE, 포트 8080(UI) / 1884(MQTT)
- 현재 단계: 기동 검증 → 기기 데이터 모델 → Frigate 연동(별도 지시 후)
- 문서: thingsboard/README.md 참조

## 작업 규칙

- 테스트 코드: 각 프로젝트 `temp_test/` 폴더, 상단 목적 주석 필수
- 문서 업데이트: 작업 완료 시 해당 프로젝트 `doc/walkthrough.md` 변경 이력 추가
- Frigate↔Thingsboard 통합: 사용자가 명시적으로 지시할 때까지 시작 안함
- 응답 언어: 한국어
