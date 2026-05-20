from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TERMS = ROOT / "references" / "prohibited_terms.tsv"

CATEGORY_RISK = {
    "商品违禁词": "high",
    "平台盗版违规词": "high",
    "商品版权词": "review",
}

RISK_ORDER = {"pass": 0, "review": 1, "high": 2}
RISK_LABEL = {
    "pass": "未命中明显风险",
    "review": "需人工复核",
    "high": "高风险",
}

WEAK_NORMALIZED_TERMS = {"v", "pm", "tk"}
CONTEXT_REQUIRED_TERMS = {
    "cad": [
        "代画",
        "替画",
        "包画",
        "代做",
        "代写",
        "替写",
        "包完成",
        "代完成",
        "破解",
        "破解版",
        "永久激活",
        "盗版",
    ],
}

COMMON_SURNAMES = set(
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜谢邹喻柏章苏潘范彭郎鲁韦马苗方俞任袁柳史唐费薛雷贺倪汤罗毕郝安常于傅齐康伍余顾孟黄穆萧尹姚邵汪祁毛米贝明臧计成戴宋庞熊纪舒屈项祝董梁杜阮蓝闵季麻贾路江童颜郭梅盛林钟徐邱骆高夏蔡田胡凌霍万卢莫房解丁宣邓洪包左石崔龚程邢裴陆翁牛温庄柴瞿阎慕连向古易廖辛曾关游权"
)
COMPOUND_SURNAMES = {
    "欧阳",
    "司马",
    "上官",
    "诸葛",
    "东方",
    "皇甫",
    "尉迟",
    "公孙",
    "令狐",
    "宇文",
    "长孙",
    "慕容",
    "司徒",
    "司空",
    "端木",
    "南宫",
}

