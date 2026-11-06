# -*- coding: utf-8 -*-
"""
cn_lit.py — 中文文献代理库检索与下载模块（供 biomed-literature-pipeline 调用）

覆盖：
  * 知网 CNKI      —— 检索 + 直接下载 PDF（已验证）
  * 中华医学会     —— 中华医学期刊全文数据库 (yiigle) 检索 + 全文 HTML 抓取
                      （该代理对 PDF 下载返回 401，故走全文抓取）

依赖：playwright（使用系统 Edge，channel="msedge"；无 Edge 时回退 Chromium）
账号：~/.workbuddy/credentials/cn_proxy.json  或环境变量 GX_USER / GX_PW

CLI:
  python cn_lit.py search  "<query>" [-n 10] [--src cnki|zh] [--json out.json]
  python cn_lit.py dl      "<query>" [-n 3] [-o ./downloads] [--src cnki]
  python cn_lit.py zh-html <cmaid>   [-o ./downloads]
"""
import sys, os, re, json, time, argparse, datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("需要 playwright: pip install playwright"); raise

HERE = os.path.dirname(os.path.abspath(__file__))
CRED_PATHS = [
    os.path.expanduser(os.path.join("~", ".workbuddy", "credentials", "cn_proxy.json")),
]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
PORTAL = "http://lib.gxpass.cn"
CNKI_ITEMS = ["1", "2", "3", "146"]
ZH_ITEM = "74"
RS_HOST = "http://rs-yiigle-com-s.webvpn.bjmu.doc110.com"


# ---------------------------------------------------------------- config
def load_cred():
    for p in CRED_PATHS:
        if os.path.isfile(p):
            d = json.load(open(p, encoding="utf-8"))
            g = d.get("portals", {}).get("gxpass", {})
            return g.get("url", PORTAL), g.get("user"), g.get("password")
    return PORTAL, os.environ.get("GX_USER"), os.environ.get("GX_PW")


# ---------------------------------------------------------------- browser
def _launch(p, headless=True):
    last = None
    for kw in ({"channel": "msedge"}, {}):
        try:
            return p.chromium.launch(headless=headless,
                                     args=["--disable-blink-features=AutomationControlled"], **kw)
        except Exception as e:
            last = e
    raise last


def _new_ctx(b):
    return b.new_context(ignore_https_errors=True, accept_downloads=True, user_agent=UA,
                         viewport={"width": 1500, "height": 950}, locale="zh-CN")


def login(page, portal, user, pw, tries=4):
    """登录门户。SPA 表单可能偶发未渲染（上游 webvpn no_connect），
    先等待占位符，超时则 reload 重来，最多 tries 次。"""
    last = None
    for t in range(tries):
        try:
            page.goto(portal + "/#/login", wait_until="domcontentloaded")
            try:
                page.wait_for_selector('input[placeholder="输入卡号/账号"]', timeout=20000)
            except Exception:
                page.reload(wait_until="domcontentloaded"); time.sleep(3)
                page.wait_for_selector('input[placeholder="输入卡号/账号"]', timeout=20000)
            page.get_by_placeholder("输入卡号/账号").fill(user)
            page.get_by_placeholder("输入密码").fill(pw)
            page.get_by_role("button", name="马上登录").click(); time.sleep(3.5)
            tok = page.evaluate("()=>sessionStorage.getItem('token')")
            if tok:
                return tok
            last = RuntimeError("登录后未拿到 token")
        except Exception as e:
            last = e
            time.sleep(2)
    raise RuntimeError(f"登录失败：{last}（请检查账号/密码或门户可用性）")


def _arrived(page, portal, want):
    try:
        u = page.url
    except Exception:
        return False
    if want and want in u:
        return True
    if not want and u and portal not in u and "rk.php" not in u and "00.php" not in u:
        return True
    return False


def open_db(page, portal, itemid, want=None, tries=3, each=10):
    """打开某数据库入口。注意：SPA 的 hash 路由切换不会重挂载组件，
    必须在 goto 后 reload 才会触发 Auth.php 授权跳转。"""
    for t in range(tries):
        for action in ("goto", "reload"):
            try:
                if action == "goto":
                    page.goto(f"{portal}/#/item?itemId={itemid}", wait_until="domcontentloaded")
                else:
                    page.reload(wait_until="domcontentloaded")
            except Exception:
                pass
            for _ in range(each):
                time.sleep(2)
                if _arrived(page, portal, want):
                    return True
    return False


def open_any(page, portal, itemids, want, each=10):
    """依次尝试多个入口，成功即返回入口 id；用于并发满/入口失效时自动切换。"""
    for iid in itemids:
        if open_db(page, portal, iid, want=want, tries=1, each=each):
            return iid
    return None


