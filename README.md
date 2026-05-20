# 闲鱼违禁词检测 Skill

> 给 Codex / ChatGPT 用的闲鱼商品发布风险检测 Skill。  
> 输入商品标题或描述，它会根据违规词库、官方规则和真实处罚样例，判断有没有发布风险。

## 这个项目能做什么

| 能力 | 说明 |
| --- | --- |
| 检测闲鱼标题 | 判断商品名里有没有违禁词、版权词、盗版风险词 |
| 检测商品描述 | 识别代写、代做、网赚、AI 托管、竞赛宣传等风险 |
| 结合真实处罚样例 | 已记录多张闲鱼处罚截图里的规则边界 |
| 给出风险等级 | 输出 `高风险`、`需人工复核`、`未命中明显风险` |
| 给出改写方向 | 告诉你哪些词要删、哪些表达更稳 |

## 不会安装？直接丢给你的 AI

很多人现在都有自己的 Agent / AI 编程助手。你不用自己看懂全部说明，可以直接复制下面这段话给你的 AI：

```text
请帮我部署这个 Codex Skill：

GitHub 地址：https://github.com/0x0xfan/goofish-weiguici-skill

要求：
1. clone 这个仓库；
2. 找到里面的 xianyu-prohibited-checker 文件夹；
3. 把 xianyu-prohibited-checker 复制到我的 Codex skills 目录；
4. 请先判断我的系统：
   - Windows 的 Codex skills 目录通常是 C:\Users\我的用户名\.codex\skills\
   - macOS / Linux 的 Codex skills 目录通常是 ~/.codex/skills/
5. 安装后帮我确认这个文件存在：
   - Windows: C:\Users\我的用户名\.codex\skills\xianyu-prohibited-checker\SKILL.md
   - macOS / Linux: ~/.codex/skills/xianyu-prohibited-checker/SKILL.md
6. 然后用一个标题测试：
   Java编程作业辅导与项目代做
7. 如果能判断为高风险，说明部署成功。

注意：只需要部署 skill，不要改我的其他文件。
```

复制给 AI 时，把 `我的用户名` 换成你电脑上的真实用户名；如果你不知道用户名，也可以让 AI 自动识别。Mac 用户一般不用改 `~/.codex/skills/` 里的 `~`，它会自动指向你的用户目录。

如果你的 AI 能操作终端，也可以让它执行：

```powershell
git clone https://github.com/0x0xfan/goofish-weiguici-skill.git
```

然后复制这个目录：

```text
goofish-weiguici-skill\xianyu-prohibited-checker
```

到：

```text
Windows: C:\Users\你的用户名\.codex\skills\
macOS / Linux: ~/.codex/skills/
```

## 人工安装

1. 下载或克隆本仓库。

```powershell
git clone https://github.com/0x0xfan/goofish-weiguici-skill.git
```

2. 复制这个文件夹：

```text
xianyu-prohibited-checker
```

3. 粘贴到 Codex skills 目录。

常见位置：

```text
Windows: C:\Users\你的用户名\.codex\skills\
macOS / Linux: ~/.codex/skills/
```

安装成功后应该能看到：

```text
Windows: C:\Users\你的用户名\.codex\skills\xianyu-prohibited-checker\SKILL.md
macOS / Linux: ~/.codex/skills/xianyu-prohibited-checker/SKILL.md
```

macOS / Linux 也可以直接用命令复制：

```bash
mkdir -p ~/.codex/skills
cp -R goofish-weiguici-skill/xianyu-prohibited-checker ~/.codex/skills/
```

## 怎么使用

安装后，在 Codex / ChatGPT 里这样问：

```text
用 $xianyu-prohibited-checker 检测：Java编程作业辅导与项目代做
```

也可以直接问：

```text
这个闲鱼标题会违规吗：2026最新AI全自动批量剪辑软件
```

如果 Skill 被正确安装，它会优先调用本项目的检测规则。

## 检测结果怎么看

### 高风险

很可能触发闲鱼违规，不建议直接发布。

常见原因：

- 代写、代做、代画、代考
- 论文修改、论文润色、论文辅助
- 盗版网课、电子书资源、音视频资源
- AI 托管、刷量、涨粉、拉新
- 大厂内推、保面试、保 offer
- 招聘代理、网赚、招商加盟
- 竞赛加绩点、包拿奖、获奖证书

### 需人工复核

有风险信号，但不一定违规，需要结合商品实际情况判断。

常见原因：

- 出现人名、品牌名、公司名、机构名
- 命中版权词
- 出版物、食品、票务等需要资质或规范发布的类目
- 极短词或暗语，可能误判