POLICY_RULES = [
    (
        "人名、品牌名、公司名、机构名存在知识产权或不当使用他人权利复核风险",
        "review",
        [
            "官方",
            "旗舰",
            "品牌授权",
            "有限公司",
            "股份有限公司",
            "集团",
            "公司",
            "大学",
            "学院",
            "学校",
            "出版社",
            "研究院",
            "协会",
            "机构",
            "工作室",
        ],
    ),
    (
        "大厂内推或求职招聘类违禁风险",
        "high",
        ["大厂内推", "内推名额", "内推服务", "付费内推", "保面试", "包面试", "保offer", "包offer"],
    ),
    (
        "AI托管或自动化批量内容工具涉嫌不当获取流量或人气",
        "high",
        ["AI托管", "代刷粉丝", "代刷听众人数", "代刷排行", "代刷流量", "代拉新推广", "顶帖删帖", "代网络投票"],
    ),
    (
        "枪支弹药、危险武器、军警及行政机关用品",
        "high",
        ["枪支", "子弹", "军火", "管制刀具", "弩", "飞镖", "仿真枪", "警服", "警徽", "军警"],
    ),
    (
        "易燃易爆、危险化学品、毒品",
        "high",
        ["炸药", "火药", "毒品", "制毒", "吸毒", "烟花爆竹", "危险化学品", "放射性"],
    ),
    (
        "政治有害、危害国家安全或社会稳定",
        "high",
        ["反动", "邪教", "分裂国家", "国家机密", "政治密押"],
    ),
    (
        "色情低俗、催情用品",
        "high",
        ["色情", "淫秽", "低俗", "原味", "催情", "裸照", "私照", "成人资源"],
    ),
    (
        "人身隐私、安全或恶意攻击",
        "high",
        ["身份证", "个人隐私", "隐私数据", "监听", "窃听", "窃取", "账号密码", "群发软件"],
    ),
    (
        "药品、医疗器械、保健食品、奶粉、食品添加剂",
        "high",
        ["处方药", "药品", "医疗器械", "美容针", "农药", "兽药", "保健食品", "奶粉", "食品添加剂"],
    ),
    (
        "非法服务、票证、作弊或违反公序良俗",
        "high",
        ["假证", "假章", "假发票", "代考", "代写论文", "代体检", "代投票", "赌博", "翻墙", "vpn", "算命"],
    ),
    (
        "代写作业或学业任务代做违禁风险",
        "high",
        [
            "代写作业",
            "作业代做",
            "项目代做",
            "代码代写",
            "代写代码",
            "代做毕设",
            "毕业设计代做",
            "课程设计代做",
            "代画设计",
            "展板代画",
            "图纸代画",
            "cad代画",
            "代画cad",
        ],
    ),
    (
        "论文辅助、代写实习报告或写作代办违禁风险",
        "high",
        [
            "代写论文",
            "论文代写",
            "论文辅助",
            "论文修改",
            "论文润色",
            "论文指导",
            "科研论文",
            "学术论文",
        ],
    ),
    (
        "动植物、人体器官及捕杀工具",
        "high",
        ["人体器官", "卵子", "精子", "保护动物", "捕杀工具", "鱼翅", "熊胆"],
    ),
    (
        "非法所得、外挂、作弊造假工具",
        "high",
        ["外挂", "私服", "虚假定位", "指纹膜", "电子秤作弊", "信号屏蔽", "手机卡复制器"],
    ),
    (
        "电信网络诈骗用途设备、软件及服务",
        "high",
        ["猫池", "接码", "打码平台", "改号软件", "伪基站", "voip", "google voice", "短信验证"],
    ),
    (
        "假冒、盗版或不当使用他人权利",
        "high",
        [
            "盗版",
            "高仿",
            "复刻",
            "破解版",
            "永久激活",
            "侵权",
            "未授权",
            "源码",
            "盗版网课资料",
            "电子书资源",
            "网课资料",
        ],
    ),
    (
        "内部资料性出版物高风险",
        "high",
        ["内部资料性出版物", "内部资料出版物", "内部出版物", "内部资料", "内部教材", "内部讲义", "狗狗博客"],
    ),
    (
        "广告类信息风险",
        "high",
        ["招聘信息", "代理信息", "网赚信息", "招聘代理", "代理加盟", "招商加盟", "招代理", "网赚", "拉代理"],
    ),
    (
        "竞赛服务不当宣传违禁风险",
        "high",
        ["加绩点", "包拿奖", "保拿奖", "包获奖", "保获奖", "代拿奖", "代参赛", "竞赛代做", "竞赛代写"],
    ),
    (
        "未经允许或不适合交易的商品或信息",
        "high",
        ["假币", "手机卡", "上网卡", "文物", "烟草", "非法账号", "游戏点卡", "充值平台"],
    ),
    (
        "出版物类商品需按平台要求发布",
        "review",
        ["图书", "教材", "电子书", "pdf", "期刊", "音像制品", "地图", "isbn"],
    ),
    (
        "食品、演出票、二手车、摩托车等需满足资质或数量规则",
        "review",
        ["食品", "零食", "演唱会票", "演出票", "门票", "二手车", "摩托车整车"],
    ),
]