# ---------------------------------------------------------------- CNKI
def cnki_search(page, q, n=10):
    page.wait_for_selector("#txt_search", timeout=45000)
    page.fill("#txt_search", q); time.sleep(0.4)
    try:
        page.click("input.search-btn")
    except Exception:
        page.press("#txt_search", "Enter")
    for _ in range(20):
        time.sleep(1.5)
        try:
            if page.eval_on_selector_all("table.result-table-list tbody tr", "e=>e.length") > 0:
                break
        except Exception:
            pass
    time.sleep(2)
    out = []
    for tr in page.query_selector_all("table.result-table-list tbody tr")[:n]:
        a = tr.query_selector("td.name a")
        if not a:
            continue
        tds = tr.query_selector_all("td")
        cells = [(td.inner_text() or "").strip() for td in tds]
        out.append({
            "title": (a.inner_text() or "").strip(),
            "dl": a.get_attribute("href") or "",
            "author": cells[2] if len(cells) > 2 else "",
            "source": cells[3] if len(cells) > 3 else "",
            "date": cells[4] if len(cells) > 4 else "",
            "type": cells[5] if len(cells) > 5 else "",
            "src": "CNKI",
        })
    return out


def cnki_pdf(ctx, dl_url):
    """代理下载链接 -> 中间页 -> docdown.cnki.net -> PDF bytes"""
    inter = ctx.request.get(dl_url, timeout=60000)
    html = inter.text()
    m = re.search(r'href="(https://docdown\.cnki\.net/docdown/fulltext/download\?[^"]+)"', html)
    if not m:
        m = re.search(r'(https://docdown\.cnki\.net/docdown/fulltext/download\?[^\s"\'<>]+)', html)
    if not m:
        return None, "no-docdown-url"
    real = m.group(1).replace("&amp;", "&")
    r = ctx.request.get(real, timeout=120000)
    body = r.body()
    if body[:4] == b"%PDF":
        return body, None
    return None, f"not-pdf(status={r.status},ct={r.headers.get('content-type')})"


# ---------------------------------------------------------------- 中华医学会
def _zh_ready(page, tries=30):
    """等待中华医学期刊全文数据库页面真正就绪（搜索框可用）。"""
    for _ in range(tries):
        try:
            if page.eval_on_selector_all('input[placeholder*="主题"]', "e=>e.length") > 0:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def zh_search(page, q, n=10):
    """中华医学期刊全文数据库检索。结果行右侧有「全文HTML / 下载PDF」两个按钮。"""
    _zh_ready(page)
    time.sleep(2)
    for _attempt in range(4):
        try:
            page.evaluate("""(q) => {
                const els=document.querySelectorAll('input[placeholder*="主题"]');
                let e=null;
                for(const x of els){const r=x.getBoundingClientRect(); if(r.width>50){e=x;break;}}
                if(!e) e=els[els.length-1];
                if(!e) return;
                e.focus();
                const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
                s.call(e,q);
                e.dispatchEvent(new Event('input',{bubbles:true}));
                e.dispatchEvent(new Event('change',{bubbles:true}));
                for(const t of ['keydown','keypress','keyup'])
                    e.dispatchEvent(new KeyboardEvent(t,{key:'Enter',keyCode:13,which:13,bubbles:true}));
            }""", q)
            break
        except Exception as e:
            if "destroyed" not in str(e) and "navigation" not in str(e):
                raise
            time.sleep(3)
            _zh_ready(page, 10)
    for _ in range(18):
        time.sleep(2)
        try:
            if "检索结果" in (page.title() or ""):
                break
        except Exception:
            pass
    time.sleep(4)
    rows = page.evaluate("""() => {
        const titleOf = (btn) => {
            let node=btn;
            while(node){
                const ts=node.querySelectorAll('a[title]');
                if(ts.length===1) return (ts[0].innerText||ts[0].getAttribute('title')||'').trim();
                if(ts.length>1) return '';      // 已越过行容器，停止
                node=node.parentElement;
            }
            return '';
        };
        const out=[];
        document.querySelectorAll('div.s_searchResult_li_button_r').forEach(btn=>{
            const dl_a = [...btn.querySelectorAll('a')].find(a=>/下载PDF/.test(a.innerText||''));
            out.push({title: titleOf(btn), has_dl: !!dl_a, src: '中华医学会'});
        });
        return out;
    }""")
    return rows[:n]


