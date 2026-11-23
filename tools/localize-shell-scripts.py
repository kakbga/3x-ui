#!/usr/bin/env python3
"""Generate Chinese shell scripts from the official 3x-ui scripts.

Only literal user-facing strings are replaced. Commands, control flow,
variables, and program output consumed by the scripts remain unchanged.
"""

from pathlib import Path
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
        "Please enter your server's public IPv4 address: ": "请输入服务器公网 IPv4 地址：",
        "Please enter domain name certificate issued for: ": "请输入证书对应的域名：",
        "Input certificate path (keywords: .crt / fullchain): ": "请输入证书文件路径（通常为 .crt 或 fullchain）：",
        "Input private key path (keywords: .key / privatekey): ": "请输入私钥文件路径（通常为 .key 或 privatekey）：",
        "Panel Installation Complete!": "面板安装完成！",
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
    "update.sh": {},
}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: localize-shell-scripts.py UPSTREAM_DIR OUTPUT_DIR", file=sys.stderr)
        return 2
    source_dir, output_dir = map(Path, sys.argv[1:])
    for name, replacements in TRANSLATIONS.items():
        text = (source_dir / name).read_text(encoding="utf-8")
        for source, localized in replacements.items():
            text = text.replace(source, localized)
        (output_dir / name).write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