COMBO_POLICY_RULES = [
    {
        "rule": "大模型/AI 面试题合集可能被归入大厂内推违禁风险",
        "risk": "high",
        "groups": [
            ["大模型", "llm", "ai", "人工智能"],
            ["面试题", "面经", "面试资料", "面试合集", "面试全集"],
        ],
    },
    {
        "rule": "大厂面试/求职资料可能被归入大厂内推违禁风险",
        "risk": "high",
        "groups": [
            ["大厂", "互联网大厂", "名企", "校招", "社招"],
            ["面试题", "面经", "内推", "求职", "简历优化", "offer"],
        ],
    },
    {
        "rule": "网课/音视频/电子书资源可能被归入假冒或盗版商品风险",
        "risk": "high",
        "groups": [
            ["网课", "课程", "教材", "教辅", "题库", "刷题", "必刷题", "讲义", "电子书"],
            ["资源", "全集", "合集", "pdf", "电子版", "扫描版", "音频", "视频", "网盘", "秒发"],
        ],
    },
    {
        "rule": "中小学教辅/教材资料资源可能被归入盗版出版物风险",
        "risk": "high",
        "groups": [
            ["高中", "初中", "小学", "数学", "英语", "语文", "物理", "化学", "生物", "人教", "人教版", "人教b版"],
            ["必刷题", "教辅", "题库", "试卷", "电子版", "pdf", "扫描版", "资源"],
        ],
    },
    {
        "rule": "内部资料性出版物风险",
        "risk": "high",
        "groups": [
            ["内部", "内部资料", "内部版", "内部讲义", "内部教材"],
            ["出版物", "资料", "教材", "讲义", "电子书", "合集", "全集"],
        ],
    },
    {
        "rule": "为完成学业任务提供代做/代写/代画服务",
        "risk": "high",
        "groups": [
            [
                "作业",
                "论文",
                "毕设",
                "毕业设计",
                "课程设计",
                "课设",
                "项目",
                "代码",
                "程序",
                "cad",
                "图纸",
                "展板",
                "环艺",
                "效果图",
                "施工图",
                "平面图",
            ],
            ["代做", "代写", "替写", "包写", "代画", "替画", "包画", "代完成", "包完成", "代交", "代考试", "代考"],
        ],
    },
    {
        "rule": "论文辅助/修改/润色/指导等服务风险",
        "risk": "high",
        "groups": [
            ["论文", "学术论文", "科研论文", "毕业论文", "本科论文", "硕士论文", "开题报告"],
            ["修改", "润色", "指导", "辅导", "辅助", "降重", "查重", "代写", "帮写", "撰写"],
        ],
    },
    {
        "rule": "学业/学术场景下的写作代办风险",
        "risk": "high",
        "groups": [
            ["论文", "学术", "学业", "科研", "毕业", "课程", "作业", "实习报告"],
            ["代写", "帮写", "撰写", "修改", "润色", "指导", "辅助", "原创定制", "交接文档"],
        ],
    },
    {
        "rule": "各类竞赛服务不当宣传风险",
        "risk": "high",
        "groups": [
            ["创青春", "大创赛", "大创", "挑战杯", "互联网+", "竞赛", "比赛", "国赛", "省赛"],
            ["模板", "ppt", "源文件", "辅导", "指导", "参赛", "比赛用", "获奖", "金奖", "证书", "奖状", "加绩点", "包拿奖"],
        ],
    },
    {
        "rule": "AI托管类自动化内容工具涉嫌不当获取流量或人气",
        "risk": "high",
        "groups": [
            ["ai", "人工智能", "智能"],
            ["ai托管", "全自动", "无人值守", "自动托管", "托管"],
            ["剪辑", "混剪", "短视频", "视频"],
            ["软件", "工具", "系统", "程序", "脚本", "神器"],
        ],
    },
    {
        "rule": "自动化批量涨粉、引流、刷量或内容托管服务",
        "risk": "high",
        "groups": [
            ["批量", "自动", "代", "托管"],
            ["涨粉", "粉丝", "流量", "排行", "拉新", "投票", "点赞", "播放", "互动", "推广"],
        ],
    },
]


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.lower()
    return re.sub(r"\s+", "", value)


def is_weak_term(norm: str) -> bool:
    if norm in WEAK_NORMALIZED_TERMS:
        return True
    if len(norm) <= 1:
        return True
    return False


def has_required_context(normalized_text: str, norm: str) -> bool:
    patterns = CONTEXT_REQUIRED_TERMS.get(norm)
    if not patterns:
        return True
    return any(normalize(pattern) in normalized_text for pattern in patterns)


def weak_ascii_present(text: str, norm: str) -> bool:
    if norm == "v":
        return bool(re.search(r"(?i)(加\s*v|v\s*(信|x|我|:|：)|\bv\b)", text))
    if norm in {"pm", "tk"}:
        return bool(re.search(rf"(?i)(^|[^a-z0-9]){re.escape(norm)}([^a-z0-9]|$)", text))
    if len(norm) == 1 and norm.isascii():
        return bool(re.search(rf"(?i)(^|[^a-z0-9]){re.escape(norm)}([^a-z0-9]|$)", text))
    return True


