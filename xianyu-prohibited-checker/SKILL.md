---
name: xianyu-prohibited-checker
description: Detect Xianyu/闲鱼 prohibited-word and publishing-rule risk in product names, titles, descriptions, or listing copy. Use when the user sends a product name and asks whether it can be posted on Xianyu, whether it has 闲鱼违禁词/违规词/版权词/盗版风险, or wants safer wording before publishing.
---

# 闲鱼违禁词检测

## Workflow

1. Take the user's product name, title, or listing copy as the detection input.
2. Run the bundled checker first:

```bash
python scripts/check_xianyu_terms.py "用户给出的商品名或描述" --json
```

3. Use the script result as the deterministic keyword scan. It reads `references/prohibited_terms.tsv`, which is the cleaned and deduplicated library.
4. Apply the official-rule summary in `references/official_rules_summary.md` for category-level judgment. Read the full OCR text in `references/official_rules_2025-12.txt` only when the user asks for source detail or the case is ambiguous.
5. Respond in Chinese with a concise risk decision, matched terms, reason, and safer rewrite suggestions.

## Risk Decisions

- `高风险`: Strong keyword hit from `商品违禁词` or `平台盗版违规词`, or the title clearly falls under an official prohibited category such as weapons, drugs, pornography, illegal services, privacy data, piracy, counterfeit goods, telecom-fraud tools, gambling, VPN/翻墙, fake certificates, or medical/food categories that the rules do not support.
- Treat `AI托管`, `AI全自动批量剪辑软件`, `自动化批量涨粉/刷量/拉新/推广`, and similar托管式 traffic or popularity tooling as `高风险`, even when the cleaned keyword library has no exact hit. Do not treat standalone words like `批量`, `剪辑/视频`, or `软件/工具` as risk by themselves. This follows a real Xianyu penalty example under `不当获取流量或人气`.
- Treat `大厂内推`, `内推服务`, `保面试/保 offer`, and `大模型/AI 面试题全集` style listings as `高风险` when the商品要素 suggest internal referral or interview-pass services. Do not treat `秒发`, `虚拟资料`, `合集`, or `全集` as prohibited by themselves; Xianyu may allow virtual materials unless they hit a specific risk category such as piracy, copyright infringement, illegal service, or 大厂内推.
- Treat `代做`, `代写`, `代画`, `替写`, `替画`, `代考`, `包完成`, especially with `作业`, `论文`, `毕设`, `课程设计`, `项目`, `代码`, `程序`, `CAD`, `图纸`, `展板`, or `环艺`, as `高风险`. Do not treat ordinary `作业辅导`, `编程辅导`, `代码讲解`, `CAD`, or `设计` as prohibited without substitute-completion context. This follows real Xianyu penalty examples under `代写作业违禁风险`.
- Treat `论文修改`, `论文润色`, `论文指导`, `论文辅助`, `论文代写`, and writing-service listings clearly tied to academic fraud or school tasks as `高风险`, including when the signal appears in listing images or chat screenshots. Do not treat standalone `宣传稿`, `演讲稿`, `读后感`, `可加急`, `原创定制`, or `交接文档` as prohibited words.
- Treat web-course materials, audio/video/e-book resources, study-guide or question-bank resources, internal-material publications, and `全集/合集/资源/网盘/秒发/PDF/电子版/扫描版` combinations as high risk when they imply resale or distribution of copyrighted materials.
- Treat advertising-style listings such as recruitment,代理,网赚,招商加盟,招代理, and similar lead-generation content as high risk.
- Treat competition-service listings as high risk when `创青春`, `大创赛`, `大创`, `挑战杯`, `互联网+`, `竞赛/比赛/国赛/省赛` appear with `比赛用`, `参赛`, `辅导/指导`, `PPT模板/源文件`, `获奖`, `加绩点`, `包拿奖`, `证书/奖状`, or similar claims. Do not treat ordinary `PPT模板` or `可编辑源文件` as prohibited without the competition-service context.
- `需人工复核`: Only copyright terms are hit, only weak short-code terms are hit, the listing contains a person name, brand name, company name, or institution name, or the product belongs to a category that official rules allow only with qualifications or strict posting requirements, such as books/publications, food, event tickets, used cars, or whole motorcycles.
- `未命中明显风险`: No keyword or official-rule category risk is found. Still remind that final enforcement depends on platform review when useful.