### 未命中明显风险

当前词库和规则没有发现明显风险。

这不等于一定安全，只表示没有明显命中。最终是否违规，以闲鱼平台审核结果为准。

## 已记录的真实处罚方向

| 风险方向 | 例子 |
| --- | --- |
| AI 托管违禁风险 | `AI全自动批量剪辑软件` |
| 大厂内推违禁风险 | `大模型(LLM)面试题全集` |
| 代写作业违禁风险 | `Java编程作业辅导与项目代做` |
| 论文辅助违禁风险 | `论文润色指导` |
| 假冒 / 盗版商品信息 | `必刷题 高中数学 人教B版` |
| 内部资料性出版物 | `狗狗博客1-3季全集` |
| 广告类信息 | `招聘代理网赚项目` |
| 竞赛服务不当宣传 | `创青春 大创赛 比赛用 PPT模板` |
| 知识产权复核风险 | 人名、品牌名、公司名、机构名 |

## 常见边界

这些词不要单独判违规：

| 不单独违规 | 什么时候会变危险 |
| --- | --- |
| `PPT模板` | 叠加 `创青春`、`大创赛`、`比赛用`、`包拿奖` |
| `可编辑源文件` | 叠加竞赛获奖、证书奖状、加绩点 |
| `宣传稿`、`演讲稿`、`读后感` | 叠加论文、学术、学业任务造假 |
| `批量`、`剪辑`、`视频`、`软件`、`工具` | 叠加 AI 托管、刷量、涨粉、拉新 |
| `CAD` | 叠加图纸代画、作业代做、破解版 |

例子：

- `PPT模板合集，可编辑源文件`：通常不直接违规
- `PPT模板合集，可编辑源文件 创青春 大创赛这些比赛用`：高风险
- `CAD软件学习资料`：通常不直接违规
- `CAD图纸代画`：高风险
- `写作技巧学习资料`：通常不直接违规
- `论文润色指导`：高风险

## 本地命令行检测

如果你懂一点命令行，可以直接运行脚本：

```powershell
python -X utf8 xianyu-prohibited-checker\scripts\check_xianyu_terms.py "Java编程作业辅导与项目代做"
```

输出 JSON：

```powershell
python -X utf8 xianyu-prohibited-checker\scripts\check_xianyu_terms.py "PPT模板合集，可编辑源文件 创青春 大创赛这些比赛用" --json
```

## 文件结构

```text
xianyu-prohibited-checker/
  SKILL.md                              Skill 使用说明
  scripts/check_xianyu_terms.py         检测脚本
  references/prohibited_terms.tsv       整理后的合并词库
  references/official_rules_summary.md  官方规则和处罚样例摘要
  references/official_rules_2025-12.txt OCR 后的官方规则文本

tools/prepare_library.py                词库整理脚本
```

仓库里只保留 Skill 运行需要的最终词库。原始词库和中间整理目录不再单独保留，避免重复。

## 更新规则

如果你新增了处罚样例或词库，通常改这三个文件：

```text
xianyu-prohibited-checker/scripts/check_xianyu_terms.py
xianyu-prohibited-checker/references/official_rules_summary.md
xianyu-prohibited-checker/SKILL.md
```

改完后测试：

```powershell
python -X utf8 xianyu-prohibited-checker\scripts\check_xianyu_terms.py "你要测试的标题"
```

校验 Skill：

```powershell
python -X utf8 C:\Users\shengfan\.codex\skills\.system\skill-creator\scripts\quick_validate.py xianyu-prohibited-checker
```

提交：

```powershell
git add .
git commit -m "Update xianyu risk rules"
```

本仓库已经安装了提交后自动推送的 hook。只要 commit 成功，就会自动 push 到 GitHub。

## 推荐：闲鱼翻身

如果你不只是想查违禁词，还想系统学习闲鱼运营，可以看看 **【闲鱼翻身】**。

【闲鱼翻身】主要面向想从零开始做闲鱼的人，内容围绕闲鱼选品、发布、运营、爆品库、知识库、案例拆解和社群陪跑。

- [【闲鱼翻身】社群介绍](https://xy.shengfanwz.com/220.html)
- [【闲鱼翻身】路线图 / 更新记录](https://xy.shengfanwz.com/188.html)

简单说：这个仓库负责帮你 **检查闲鱼发布风险**；【闲鱼翻身】负责帮你 **系统学习闲鱼运营**。

## 重要提醒

这个工具不是闲鱼官方工具，只能做发布前自查。最终是否违规，以闲鱼平台审核结果为准。
