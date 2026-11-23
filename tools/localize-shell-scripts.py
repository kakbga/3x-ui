#!/usr/bin/env python3
"""Generate Chinese shell scripts from the official 3x-ui scripts.

Only literal user-facing strings are replaced. Commands, control flow,
variables, and program output consumed by the scripts remain unchanged.
"""

from pathlib import Path
import re
import sys


TRANSLATIONS = {
    "install.sh": {
        "Fatal error: ${plain} Please run this script with root privilege": "致命错误：${plain} 请使用 root 权限运行此脚本",
        "Failed to check the system OS, please contact the author!": "无法识别操作系统，请联系项目维护者！",
        "The OS release is: $release": "操作系统：$release",
        "Unsupported CPU architecture! ": "不支持的 CPU 架构！",
        "Arch: $(arch)": "CPU 架构：$(arch)",
        "Would you like to customize the Panel Port settings? (If not, a random port will be applied) [y/N]: ": "是否自定义面板端口？（否则将随机分配端口）[y/N]： ",
        "Please set up the panel port: ": "请设置面板端口：",
        "Enter another port for acme.sh standalone listener (leave empty to abort): ": "请输入 acme.sh 独立验证所用端口（留空则取消）：",
        "Please enter your domain name: ": "请输入域名：",
        "Would you like to modify --reloadcmd for ACME? (y/n): ": "是否修改 ACME 的 --reloadcmd？(y/n)：",
        "Choose an option: ": "请选择：",
        "Please enter your custom reloadcmd: ": "请输入自定义 reloadcmd：",
        "Would you like to set this certificate for the panel? (y/n): ": "是否将此证书用于面板？(y/n)：",
        "Choose SSL certificate setup method:": "请选择 SSL 证书配置方式：",
        "Let's Encrypt for Domain (90-day validity, auto-renews)": "Let's Encrypt 域名证书（有效期 90 天，自动续期）",
        "Let's Encrypt for IP Address (6-day validity, auto-renews)": "Let's Encrypt IP 证书（有效期 6 天，自动续期）",
        "Custom SSL Certificate (Path to existing files)": "自定义 SSL 证书（使用现有证书文件路径）",
        "Skip SSL (advanced — behind reverse proxy / SSH tunnel only)": "跳过 SSL（高级选项，仅适用于反向代理或 SSH 隧道）",
        "Options 1 & 2 require port 80 open. Option 3 requires manual paths.": "选项 1 和 2 需要开放 80 端口。选项 3 需要手动填写证书路径。",
        "Option 4 serves the panel over plain HTTP — only safe behind nginx/Caddy or an SSH tunnel.": "选项 4 将通过 HTTP 明文提供面板，仅建议在 nginx/Caddy 反向代理或 SSH 隧道后使用。",
        "Choose an option (default 2 for IP): ": "请选择 [默认 2：IP 证书]：",
        "Unknown XUI_SSL_MODE='${XUI_SSL_MODE}', defaulting to none (HTTP).": "未知的 XUI_SSL_MODE='${XUI_SSL_MODE}'，将默认跳过 SSL（HTTP）。",
        "SSL is strongly recommended. Skip only if a reverse proxy": "强烈建议启用 SSL。只有在反向代理",
        "or SSH tunnel handles TLS for you.": "或 SSH 隧道已为你处理 TLS 时才跳过。",
        "Let's Encrypt now supports both domains and IP addresses!": "Let's Encrypt 现在同时支持域名和 IP 地址证书！",
        "Setting up Let's Encrypt IP certificate (shortlived profile)...": "正在配置 Let's Encrypt 短期 IP 证书…",
        "Note: IP certificates are valid for ~6 days and will auto-renew.": "提示：IP 证书有效期约 6 天，并会自动续期。",
        "Default listener is port 80. If you choose another port, ensure external port 80 forwards to it.": "默认监听端口为 80。若选择其他端口，请将外部 80 端口转发到该端口。",
        "Failed to install acme.sh": "安装 acme.sh 失败",
        "IPv4 address is required": "必须提供 IPv4 地址",
        "Invalid IPv4 address: $ipv4": "IPv4 地址无效：$ipv4",
        "Including IPv6 address: ${ipv6}": "同时使用 IPv6 地址：${ipv6}",
        "Port to use for ACME HTTP-01 listener (default 80): ": "ACME HTTP-01 验证监听端口（默认 80）：",
        "Invalid port provided. Falling back to 80.": "端口无效，将使用默认端口 80。",
        "Using port ${WebPort} for standalone validation.": "独立验证将使用端口 ${WebPort}。",
        "Reminder: Let's Encrypt still connects on port 80; forward external port 80 to ${WebPort}.": "提醒：Let's Encrypt 仍通过外部 80 端口连接，请将其转发到 ${WebPort}。",
        "Port ${WebPort} is in use.": "端口 ${WebPort} 已被占用。",
        "Port ${WebPort} is busy; cannot proceed in non-interactive mode.": "端口 ${WebPort} 正忙，无法在非交互模式下继续。",
        "Port ${WebPort} is busy; cannot proceed.": "端口 ${WebPort} 正忙，无法继续。",
        "Invalid port provided.": "提供的端口无效。",
        "Port ${WebPort} is free and ready for standalone validation.": "端口 ${WebPort} 空闲，可用于独立验证。",
        "Issuing IP certificate for ${ipv4}...": "正在为 ${ipv4} 申请 IP 证书…",
        "Failed to issue IP certificate": "IP 证书申请失败",
        "Please ensure port ${WebPort} is reachable (or forwarded from external port 80)": "请确认端口 ${WebPort} 可从外部访问（或已从外部 80 端口转发）",
        "Certificate issued successfully, installing...": "证书申请成功，正在安装…",
        "Certificate files not found after installation": "安装后未找到证书文件",
        "Certificate files installed successfully": "证书文件安装成功",
        "Setting certificate paths for the panel...": "正在为面板设置证书路径…",
        "Warning: Could not set certificate paths automatically": "警告：无法自动设置证书路径",
        "Certificate files are at:": "证书文件位置：",
        "  Cert: ${certDir}/fullchain.pem": "  证书：${certDir}/fullchain.pem",
        "  Key:  ${certDir}/privkey.pem": "  私钥：${certDir}/privkey.pem",
        "Certificate paths configured successfully": "证书路径配置成功",
        "IP certificate installed and configured successfully!": "IP 证书已成功安装并配置！",
        "Certificate valid for ~6 days, auto-renews via acme.sh cron job.": "证书有效期约 6 天，由 acme.sh 定时任务自动续期。",
        "acme.sh will automatically renew and reload x-ui before expiry.": "acme.sh 会在证书到期前自动续期并重启 x-ui。",
        "Existing certificate found for ${domain}, will reuse it.": "已找到 ${domain} 的现有证书，将继续使用。",
        "Found incomplete acme.sh state for ${domain} (no valid certificate files); cleaning it up and re-issuing.": "发现 ${domain} 的 acme.sh 证书记录不完整（缺少有效证书文件），正在清理并重新申请。",
        "Your domain is ready for issuing certificates now...": "域名已就绪，可以开始申请证书…",
        "Please choose which port to use (default is 80): ": "请选择验证端口（默认 80）：",
        "Your input ${WebPort} is invalid, will use default port 80.": "端口 ${WebPort} 无效，将使用默认端口 80。",
        "Will use port: ${WebPort} to issue certificates. Please make sure this port is open.": "将使用端口 ${WebPort} 申请证书，请确认该端口已开放。",
        "Stopping panel temporarily...": "正在暂时停止面板…",
        "Issuing certificate failed, please check logs.": "证书申请失败，请检查日志。",
        "Issuing certificate succeeded, installing certificates...": "证书申请成功，正在安装…",
        "Using existing certificate, installing certificates...": "正在使用现有证书并安装…",
        "Default --reloadcmd for ACME is: ": "ACME 默认续期命令为：",
        "This command will run on every certificate issue and renew.": "每次申请或续期证书时都会执行此命令。",
        "\n${green}\t1.${plain} Preset: systemctl reload nginx ; systemctl restart x-ui": "\n${green}\t1.${plain} 预设：systemctl reload nginx ; systemctl restart x-ui",
        "${green}\t2.${plain} Input your own command": "${green}\t2.${plain} 输入自定义命令",
        "${green}\t0.${plain} Keep default reloadcmd": "${green}\t0.${plain} 保持默认续期命令",
        "Reloadcmd is: systemctl reload nginx ; systemctl restart x-ui": "续期命令：systemctl reload nginx ; systemctl restart x-ui",
        "It's recommended to put x-ui restart at the end": "建议将重启 x-ui 的命令放在最后",
        "Reloadcmd is: ${reloadCmd}": "续期命令：${reloadCmd}",
        "Keeping default reloadcmd": "保持默认续期命令",
        "Installing certificate succeeded, enabling auto renew...": "证书安装成功，正在启用自动续期…",
        "Installing certificate failed, exiting.": "证书安装失败，正在退出。",
        "Auto renew setup had issues, certificate details:": "自动续期配置遇到问题，证书详情：",
        "Auto renew succeeded, certificate details:": "自动续期配置成功，证书详情：",
        "Certificate paths set for the panel": "面板证书路径已设置",
        "Certificate File: $webCertFile": "证书文件：$webCertFile",
        "Private Key File: $webKeyFile": "私钥文件：$webKeyFile",
        "Access URL: https://${domain}:${existing_port}/${existing_webBasePath}": "访问地址：https://${domain}:${existing_port}/${existing_webBasePath}",
        "Panel will restart to apply SSL certificate...": "面板将重启以应用 SSL 证书…",
        "Error: Certificate or private key file not found for domain: $domain.": "错误：未找到域名 $domain 对应的证书或私钥文件。",
        "Skipping panel path setting.": "跳过面板证书路径设置。",
        "Using Let's Encrypt for domain certificate...": "正在使用 Let's Encrypt 申请域名证书…",
        "✓ SSL certificate configured successfully with domain: ${cert_domain}": "✓ 已成功配置域名 ${cert_domain} 的 SSL 证书",
        "SSL setup may have completed, but domain extraction failed": "SSL 证书可能已配置完成，但无法识别域名",
        "SSL certificate setup failed for domain mode.": "域名证书配置失败。",
        "Using Let's Encrypt for IP certificate (shortlived profile)...": "正在使用 Let's Encrypt 配置短期 IP 证书…",
        "Is ${server_ip} the correct incoming public IPv4 address for this server? [Default y]: ": "检测到公网 IPv4 地址为 ${server_ip}，确认这是此服务器的正确入站地址吗？[默认 y]：",
        "Invalid IPv4 address. Please try again.": "IPv4 地址无效，请重试。",
        "Do you have an IPv6 address to include? (leave empty to skip): ": "是否有需要一并使用的 IPv6 地址？（留空则跳过）：",
        "✓ Let's Encrypt IP certificate configured successfully": "✓ Let's Encrypt IP 证书配置成功",
        "✗ IP certificate setup failed. Please check port 80 is open.": "✗ IP 证书配置失败，请确认 80 端口已开放。",
        "Using custom existing certificate...": "正在使用已有的自定义证书…",
        "Error: File does not exist! Try again.": "错误：文件不存在，请重试。",
        "Error: File exists but is not readable (check permissions)!": "错误：文件存在但不可读，请检查权限。",
        "Error: File is empty!": "错误：文件为空。",
        "✓ Custom certificate paths applied.": "✓ 自定义证书路径已应用。",
        "Note: You are responsible for renewing these files externally.": "提示：这些证书文件需要由你在外部自行续期。",
        "⚠ Panel will be installed WITHOUT SSL/TLS.": "⚠ 面板将不启用 SSL/TLS。",
        "Login credentials and cookies will travel as plain HTTP.": "登录凭据和 Cookie 将通过未加密的 HTTP 传输。",
        "Only safe when:": "仅在以下情况下安全：",
        "  • A reverse proxy (nginx, Caddy, Traefik) terminates TLS for you, or": "  • 由反向代理（nginx、Caddy、Traefik）负责 TLS 加密；或",
        "  • You access the panel exclusively via SSH tunnel": "  • 仅通过 SSH 隧道访问面板",
        "Bind the panel to 127.0.0.1 only? (recommended — forces SSH tunnel / reverse-proxy access) [y/N]: ": "是否仅将面板绑定到 127.0.0.1？（推荐，可强制通过 SSH 隧道或反向代理访问）[y/N]：",
        "✓ Panel bound to 127.0.0.1 only. It is now unreachable from the public internet.": "✓ 面板现仅绑定到 127.0.0.1，无法从公网直接访问。",
        "SSH Port Forwarding — open the panel from your local machine via:": "SSH 端口转发：在本地电脑运行以下命令访问面板：",
        "Alternative: point a reverse proxy (nginx/Caddy) at 127.0.0.1:${panel_port} and let it terminate TLS.": "也可以将反向代理（nginx/Caddy）指向 127.0.0.1:${panel_port}，由代理处理 TLS 加密。",
        "Panel will listen on all interfaces over plain HTTP. Make sure something else is terminating TLS in front of it.": "面板将通过未加密的 HTTP 监听所有网络接口，请确保前置服务负责 TLS 加密。",
        "✓ SSL setup skipped.": "✓ 已跳过 SSL 配置。",
        "Invalid option. Skipping SSL setup.": "选项无效，跳过 SSL 配置。",
        "⚠ SSL Certificate: Enabled and configured": "⚠ SSL 证书：已启用并配置",
        "⚠ SSL Certificate: Skipped — panel is HTTP-only. Use a reverse proxy or SSH tunnel.": "⚠ SSL 证书：已跳过，面板仅使用 HTTP。请通过反向代理或 SSH 隧道访问。",
        "SSL certificate already configured. No action needed.": "SSL 证书已配置，无需操作。",
        "Please enter your server's public IPv4 address: ": "请输入服务器公网 IPv4 地址：",
        "Please enter domain name certificate issued for: ": "请输入证书对应的域名：",
        "Input certificate path (keywords: .crt / fullchain): ": "请输入证书文件路径（通常为 .crt 或 fullchain）：",
        "Input private key path (keywords: .key / privatekey): ": "请输入私钥文件路径（通常为 .key 或 privatekey）：",
        "Panel Installation Complete!": "面板安装完成！",
        "Got x-ui latest version: ${tag_version}, beginning the installation...": "获取到 x-ui 版本：${tag_version}，正在开始安装…",
        "Installing the rolling dev build (tag: dev-latest). This is a per-commit pre-release, not a stable version.": "正在安装本仓库滚动开发版（dev-latest）；该版本随官网更新，不是稳定版。",
        "IMPORTANT: Save these credentials securely!": "重要：请妥善保存以上登录凭据！",
        "Database Selection": "数据库选择",
        "default — recommended for < 500 clients": "默认，建议少于 500 个客户端时使用",
        "recommended for high client counts / many nodes": "客户端较多或节点较多时推荐",
        "SSL Certificate Setup (RECOMMENDED)": "SSL 证书配置（推荐）",
        "Standard SSH command:": "标准 SSH 命令：",
        "If using an SSH key:": "如果使用 SSH 密钥：",
        "Then open in your browser:": "然后在浏览器中打开：",
        "https://raw.githubusercontent.com/MHSanaei/3x-ui/${script_ref}/x-ui.sh": "https://raw.githubusercontent.com/kakbga/3x-ui/main/x-ui.sh",
    },
    "x-ui.sh": {
        "Panel state: ${green}Running${plain}": "面板状态：${green}运行中${plain}",
        "Panel state: ${yellow}Not Running${plain}": "面板状态：${yellow}未运行${plain}",
        "Panel state: ${red}Not Installed${plain}": "面板状态：${red}未安装${plain}",
        "Start automatically: ${green}Managed by Docker${plain}": "开机自启：${green}由 Docker 管理${plain}",
        "Start automatically: ${green}Yes${plain}": "开机自启：${green}是${plain}",
        "Start automatically: ${red}No${plain}": "开机自启：${red}否${plain}",
        "xray state: ${green}Running${plain}": "Xray 状态：${green}运行中${plain}",
        "xray state: ${red}Not Running${plain}": "Xray 状态：${red}未运行${plain}",
        "mtproto inbound ${id} (${bind}): ${green}Running${plain}": "MTProto 入站 ${id} (${bind})：${green}运行中${plain}",
        "mtproto inbound ${id} (${bind}): ${red}Not Running${plain}": "MTProto 入站 ${id} (${bind})：${red}未运行${plain}",
        "Restart the panel, Attention: Restarting the panel will also restart xray": "确认重启面板？注意：重启面板也会同时重启 Xray",
        "Press enter to return to the main menu: ": "按回车键返回主菜单： ",
        "Cancelled": "已取消",
        "Uninstalled Successfully.": "卸载成功。",
        "3X-UI Panel Management Script": "3X-UI 面板管理脚本",
        "Install                                   │": "安装                                    │",
        "Update                                    │": "更新                                    │",
        "Update to Dev Channel (latest commit)": "更新到开发版（最新提交）",
        "Update Menu": "更新菜单",
        "Legacy Version": "旧版本",
        "Uninstall                                 │": "卸载                                    │",
        "Reset Username & Password": "重置用户名和密码",
        "Reset Web Base Path": "重置面板访问路径",
        "Reset Settings": "重置设置",
        "Change Port": "修改端口",
        "View Current Settings": "查看当前设置",
        "Logs Management": "日志管理",
        "SSL Certificate Management": "SSL 证书管理",
        "IP Limit Management": "IP 限制管理",
        "Firewall Management": "防火墙管理",
        "SSH Port Forwarding Management": "SSH 端口转发管理",
        "PostgreSQL Management": "PostgreSQL 管理",
        "Please enter your selection [0-28]: ": "请输入选项 [0-28]：",
        "Install Fail2ban and configure IP Limit": "安装 Fail2ban 并配置 IP 限制",
        "Change Ban Duration": "修改封禁时长",
        "Unban Everyone": "解除所有封禁",
        "Ban Logs": "封禁日志",
        "Ban an IP Address": "封禁 IP 地址",
        "Unban an IP Address": "解除 IP 封禁",
        "Real-Time Logs": "实时日志",
        "Service Status": "服务状态",
        "Service Restart": "重启服务",
        "Back to Main Menu": "返回主菜单",
        "Choose an option: ": "请选择：",
        "Set listen IP": "设置监听 IP",
        "Clear listen IP": "清除监听 IP",
        "Current SSH Port Forwarding Configuration:": "当前 SSH 端口转发配置：",
        "If using SSH key:": "如果使用 SSH 密钥：",
        "https://raw.githubusercontent.com/MHSanaei/3x-ui/main/install.sh": "https://raw.githubusercontent.com/kakbga/3x-ui/main/install.sh",
        "https://raw.githubusercontent.com/mhsanaei/3x-ui/v$tag_version/install.sh": "https://raw.githubusercontent.com/kakbga/3x-ui/main/install.sh",
        "https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh": "https://raw.githubusercontent.com/kakbga/3x-ui/main/install.sh",
    },
    "update.sh": {
        "Using update tag: ${tag_version}": "更新目标版本：${tag_version}",
        "Got x-ui latest version: ${tag_version}, beginning the installation...": "获取到 x-ui 版本：${tag_version}，正在开始安装…",
    },
}


