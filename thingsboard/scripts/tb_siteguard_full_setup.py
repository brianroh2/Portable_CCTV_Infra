#!/usr/bin/env python3
# SiteGuard Thingsboard 전체 설정
# 실행: python tb_siteguard_full_setup.py
# 수행: cctv-1/cctv-3 서버속성 추가 + 멀티카메라 그리드 대시보드 생성 + 기기 프로파일 대시보드

import requests
import json
import uuid

TB_URL = "http://localhost:8080"
TENANT_USER = "tenant@thingsboard.org"
TENANT_PASS = "tenant"
GO2RTC_EXT = "http://46.62.155.122/go2rtc"

CAMERAS = [
    {
        "name": "cctv-1",
        "label": "CCTV-1 TVT Dome",
        "stream": "cctv_1",
        "model": "TVT TD-9421S4C",
        "internal_ip": "192.168.1.51",
        "wan_port": 554,
        "main_rtsp_profile": "profile1",
        "main_resolution": "1920x1080",
        "main_fps": 30,
        "sub_rtsp_profile": "profile2",
        "sub_resolution": "640x480",
        "sub_fps": 10,
        "codec": "H.264",
        "audio": "없음",
        "location": "LTE 라우터 직접 연결 (포트1)",
        "ddns": "0004312.m2mnet.kr",
    },
    {
        "name": "cctv-3",
        "label": "CCTV-3 VHT Dome F977",
        "stream": "cctv_3",
        "model": "Vision Hitech TBT-Dome F977",
        "internal_ip": "192.168.1.53",
        "wan_port": 555,
        "main_rtsp_profile": "Ch1",
        "main_resolution": "1920x1080",
        "main_fps": 30,
        "sub_rtsp_profile": "Ch2",
        "sub_resolution": "640x480",
        "sub_fps": 10,
        "codec": "H.264",
        "audio": "없음",
        "location": "POE 스위치 연결 (192.168.1.53)",
        "ddns": "0004312.m2mnet.kr",
    },
]


def login():
    r = requests.post(f"{TB_URL}/api/auth/login",
                      json={"username": TENANT_USER, "password": TENANT_PASS})
    r.raise_for_status()
    return r.json()["token"]