## Output Format

Use this shape unless the user asks for another format:

```text
结论：高风险 / 需人工复核 / 未命中明显风险

命中：
- 词条：...（来源：商品违禁词/商品版权词/平台盗版违规词；强匹配/弱匹配）
- 官方规则：...

原因：...

建议改法：
- ...
```

Keep weak matches proportional. Single-character or very short tokens such as `V` may be contact-code hints, but can also be false positives in normal brand/model names. Treat them as review signals unless the surrounding text supports off-platform contact or引流.

## Rewrite Guidance

- Remove explicit prohibited terms instead of masking them with homophones when the underlying product or service is prohibited.
- For copyright/IP/course/book/software hits, avoid `盗版`, `破解版`, `永久激活`, `全集`, `电子书`, `PDF`, `网盘`, `资源`, `源码`, `会员破解`, and similar resource-sharing language.
- For names and organizations, flag person names, brand names, company names, and institution names as intellectual-property review risk. Avoid implying authorization, official affiliation, ownership of someone else's course/IP, or resale of named-person/brand/institution materials unless the listing can prove legitimate rights.
- For education/book/media listings, avoid `必刷题`, `教辅`, `题库`, `网课资料`, `音频/视频资源`, `电子书资源`, `全集`, `合集`, `内部资料`, `内部讲义`, `电子版`, `扫描版`, and similar redistribution signals unless the user has legitimate rights and clear proof.
- For advertising-risk listings, avoid `招聘`, `代理`, `网赚`, `招商加盟`, `招代理`, and similar wording.
- For competition-related listings, avoid `创青春`, `大创赛`, `挑战杯`, `互联网+`, `比赛用`, `竞赛辅导`, `加绩点`, `包拿奖`, `获奖证书`, `国赛金奖`, and certificate/award-display claims unless the listing is clearly legitimate and not promising competition outcomes.
- For AI/video tools, avoid `AI托管`, `AI全自动`, `无人值守`, `涨粉`, `刷量`, `代拉新`, `推广`, `顶帖`, and similar托管式 traffic-growth or automation claims. Do not over-penalize ordinary `批量剪辑`, `视频剪辑`, `软件`, or `工具` wording without the托管/刷量 context.
- For job/interview materials, avoid `大厂内推`, `保面试`, `包 offer`, `面试题全集`, `面试通关`, `内推名额`, and similar terms that imply referral, recruitment, or guaranteed interview outcomes. Safer wording should describe ordinary study notes only, without promising interview access or big-company referral value.
- For academic/programming/design/writing services, avoid `代做`, `代写`, `代画`, `替写`, `替画`, `代考`, `包完成`, `项目代做`, `代码代写`, `展板代画`, `图纸代画`, `论文修改`, `论文润色`, `论文指导`, and similar academic substitute-completion claims. Ordinary commercial writing terms need academic/学业/论文 context before treating them as prohibited.
- For legitimate second-hand physical goods, steer wording toward the concrete item, condition, quantity, purchase channel, and proof of authenticity.
- Do not tell the user a listing is definitely safe; say the scan did not find obvious risk.

## Resources

- `scripts/check_xianyu_terms.py`: deterministic keyword and official-pattern scanner.
- `references/prohibited_terms.tsv`: cleaned combined term library; one row per normalized term with source categories.
- `references/official_rules_summary.md`: concise official-rule categories for manual judgment.
- `references/official_rules_2025-12.txt`: OCR text converted from the official-rule image.