def load_terms(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        return [row for row in reader if row.get("term") and row.get("normalized")]


def find_keyword_matches(text: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized_text = normalize(text)
    matches: list[dict[str, str]] = []

    for row in rows:
        norm = row["normalized"]
        if not norm or norm not in normalized_text:
            continue
        if not has_required_context(normalized_text, norm):
            continue
        if is_weak_term(norm) and norm.isascii() and not weak_ascii_present(text, norm):
            continue

        categories = row.get("categories", "")
        category_list = [item for item in categories.split("|") if item]
        category_risk = max(
            (CATEGORY_RISK.get(category, "review") for category in category_list),
            key=lambda risk: RISK_ORDER[risk],
            default="review",
        )
        confidence = "weak" if is_weak_term(norm) else "strong"
        risk = "review" if confidence == "weak" and category_risk == "high" else category_risk
        matches.append(
            {
                "term": row["term"],
                "normalized": norm,
                "categories": categories,
                "sources": row.get("sources", ""),
                "confidence": confidence,
                "risk": risk,
            }
        )

    matches.sort(
        key=lambda item: (
            RISK_ORDER[item["risk"]],
            1 if item["confidence"] == "strong" else 0,
            len(item["normalized"]),
        ),
        reverse=True,
    )
    return matches


def find_person_name_ip_hits(text: str) -> list[dict[str, str]]:
    context_words = [
        "课",
        "课程",
        "教程",
        "网课",
        "录播",
        "资料",
        "合集",
        "全集",
        "题库",
        "面试",
        "面经",
        "笔记",
        "讲义",
        "电子书",
        "全程班",
        "系统班",
    ]
    if not any(word in text for word in context_words):
        return []

    candidates = re.findall(
        r"([\u4e00-\u9fff]{2,4})(?=.{0,8}(?:课|课程|教程|网课|录播|资料|合集|全集|题库|面试|面经|笔记|讲义|电子书|全程班|系统班))",
        text,
    )
    names: list[str] = []
    for candidate in candidates:
        if candidate[:2] in COMPOUND_SURNAMES or candidate[0] in COMMON_SURNAMES:
            names.append(candidate)

    if not names:
        return []

    return [
        {
            "rule": "疑似人名与课程/资料/题库等商品要素组合，存在知识产权复核风险",
            "risk": "review",
            "matched_patterns": "、".join(sorted(set(names))[:10]),
        }
    ]


def find_policy_hits(text: str) -> list[dict[str, str]]:
    normalized_text = normalize(text)
    hits: list[dict[str, str]] = []
    for rule, risk, patterns in POLICY_RULES:
        matched = [
            pattern
            for pattern in patterns
            if normalize(pattern) and normalize(pattern) in normalized_text
        ]
        if matched:
            hits.append({"rule": rule, "risk": risk, "matched_patterns": "、".join(matched)})

    for combo in COMBO_POLICY_RULES:
        matched_groups: list[str] = []
        for group in combo["groups"]:
            matched = [pattern for pattern in group if normalize(pattern) in normalized_text]
            if not matched:
                matched_groups = []
                break
            matched_groups.append("/".join(matched))
        if matched_groups:
            hits.append(
                {
                    "rule": combo["rule"],
                    "risk": combo["risk"],
                    "matched_patterns": " + ".join(matched_groups),
                }
            )

    hits.extend(find_person_name_ip_hits(text))

    hits.sort(key=lambda item: RISK_ORDER[item["risk"]], reverse=True)
    return hits


def assess(text: str, terms_path: Path = DEFAULT_TERMS, limit: int = 30) -> dict[str, object]:
    rows = load_terms(terms_path)
    keyword_matches = find_keyword_matches(text, rows)
    policy_hits = find_policy_hits(text)

    risk = "pass"
    for item in keyword_matches:
        if RISK_ORDER[item["risk"]] > RISK_ORDER[risk]:
            risk = item["risk"]
    for item in policy_hits:
        if RISK_ORDER[item["risk"]] > RISK_ORDER[risk]:
            risk = item["risk"]

    return {
        "input": text,
        "risk": risk,
        "risk_label": RISK_LABEL[risk],
        "keyword_match_count": len(keyword_matches),
        "keyword_matches": keyword_matches[:limit],
        "policy_hits": policy_hits[:limit],
        "notes": [
            "单字、极短英文或疑似暗语命中会降为弱匹配，需结合上下文判断。",
            "仅命中版权词时通常判为需复核，重点确认是否盗版、假冒、未授权或侵权。",
            "最终处置以闲鱼平台审核为准。",
        ],
    }


def format_human(result: dict[str, object]) -> str:
    lines = [
        f"输入：{result['input']}",
        f"结论：{result['risk_label']}",
        "",
    ]

    policy_hits = result["policy_hits"]
    if isinstance(policy_hits, list) and policy_hits:
        lines.append("官方规则命中：")
        for hit in policy_hits:
            lines.append(f"- {hit['rule']}：{hit['matched_patterns']}（{RISK_LABEL[hit['risk']]}）")
        lines.append("")

    matches = result["keyword_matches"]
    if isinstance(matches, list) and matches:
        lines.append(f"词库命中：{result['keyword_match_count']} 条")
        for match in matches:
            confidence = "强匹配" if match["confidence"] == "strong" else "弱匹配"
            lines.append(
                f"- {match['term']} [{match['categories']}]（{confidence}，{RISK_LABEL[match['risk']]}）"
            )
        lines.append("")
    else:
        lines.append("词库命中：无")
        lines.append("")

    lines.extend(
        [
            "建议：",
            "- 高风险命中不要直接发布，先删除或替换相关商品名/描述。",
            "- 闲鱼支持部分虚拟资料交易，不要仅因“秒发”“资料”“合集”“全集”直接判违规；需要看是否落到版权、盗版、内推求职、违规服务等具体风险。",
            "- 人名、品牌名、公司名、机构名都存在知识产权或不当使用他人权利复核风险；叠加盗版、假冒、资源包、课程、电子资料等表达时风险更高。",
            "- 网课资料、音频/视频/电子书资源、教辅题库资源、内部资料性出版物、全集合集等表达容易触发盗版或内部资料出版物风险。",
            "- 招聘、代理、网赚、招商加盟等广告类信息也会触发发布风险。",
            "- 竞赛辅导/竞赛资料/比赛用模板等需规范宣传；创青春、大创赛、挑战杯等竞赛场景叠加加绩点、包拿奖、获奖证书、国赛金奖、比赛用等表达会触发高风险。",
            "- 大模型/AI 面试题、面经、大厂面试资料等表达可能被归入“大厂内推违禁风险”。",
            "- 宣传稿、演讲稿、读后感、可加急、原创定制、交接文档等普通写作服务词不要单独判违规；风险锚点是论文、学术研究、学业任务造假，或明确代写/帮写用于学业任务。",
            "- 作业辅导本身不要直接判违规；风险锚点是代做、代写、代画、替写、替画、代考、包完成、论文修改/润色/指导等替用户完成学术或学业任务的服务。",
            "- 单独的“批量”“剪辑/视频”“软件/工具”不应直接判违规；风险锚点是 AI 托管、全自动无人值守、刷量、拉新、涨粉、推广等表达。",
            "- 版权词命中需确认是否正版、授权、实物闲置，避免出现盗版、电子资源、破解版、全集、PDF 等表达。",
            "- 弱匹配只作为提醒，结合商品上下文判断是否属于联系方式、引流或暗语。",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Xianyu product text against prohibited-term references.")
    parser.add_argument("text", nargs="*", help="Product title or description to check. Reads stdin when omitted.")
    parser.add_argument("--terms", type=Path, default=DEFAULT_TERMS, help="Path to prohibited_terms.tsv.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--limit", type=int, default=30, help="Maximum matches to include.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text = " ".join(args.text).strip() if args.text else sys.stdin.read().strip()
    if not text:
        print("请提供要检测的商品名或描述。", file=sys.stderr)
        return 2

    result = assess(text, args.terms, args.limit)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
