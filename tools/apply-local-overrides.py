#!/usr/bin/env python3
"""Reapply the fork's small UI and release-channel customizations after upstream sync."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def remove_sponsor_ui() -> None:
    replacements = {
        "frontend/src/pages/index/IndexPage.tsx": [
            ("import SponsorSlot from '@/components/sponsor/SponsorSlot';\n", ""),
            ('                  <SponsorSlot slot="dashboard" />\n', ""),
        ],
        "frontend/src/pages/login/LoginPage.tsx": [
            ("import SponsorSlot from '@/components/sponsor/SponsorSlot';\n", ""),
            ('                <SponsorSlot slot="login" variant="compact" className="login-sponsor" />\n', ""),
        ],
        "frontend/src/routes/panelRoutes.tsx": [
            ("  CrownOutlined,\n", ""),
            ("const SponsorsPage = lazy(() => import('@/pages/sponsors/SponsorsPage'));\n", ""),
            ("  { path: '/sponsors', titleKey: 'menu.sponsors', icon: CrownOutlined, component: SponsorsPage },\n", ""),
        ],
    }

    for relative, pairs in replacements.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            text = text.replace(old, new)
        if relative.endswith("IndexPage.tsx") and "SponsorSlot" in text:
            raise RuntimeError(f"Unrecognized sponsor placement remains in {relative}")
        if relative.endswith("LoginPage.tsx") and "SponsorSlot" in text:
            raise RuntimeError(f"Unrecognized sponsor placement remains in {relative}")
        if relative.endswith("panelRoutes.tsx") and ("SponsorsPage" in text or "'/sponsors'" in text):
            raise RuntimeError(f"Unrecognized sponsor route remains in {relative}")
        path.write_text(text, encoding="utf-8", newline="\n")

    palette = ROOT / "frontend/src/components/command-palette/CommandPalette.tsx"
    text = palette.read_text(encoding="utf-8")
    text = re.sub(r"^\s*'/sponsors':.*\n", "", text, flags=re.MULTILINE)
    if "'/sponsors'" in text:
        raise RuntimeError("Unrecognized sponsor command-palette entry remains")
    palette.write_text(text, encoding="utf-8", newline="\n")

    translation_dir = ROOT / "internal/web/translation"
    locale_files = sorted(translation_dir.glob("*.json"))
    if not locale_files:
        raise RuntimeError("No translation JSON files found")
    for path in locale_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.get("menu", {}).pop("sponsors", None)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def use_fork_dev_release() -> None:
    install = ROOT / "install.sh"
    text = install.read_text(encoding="utf-8")
    start = text.index("resolve_latest_tag() {")
    end = text.index("\n}\n", start) + 3
    text = text[:start] + '''resolve_latest_tag() {
    # This fork publishes a rolling dev-latest build after each upstream sync.
    echo "dev-latest"
}
''' + text[end:]
    text = text.replace(
        "# resolve_latest_tag prints the latest stable release tag. It prefers the web\n# releases/latest redirect, which is not subject to the unauthenticated API's\n# 60 req/h-per-IP limit that trips shared CI/CGNAT addresses (the install then\n# fails with \"Failed to fetch x-ui version\"), and falls back to the API.",
        "# resolve_latest_tag selects this fork's rolling release.",
    )
    text = text.replace("https://github.com/MHSanaei/3x-ui/releases/download/", "https://github.com/kakbga/3x-ui/releases/download/")
    text = text.replace("https://raw.githubusercontent.com/MHSanaei/3x-ui/", "https://raw.githubusercontent.com/kakbga/3x-ui/")
    if "https://github.com/MHSanaei/3x-ui/releases/" in text:
        raise RuntimeError("install.sh still points at upstream release assets")
    install.write_text(text, encoding="utf-8", newline="\n")

    update = ROOT / "update.sh"
    text = update.read_text(encoding="utf-8")
    old_default = r'''    else
        tag_version=$(${curl_bin} -Ls "https://api.github.com/repos/MHSanaei/3x-ui/releases/latest" 2> /dev/null | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
        if [[ ! -n "$tag_version" ]]; then
            _fail "ERROR: Failed to fetch x-ui version, it may be due to GitHub API restrictions, please try it later"
        fi
    fi'''
    new_default = '''    else
        tag_version="dev-latest"
        echo -e "${green}正在使用本仓库滚动版本：${tag_version}${plain}"
    fi'''
    text = text.replace(old_default, new_default)
    text = text.replace(
        'echo -e "${green}Using your fork\'s rolling build: ${tag_version}${plain}"',
        'echo -e "${green}正在使用本仓库滚动版本：${tag_version}${plain}"',
    )
    if 'tag_version="dev-latest"' not in text:
        raise RuntimeError("Could not switch update.sh's default channel to dev-latest")
    if "https://api.github.com/repos/MHSanaei/3x-ui/releases/latest" in text:
        raise RuntimeError("Could not switch update.sh's default channel to dev-latest")
    text = text.replace("https://github.com/MHSanaei/3x-ui/releases/download/", "https://github.com/kakbga/3x-ui/releases/download/")
    text = text.replace("https://raw.githubusercontent.com/MHSanaei/3x-ui/", "https://raw.githubusercontent.com/kakbga/3x-ui/")
    text = text.replace("# rolling dev-latest pre-release). Empty keeps the default latest-stable flow.", "# rolling dev-latest pre-release). Empty selects this fork's rolling build.")
    if "https://github.com/MHSanaei/3x-ui/releases/" in text:
        raise RuntimeError("update.sh still points at upstream release assets")
    update.write_text(text, encoding="utf-8", newline="\n")

    menu = ROOT / "x-ui.sh"
    text = menu.read_text(encoding="utf-8")
    text = text.replace("https://raw.githubusercontent.com/MHSanaei/3x-ui/", "https://raw.githubusercontent.com/kakbga/3x-ui/")
    menu.write_text(text, encoding="utf-8", newline="\n")

    sidebar = ROOT / "frontend/src/layouts/AppSidebar.tsx"
    text = sidebar.read_text(encoding="utf-8")
    text = text.replace(
        "const REPO_URL = 'https://github.com/MHSanaei/3x-ui';",
        "const REPO_URL = 'https://github.com/kakbga/3x-ui/releases/tag/dev-latest';",
    )
    if "const REPO_URL = 'https://github.com/MHSanaei/3x-ui';" in text:
        raise RuntimeError("AppSidebar version link still points at the upstream repository")
    sidebar.write_text(text, encoding="utf-8", newline="\n")

    panel = ROOT / "internal/web/service/panel/panel.go"
    text = panel.read_text(encoding="utf-8")
    text = text.replace(
        "https://raw.githubusercontent.com/MHSanaei/3x-ui/",
        "https://raw.githubusercontent.com/kakbga/3x-ui/",
    )
    text = text.replace(
        "https://api.github.com/repos/MHSanaei/3x-ui/",
        "https://api.github.com/repos/kakbga/3x-ui/",
    )
    if "https://raw.githubusercontent.com/MHSanaei/3x-ui/" in text or "https://api.github.com/repos/MHSanaei/3x-ui/" in text:
        raise RuntimeError("Panel updater still points at the upstream repository")
    panel.write_text(text, encoding="utf-8", newline="\n")

    release = ROOT / ".github/workflows/release.yml"
    text = release.read_text(encoding="utf-8")
    if "  publish-dev:" not in text:
        raise RuntimeError("release.yml no longer defines the rolling dev-latest release")
    text = text.replace("msystem: MINGW64", "msystem: UCRT64")
    text = text.replace("mingw-w64-x86_64-gcc", "mingw-w64-ucrt-x86_64-gcc")
    text = text.replace("mingw-w64-x86_64-sqlite3", "mingw-w64-ucrt-x86_64-sqlite3")
    text = text.replace("mingw-w64-x86_64-pkg-config", "mingw-w64-ucrt-x86_64-pkgconf")
    if any(
        marker in text
        for marker in (
            "msystem: MINGW64",
            "mingw-w64-x86_64-gcc",
            "mingw-w64-x86_64-sqlite3",
            "mingw-w64-x86_64-pkg-config",
            "mingw-w64-x86_64-pkgconf",
        )
    ):
        raise RuntimeError("release.yml still configures the deprecated MINGW64 environment")
    text = text.replace(
        "    if: github.event_name == 'push' && github.ref == 'refs/heads/main'",
        "    if: (github.event_name == 'push' || github.event_name == 'workflow_dispatch') && github.ref == 'refs/heads/main'",
    )
    if "workflow_dispatch') && github.ref == 'refs/heads/main'" not in text:
        raise RuntimeError("release.yml cannot publish dev-latest after an automated sync")
    text = text.replace(
        '''          notes="Rolling development build — installs via the panel's Dev update channel.

          commit=${COMMIT}
          built=$(date -u +%Y-%m-%dT%H:%M:%SZ)

          Automated per-commit build from main. Not a stable release."''',
        '''          notes="个人自用构建，基于 3X-UI 官网 main 分支编译。

          构建时间（北京时间，UTC+8）=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')

          此版本已移除赞助展示，并提供中文安装交互提示。

          这是滚动开发版，随官网更新，不是正式稳定版。"''',
    )
    text = text.replace(
        "构建时间=$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "构建时间（北京时间，UTC+8）=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')",
    )
    text = text.replace('"Dev build ${short}"', '"开发版 ${short}"')
    text = text.replace('"开发版构建 ${short}"', '"开发版 ${short}"')
    if "Rolling development build — installs via the panel's Dev update channel." in text:
        raise RuntimeError("release.yml still contains the upstream English dev-release notes")
    release.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    remove_sponsor_ui()
    use_fork_dev_release()


if __name__ == "__main__":
    main()