MENU_LABELS = {
    "Exit Script": "退出脚本",
    "Start": "启动",
    "Stop": "停止",
    "Restart": "重启",
    "Restart Xray": "重启 Xray",
    "Check Status": "查看运行状态",
    "Enable Autostart": "启用开机自启",
    "Disable Autostart": "禁用开机自启",
    "Cloudflare SSL Certificate": "Cloudflare SSL 证书",
    "Enable BBR": "启用 BBR",
    "Update Geo Files": "更新 Geo 数据文件",
    "Speedtest by Ookla": "Ookla 网络测速",
}


def localize_xui_menu(text: str) -> str:
    """Translate upstream menu labels and avoid fixed-width box alignment."""
    function = re.search(r"(?m)^show_menu\(\) \{\s*$", text)
    if not function:
        raise RuntimeError("Could not locate show_menu() in x-ui.sh")
    output = re.search(r'(?m)^    echo -e "\s*$', text[function.end() :])
    if not output:
        raise RuntimeError("Could not locate the menu output in show_menu()")
    output_start = function.end() + output.start()
    status = re.search(r"(?m)^    show_status\s*$", text[output_start + output.end() :])
    if not status:
        raise RuntimeError("Could not locate show_status after the menu output")
    status_start = output_start + output.end() + status.start()
    block = text[output_start : status_start]
    entries = []
    for line in block.splitlines():
        item = re.search(r"\$\{green\}(\d+)\.\$\{plain\}\s*(.*)$", line)
        if not item:
            continue
        number = int(item.group(1))
        label = re.sub(r"[│|]\s*$", "", item.group(2)).strip()
        entries.append((number, MENU_LABELS.get(label, label)))
    if not entries:
        raise RuntimeError("No numbered menu entries found in x-ui.sh")

    lines = ["${green}3X-UI 面板管理脚本${plain}", "════════════════════════════════════"]
    separators_before = {7, 12, 18, 20, 26}
    for number, label in entries:
        if number in separators_before:
            lines.append("────────────────────────────────────")
        lines.append(f"${{green}}{number}.${{plain}} {label}")
    lines.append("════════════════════════════════════")
    menu = '    echo -e "\n' + "\n".join(lines) + '\n"\n'
    return text[:output_start] + menu + text[status_start:]


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: localize-shell-scripts.py UPSTREAM_DIR OUTPUT_DIR", file=sys.stderr)
        return 2
    source_dir, output_dir = map(Path, sys.argv[1:])
    for name, replacements in TRANSLATIONS.items():
        text = (source_dir / name).read_text(encoding="utf-8")
        for source, localized in replacements.items():
            text = text.replace(source, localized)
        if name == "x-ui.sh":
            text = localize_xui_menu(text)
        (output_dir / name).write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