def zh_download(page, maxn=5, outdir="."):
    """点击结果行右侧的「下载PDF」按钮直接下载（用户确认可行）。"""
    os.makedirs(outdir, exist_ok=True)
    titles = page.evaluate("""() => {
        const titleOf = (btn) => {
            let node=btn;
            while(node){
                const ts=node.querySelectorAll('a[title]');
                if(ts.length===1) return (ts[0].innerText||ts[0].getAttribute('title')||'').trim();
                if(ts.length>1) return '';
                node=node.parentElement;
            }
            return '';
        };
        const out=[];
        document.querySelectorAll('div.s_searchResult_li_button_r').forEach(btn=>out.push(titleOf(btn)));
        return out;
    }""")
    links = page.locator('div.s_searchResult_li_button_r a').filter(has_text="下载PDF")
    cnt = links.count()
    got = []
    for i in range(min(maxn, cnt)):
        title = titles[i] if i < len(titles) else f"zh_{i+1}"
        try:
            lnk = links.nth(i)
            lnk.scroll_into_view_if_needed(timeout=10000)
            time.sleep(0.4)
            with page.expect_download(timeout=90000) as di:
                lnk.click(timeout=15000)
            d = di.value
            raw = d.suggested_filename or f"{title}.pdf"      # 服务器给的文件名最准
            safe = re.sub(r'[\\/:*?"<>|]', "_", raw)[:90]
            fn = os.path.join(outdir, safe)
            d.save_as(fn)
            size = os.path.getsize(fn)
            ok = open(fn, "rb").read(4) == b"%PDF"
            real_title = os.path.splitext(raw)[0] or title
            got.append({"title": real_title, "file": fn, "size": size, "pdf": ok})
            print(f"[{'OK' if ok else '??'}] {real_title[:46]} -> {safe} ({size}B)", flush=True)
        except Exception as e:
            got.append({"title": title, "error": type(e).__name__ + ":" + str(e)[:80]})
            print(f"[FAIL] {title[:46]} : {type(e).__name__}", flush=True)
        time.sleep(1.5)
    return got


def zh_fulltext(ctx, cmaid):
    r = ctx.request.get(f"{RS_HOST}/cmaid/{cmaid}", timeout=60000)
    return r.text()


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description="中文文献代理库检索/下载")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("-n", type=int, default=10)
    s.add_argument("--src", choices=["cnki", "zh"], default="cnki"); s.add_argument("--json")
    d = sub.add_parser("dl"); d.add_argument("query"); d.add_argument("-n", type=int, default=3)
    d.add_argument("-o", default=os.path.join(HERE, "..", "downloads"))
    zd = sub.add_parser("zh-dl"); zd.add_argument("query"); zd.add_argument("-n", type=int, default=3)
    zd.add_argument("-o", default=os.path.join(HERE, "..", "downloads"))
    z = sub.add_parser("zh-html"); z.add_argument("cmaid"); z.add_argument("-o", default=".")
    a = ap.parse_args()

    portal, user, pw = load_cred()
    if not user or not pw:
        print("缺少账号：请创建 ~/.workbuddy/credentials/cn_proxy.json 或设置 GX_USER/GX_PW"); return 1

    with sync_playwright() as p:
        b = _launch(p); ctx = _new_ctx(b); page = ctx.new_page(); page.set_default_timeout(60000)
        try:
            login(page, portal, user, pw)
            if a.cmd == "search" and a.src == "cnki":
                if not open_any(page, portal, CNKI_ITEMS, "defaultresult"): raise RuntimeError("打不开知网（所有入口失败）")
                res = cnki_search(page, a.query, a.n)
            elif a.cmd == "search":
                if not open_any(page, portal, [ZH_ITEM], "yiigle"): raise RuntimeError("打不开中华医学会")
                res = zh_search(page, a.query, a.n)
            elif a.cmd == "dl":
                if not open_any(page, portal, CNKI_ITEMS, "defaultresult"): raise RuntimeError("打不开知网（所有入口失败）")
                res = cnki_search(page, a.query, a.n)
                os.makedirs(a.o, exist_ok=True)
                for i, r in enumerate(res, 1):
                    pdf, err = cnki_pdf(ctx, r["dl"])
                    if pdf:
                        fn = os.path.join(a.o, f"{i:02d}_{re.sub(r'[\\\\/:*?\"<>|]','_',r['title'])[:60]}.pdf")
                        open(fn, "wb").write(pdf); r["file"] = fn
                        print(f"[OK] {r['title'][:50]} -> {os.path.basename(fn)} ({len(pdf)}B)")
                    else:
                        r["error"] = err; print(f"[FAIL] {r['title'][:50]} : {err}")
            elif a.cmd == "zh-html":
                if not open_any(page, portal, [ZH_ITEM], "yiigle"): raise RuntimeError("打不开中华医学会")
                os.makedirs(a.o, exist_ok=True)
                html = zh_fulltext(ctx, a.cmaid)
                fn = os.path.join(a.o, f"zh_{a.cmaid}.html"); open(fn, "w", encoding="utf-8").write(html)
                print(f"[OK] {fn} ({len(html)} chars)")
                res = [{"cmaid": a.cmaid, "file": fn}]
            elif a.cmd == "zh-dl":
                if not open_any(page, portal, [ZH_ITEM], "yiigle"): raise RuntimeError("打不开中华医学会")
                zh_search(page, a.query, max(a.n, 10))
                res = zh_download(page, a.n, a.o)
            print(json.dumps(res, ensure_ascii=False, indent=1))
            if getattr(a, "json", None):
                json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        finally:
            b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
