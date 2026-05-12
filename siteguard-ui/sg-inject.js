/* SiteGuard TB 커스터마이징 — index.html 주입 스크립트
 * 역할: Entities > Devices > 기기 클릭 시 tb-device-tabs 숨김 + camera-detail.html iframe 표시 */
(function () {
  'use strict';

  var DETAIL_PAGE = '/camera-detail.html';

  /* URL에서 device UUID 추출 — 패턴: /entities/devices/{uuid} */
  function getDeviceId() {
    var m = location.pathname.match(
      /\/entities\/devices\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i
    );
    return m ? m[1] : null;
  }

  var _lastDeviceId = null;
  var _timer        = null;

  function applyCustomPanel() {
    var deviceId = getDeviceId();
    var tabsEl   = document.querySelector('tb-device-tabs');

    /* tb-device-tabs가 없으면 할 일 없음 */
    if (!tabsEl) { _lastDeviceId = null; return; }

    /* 기본 탭 패널 숨김 */
    tabsEl.style.cssText = 'display:none!important;';

    var parent = tabsEl.parentElement;
    if (!parent) return;

    /* 기기 상세 페이지가 아니면 iframe 제거 */
    if (!deviceId) {
      var old = parent.querySelector('iframe.sg-cam-frame');
      if (old) old.remove();
      _lastDeviceId = null;
      return;
    }

    var iframe = parent.querySelector('iframe.sg-cam-frame');

    /* iframe 없으면 생성 */
    if (!iframe) {
      iframe = document.createElement('iframe');
      iframe.className = 'sg-cam-frame';
      iframe.style.cssText =
        'position:absolute;top:0;left:0;width:100%;height:100%;' +
        'border:none;display:block;z-index:1;background:#0f1117;';

      /* 부모가 상대 위치가 아니면 수정 */
      var ps = window.getComputedStyle(parent);
      if (ps.position === 'static') parent.style.position = 'relative';
      parent.style.overflow = 'hidden';

      parent.appendChild(iframe);
    }

    /* 기기 변경 시 src 업데이트 */
    if (deviceId !== _lastDeviceId) {
      iframe.src     = DETAIL_PAGE + '?id=' + deviceId;
      _lastDeviceId  = deviceId;
    }
  }

  function schedule() {
    clearTimeout(_timer);
    _timer = setTimeout(applyCustomPanel, 120);
  }

  /* DOM 변경 감시 */
  new MutationObserver(schedule).observe(document.documentElement, {
    subtree: true, childList: true
  });

  /* Angular 라우터 — pushState / replaceState 가로채기 */
  ['pushState', 'replaceState'].forEach(function (fn) {
    var orig = history[fn];
    history[fn] = function () {
      orig.apply(this, arguments);
      schedule();
    };
  });
  window.addEventListener('popstate', schedule);
})();