def h(token):
    return {"X-Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_device_id(token, name):
    r = requests.get(f"{TB_URL}/api/tenant/devices?pageSize=100&page=0", headers=h(token))
    r.raise_for_status()
    for dev in r.json().get("data", []):
        if dev["name"] == name:
            return dev["id"]["id"]
    return None


def get_profile_id(token, name):
    r = requests.get(f"{TB_URL}/api/deviceProfiles?pageSize=50&page=0", headers=h(token))
    r.raise_for_status()
    for p in r.json().get("data", []):
        if p["name"] == name:
            return p["id"]["id"]
    return None


def set_server_attributes(token, device_id, attrs):
    r = requests.post(
        f"{TB_URL}/api/plugins/telemetry/DEVICE/{device_id}/SERVER_SCOPE",
        headers=h(token), json=attrs,
    )
    r.raise_for_status()


def delete_dashboards_by_title(token, title):
    r = requests.get(f"{TB_URL}/api/tenant/dashboards?pageSize=100&page=0", headers=h(token))
    r.raise_for_status()
    deleted = []
    for db in r.json().get("data", []):
        if db["title"] == title:
            db_id = db["id"]["id"]
            requests.delete(f"{TB_URL}/api/dashboard/{db_id}", headers=h(token))
            deleted.append(db_id)
    return deleted


def make_widget(type_fqn, widget_type, title, settings, row, col, sx, sy,
                datasources=None, show_title=False):
    wid = str(uuid.uuid4())
    w = {
        "id": wid,
        "typeFullFqn": type_fqn,
        "type": widget_type,
        "sizeX": sx,
        "sizeY": sy,
        "row": row,
        "col": col,
        "config": {
            "datasources": datasources or [],
            "settings": settings,
            "title": title,
            "showTitle": show_title,
            "dropShadow": False,
            "enableFullscreen": False,
            "titleStyle": {"fontSize": "13px", "fontWeight": "500"},
            "widgetStyle": {"padding": "0"},
            "actions": {},
        },
    }
    return wid, w


def build_grid_dashboard():
    """멀티 카메라 그리드 대시보드 — camera-grid.html iframe 임베드"""
    card_html = (
        '<iframe src="/camera-grid.html" '
        'style="width:100%;height:100%;border:none;display:block;" '
        'allowfullscreen></iframe>'
    )
    card_css = "html,body{margin:0;padding:0;overflow:hidden;}"

    wid, w = make_widget(
        "system.cards.html_card", "latest", "SiteGuard 현장 관제",
        {"cardHtml": card_html, "cardCss": card_css},
        row=0, col=0, sx=24, sy=21,
    )

    return wid, {
        "title": "SiteGuard 현장 관제",
        "configuration": {
            "description": "LTE 현장 CCTV 멀티카메라 그리드 관제",
            "widgets": {wid: w},
            "states": {
                "default": {
                    "name": "현장 관제",
                    "root": True,
                    "layouts": {
                        "main": {
                            "widgets": {wid: {"sizeX": 24, "sizeY": 21, "row": 0, "col": 0}},
                            "gridSettings": {
                                "columns": 24,
                                "color": "#0f1117",
                                "backgroundSize": "100%",
                                "backgroundImageUrl": "",
                                "mobileAutoFillHeight": False,
                                "mobileRowHeight": 70,
                            },
                        }
                    },
                }
            },
            "entityAliases": {},
            "filters": {},
        },
    }


def build_device_dashboard(cam):
    """개별 기기 대시보드 — 영상 + 스펙 테이블"""
    alias_id = str(uuid.uuid4())
    alias = {
        alias_id: {
            "id": alias_id,
            "alias": cam["name"],
            "filter": {
                "type": "entityName",
                "resolveMultiple": False,
                "entityNameFilter": cam["name"],
            },
        }
    }

    stream_url = f"{GO2RTC_EXT}/stream.html?src={cam['stream']}&mode=mse"
    video_html = (
        f'<div style="width:100%;height:100%;background:#000;overflow:hidden;">'
        f'<iframe src="{stream_url}" style="width:100%;height:100%;border:none;" allowfullscreen></iframe>'
        f'</div>'
    )
    video_css = "html,body{margin:0;padding:0;overflow:hidden;}"

    td_k = 'style="padding:4px 8px 4px 0;color:#888;width:42%;vertical-align:top;"'
    td_v = 'style="color:#ddd;font-size:11px;"'
    td_h = 'style="padding:8px 0 4px;color:#4db6ac;font-size:11px;font-weight:700;letter-spacing:.5px;" colspan="2"'
    attrs_html = f"""<div style="padding:12px;font-family:sans-serif;color:#ccc;background:#0f1117;height:100%;overflow:auto;">
  <h3 style="color:#4db6ac;margin:0 0 10px;font-size:13px;border-bottom:1px solid #2a2a4a;padding-bottom:6px;">{cam['label']} — 기기 정보</h3>
  <table style="width:100%;border-collapse:collapse;font-size:12px;">
    <tr><td {td_k}>모델</td><td {td_v}>{cam['model']}</td></tr>
    <tr><td {td_k}>내부 IP</td><td {td_v}>{cam['internal_ip']}</td></tr>
    <tr><td {td_k}>WAN 포트</td><td {td_v}>{cam['wan_port']}</td></tr>
    <tr><td {td_k}>코덱</td><td {td_v}>{cam['codec']}</td></tr>
    <tr><td {td_k}>오디오</td><td {td_v}>{cam['audio']}</td></tr>
    <tr><td {td_k}>위치</td><td {td_v}>{cam['location']}</td></tr>
    <tr><td {td_k}>DDNS</td><td {td_v}>{cam['ddns']}</td></tr>
    <tr><td {td_h}>▶ 메인 스트림 (1080p)</td></tr>
    <tr><td {td_k}>프로파일</td><td {td_v}>{cam['main_rtsp_profile']}</td></tr>
    <tr><td {td_k}>해상도</td><td {td_v}>{cam['main_resolution']}</td></tr>
    <tr><td {td_k}>프레임</td><td {td_v}>{cam['main_fps']} fps</td></tr>
    <tr><td {td_k}>외부 RTSP</td><td style="color:#aaa;font-size:10px;word-break:break-all;">rtsp://{cam['ddns']}:{cam['wan_port']}/{cam['main_rtsp_profile']}</td></tr>
    <tr><td {td_h}>▶ 서브 스트림 ★현재 사용 (go2rtc)</td></tr>
    <tr><td {td_k}>프로파일</td><td {td_v}>{cam['sub_rtsp_profile']}</td></tr>
    <tr><td {td_k}>해상도</td><td {td_v}>{cam['sub_resolution']}</td></tr>
    <tr><td {td_k}>프레임</td><td {td_v}>{cam['sub_fps']} fps</td></tr>
    <tr><td {td_k}>외부 RTSP</td><td style="color:#aaa;font-size:10px;word-break:break-all;">rtsp://{cam['ddns']}:{cam['wan_port']}/{cam['sub_rtsp_profile']}</td></tr>
  </table>
</div>"""

    wid_v, w_v = make_widget(
        "system.cards.html_card", "latest", f"{cam['label']} 라이브",
        {"cardHtml": video_html, "cardCss": video_css},
        row=0, col=0, sx=16, sy=12,
    )
    wid_a, w_a = make_widget(
        "system.cards.html_card", "latest", f"{cam['label']} 기기 정보",
        {"cardHtml": attrs_html, "cardCss": ""},
        row=0, col=16, sx=8, sy=12,
    )

    widgets_def = {wid_v: w_v, wid_a: w_a}
    layout_w = {
        wid_v: {"sizeX": 16, "sizeY": 12, "row": 0, "col": 0},
        wid_a: {"sizeX": 8,  "sizeY": 12, "row": 0, "col": 16},
    }

    return {
        "title": f"SiteGuard — {cam['label']}",
        "configuration": {
            "description": f"{cam['label']} 영상 및 기기 정보",
            "widgets": widgets_def,
            "states": {
                "default": {
                    "name": cam["label"],
                    "root": True,
                    "layouts": {
                        "main": {
                            "widgets": layout_w,
                            "gridSettings": {
                                "columns": 24,
                                "color": "#0f1117",
                                "backgroundSize": "100%",
                                "backgroundImageUrl": "",
                                "mobileAutoFillHeight": False,
                                "mobileRowHeight": 70,
                            },
                        }
                    },
                }
            },
            "entityAliases": alias,
            "filters": {},
        },
    }


def set_device_dashboard(token, device_id, dashboard_id):
    """기기 관련 대시보드 ID를 서버 속성에 저장 (TB 기기 상세 화면 연동용)"""
    set_server_attributes(token, device_id, {"device_dashboard_id": dashboard_id})


def update_profile_dashboard(token, profile_id, dashboard_id):
    """ip-camera 프로파일에 기본 대시보드 설정"""
    r = requests.get(f"{TB_URL}/api/deviceProfile/{profile_id}", headers=h(token))
    r.raise_for_status()
    profile = r.json()
    profile["defaultDashboardId"] = {"id": dashboard_id, "entityType": "DASHBOARD"}
    r2 = requests.post(f"{TB_URL}/api/deviceProfile", headers=h(token), json=profile)
    r2.raise_for_status()


def main():
    print("=== SiteGuard Thingsboard 전체 설정 ===\n")

    print("[1/5] TB 로그인...")
    token = login()
    print("   OK")

    print("\n[2/5] 기기 서버 속성 설정...")
    for cam in CAMERAS:
        dev_id = get_device_id(token, cam["name"])
        if not dev_id:
            print(f"   SKIP: 기기 없음 — {cam['name']}")
            continue
        attrs = {
            "model":                cam["model"],
            "internal_ip":          cam["internal_ip"],
            "wan_port":             cam["wan_port"],
            "codec":                cam["codec"],
            "audio":                cam["audio"],
            "location":             cam["location"],
            "ddns":                 cam["ddns"],
            # 메인 스트림
            "main_rtsp_profile":    cam["main_rtsp_profile"],
            "main_resolution":      cam["main_resolution"],
            "main_fps":             cam["main_fps"],
            "rtsp_url_main":        f"rtsp://{cam['ddns']}:{cam['wan_port']}/{cam['main_rtsp_profile']}",
            # 서브 스트림 (go2rtc 현재 사용)
            "sub_rtsp_profile":     cam["sub_rtsp_profile"],
            "sub_resolution":       cam["sub_resolution"],
            "sub_fps":              cam["sub_fps"],
            "rtsp_url_external":    f"rtsp://{cam['ddns']}:{cam['wan_port']}/{cam['sub_rtsp_profile']}",
            "stream_url":           f"{GO2RTC_EXT}/stream.html?src={cam['stream']}&mode=mse",
        }
        set_server_attributes(token, dev_id, attrs)
        print(f"   OK: {cam['name']} — {len(attrs)}개 속성")

    print("\n[3/5] 기존 SiteGuard 대시보드 정리...")
    for title in ["SiteGuard 현장 관제", "SiteGuard — CCTV-1 TVT Dome",
                  "SiteGuard — CCTV-3 VHT Dome F977"]:
        ids = delete_dashboards_by_title(token, title)
        for did in ids:
            print(f"   DEL: {did}")
    print("   완료")

    print("\n[4/5] 메인 그리드 대시보드 생성...")
    _, grid_dashboard = build_grid_dashboard()
    r = requests.post(f"{TB_URL}/api/dashboard", headers=h(token), json=grid_dashboard)
    if r.status_code != 200:
        print(f"   FAIL: {r.status_code} — {r.text[:300]}")
        return
    grid_db_id = r.json()["id"]["id"]
    print(f"   OK: {grid_db_id}")

    print("\n[5/5] 기기별 대시보드 생성...")
    for cam in CAMERAS:
        dev_id = get_device_id(token, cam["name"])
        dev_dashboard = build_device_dashboard(cam)
        r = requests.post(f"{TB_URL}/api/dashboard", headers=h(token), json=dev_dashboard)
        if r.status_code != 200:
            print(f"   FAIL ({cam['name']}): {r.status_code}")
            continue
        dev_db_id = r.json()["id"]["id"]
        print(f"   OK: {cam['name']} → {dev_db_id}")
        if dev_id:
            set_server_attributes(token, dev_id, {"device_dashboard_id": dev_db_id})

    # ip-camera 프로파일에 그리드 대시보드 설정
    profile_id = get_profile_id(token, "ip-camera")
    if profile_id:
        try:
            update_profile_dashboard(token, profile_id, grid_db_id)
            print(f"   OK: ip-camera 프로파일 기본 대시보드 설정")
        except Exception as e:
            print(f"   WARN: 프로파일 대시보드 설정 실패 — {e}")

    print("\n" + "="*50)
    print("완료!")
    print(f"  메인 대시보드:  http://46.62.155.122:8080/dashboard/{grid_db_id}")
    print(f"  camera-grid.html: http://46.62.155.122:8080/camera-grid.html")

    return grid_db_id


if __name__ == "__main__":
    main()
