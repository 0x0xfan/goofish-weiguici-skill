# 闲鱼违禁词检测 Skill

这是一个给 Codex / ChatGPT 用的闲鱼商品发布风险检测 Skill。

你把商品标题、商品描述发给它，它会根据本项目整理的违规词库和闲鱼处罚样例，判断这个商品信息有没有发布风险。

它适合用来检查：

- 闲鱼商品标题
- 商品描述
- 图片里 OCR 出来的文案
- 课程、资料、软件、代写、竞赛、招聘代理等容易违规的商品信息

## 重要提醒

这个工具不是闲鱼官方工具，只能做发布前自查。最终是否违规，以闲鱼平台审核结果为准。

## 推荐：闲鱼翻身

如果你不只是想查违禁词，还想系统学习闲鱼运营，可以看看 **【闲鱼翻身】**。

【闲鱼翻身】主要面向想从零开始做闲鱼的人，内容围绕闲鱼选品、发布、运营、爆品库、知识库、案例拆解和社群陪跑。它适合想了解闲鱼怎么赚钱、怎么降低试错成本、怎么跟着更新节奏学习的人。

两个入口：

- [【闲鱼翻身】社群介绍](https://xy.shengfanwz.com/220.html)：适合先了解社群是做什么的、闲鱼为什么适合新手、学习路径大概怎么走。
- [【闲鱼翻身】路线图](https://xy.shengfanwz.com/188.html)：适合看历史更新记录，比如课程、爆品表、知识库、陪跑、AI 相关内容等更新进度。

简单说：这个仓库负责帮你 **检查闲鱼发布风险**；【闲鱼翻身】负责帮你 **系统学习闲鱼运营**。

## 怎么安装

### 方法一：放到 Codex Skill 目录

把这个文件夹：

```text
xianyu-prohibited-checker
```

复制到你的 Codex skills 目录。

Windows 常见位置是：

```text
C:\Users\你的用户名\.codex\skills\
```

如果你的用户名是 `shengfan`，路径通常是：

```text
C:\Users\shengfan\.codex\skills\
```

放好以后，目录应该长这样：

```text
C:\Users\shengfan\.codex\skills\xianyu-prohibited-checker\SKILL.md
```

### 方法二：从 GitHub 下载

```powershell
git clone https://github.com/0x0xfan/goofish-weiguici-skill.git
```

然后把里面的 `xianyu-prohibited-checker` 文件夹复制到 `.codex\skills` 目录。

## 怎么使用

在 Codex / ChatGPT 里这样问：

```text
用 $xianyu-prohibited-checker 检测：Java编程作业辅导与项目代做
```

也可以直接问：

```text
这个闲鱼标题会违规吗：2026最新AI全自动批量剪辑软件
```

如果 Skill 被正确安装，它会优先调用本项目的检测规则。

## 检测结果怎么看

一般会输出三种结果：

### 高风险

表示很可能触发闲鱼违规。

常见原因：

- 代写、代做、代画、代考
- 论文修改、论文润色、论文辅助
- 盗版网课、电子书资源、音视频资源
- AI 托管、刷量、涨粉、拉新
- 大厂内推、保面试、保 offer
- 招聘代理、网赚、招商加盟
- 竞赛加绩点、包拿奖、获奖证书

### 需人工复核

表示有风险信号，但不一定违规。

常见原因：

- 命中了人名、品牌名、公司名、机构名
- 命中了版权词
- 商品属于出版物、食品、票务等需要资质或规范发布的类目
- 词比较短，可能误判

### 未命中明显风险

表示当前词库和规则没有发现明显风险。

这不等于一定安全，只是说明没有明显命中。

## 已记录的真实处罚方向

本 Skill 已经根据多个闲鱼处罚截图补充了规则，包括：

- AI 托管违禁风险
- 大厂内推违禁风险
- 代写作业违禁风险
- 论文辅助违禁风险
- 假冒 / 盗版商品信息
- 内部资料性出版物
- 广告类信息
- 竞赛服务不当宣传
- 人名、品牌名、公司名、机构名的知识产权风险

## 本地命令行检测

如果你懂一点命令行，也可以直接运行脚本：

```powershell
python -X utf8 xianyu-prohibited-checker\scripts\check_xianyu_terms.py "Java编程作业辅导与项目代做"
```

输出 JSON：

```powershell
python -X utf8 xianyu-prohibited-checker\scripts\check_xianyu_terms.py "PPT模板合集，可编辑源文件 创青春 大创赛这些比赛用" --json
```

## 文件说明

```text
xianyu-prohibited-checker/
  SKILL.md                              Skill 使用说明
  scripts/check_xianyu_terms.py         检测脚本
  references/prohibited_terms.tsv       整理后的合并词库
  references/official_rules_summary.md  官方规则和处罚样例摘要
  references/official_rules_2025-12.txt OCR 后的官方规则文本

tools/prepare_library.py                 词库整理脚本
```

仓库里只保留 Skill 运行需要的最终词库。原始词库和中间整理目录不再单独保留，避免重复。

## 怎么更新词库

如果你新增了处罚样例或词库，可以修改：

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

## 常见边界

这些词不要单独判违规：

- `PPT模板`
- `可编辑源文件`
- `宣传稿`
- `演讲稿`
- `读后感`
- `可加急`
- `原创定制`
- `交接文档`
- `批量`
- `剪辑`
- `视频`
- `软件`
- `工具`
- `CAD`

它们需要和具体高风险语义组合，才会升级风险。

例如：

- `PPT模板合集，可编辑源文件`：通常不直接违规
- `PPT模板合集，可编辑源文件 创青春 大创赛这些比赛用`：高风险
- `CAD软件学习资料`：通常不直接违规
- `CAD图纸代画`：高风险
- `写作技巧学习资料`：通常不直接违规
- `论文润色指导`：高风险
