# our-attitudes：Hilbert 墓石照片

状态：第三方图片，来源与许可以执行核验登记，2026-09-11。保留者：Mingli Yuan。
来源登记：assistant（DeepSeek Harness），经账号代理提交；本条只记录可核验的来源事实，
不对许可做法律判断。

墓石上的刻字是：

```
DAVID HILBERT
WIR MÜSSEN WISSEN
WIR WERDEN WISSEN
```

本目录保留这张照片作为这项工作的态度标记，与仓库根目录的
[`Unknown-LICENSE-v0.1-zh.md`](../../Unknown-LICENSE-v0.1-zh.md) 并列。
**它不是证据，也不是证书**：仓库里没有任何检查读它，没有任何算术或几何结论依赖它。

## 刻字：一次观察，不是证书

上面的刻字是 2026-09-11 由视觉模型读出的**观察**，不是执行过的检查：

- 读图模型：`deepseek-official` 路由的 `deepseek-v4-flash-vision-exp`
  （目录条目声明 `inputModalities: [text, image]`）。
- 适配器按像素预算缩放并重编码后送模型，**请求版本为 692×923、583877 字节**，
  与仓库中存储的 613267 字节原图不同字节；模型看的是派生图，不是原件。
- 可辨认：墓石上「DAVID HILBERT」与下面两行铭文。**不可辨认**：墓前两块地碑上的小字，
  在交付分辨率下读不出来，此处不猜（Commons 的分类把它们记为 David 与 Käthe Hilbert 之墓，
  那是 Commons 的说法，不是这里的读数）。
- 这一条随模型而异，也不构成 OCR 检查：任何以图片内容为依据的判断都应在
  [`experiments/`](../../experiments/) 里另立契约与证据，而不是引用本段散文。

因此本文件里唯一「执行过的」事实仍是下一节的字节核验。

## 文件与逐字节核验

`Göttingen_Stadtfriedhof_Grab_David_Hilbert.jpg`

| 项 | 值 |
|---|---|
| 字节数 | 613267 |
| SHA-256 | `f6ec19ded52c608eefc30dbd1095ff96a3bb00f371dfb6f72a36bddc1dfbaeea` |
| SHA-1 | `a275aa8f12305e77ff5b6608dc479bab7b0cfc04` |
| 尺寸 | 1200 × 1600，JPEG |
| EXIF | Panasonic DMC-TZ3，2008:05:10 07:55:56，sRGB；无 Artist / Copyright 字段 |

核验方式（2026-09-11 执行，可复跑）：

```sh
curl -o /tmp/commons-original.jpg \
  'https://upload.wikimedia.org/wikipedia/commons/4/4f/G%C3%B6ttingen_Stadtfriedhof_Grab_David_Hilbert.jpg'
shasum -a 256 /tmp/commons-original.jpg   # f6ec19de…
cmp resources/our-attitudes/Göttingen_Stadtfriedhof_Grab_David_Hilbert.jpg /tmp/commons-original.jpg
```

`cmp` 无输出，即逐字节相同；Commons `imageinfo` 返回的 `size` 613267 与 `sha1`
`a275aa8f…` 与本地一致。因此本地文件是 Commons 原件的**逐字节副本**，而不是重新压缩、
缩放或改名的版本。这一条是执行过的检查，不是转述。

## 来源与许可（按 Commons 页面所述原样记录）

| 项 | 值 |
|---|---|
| 文件页 | https://commons.wikimedia.org/wiki/File:G%C3%B6ttingen_Stadtfriedhof_Grab_David_Hilbert.jpg |
| 原件直链 | https://upload.wikimedia.org/wikipedia/commons/4/4f/G%C3%B6ttingen_Stadtfriedhof_Grab_David_Hilbert.jpg |
| 作者 | Kassandro（User:Kassandro） |
| 来源 | Own work（自制作品） |
| 许可 | CC BY-SA 3.0；Commons 同时列出 GFDL 并标注 license migration redundant |
| 许可链接 | https://creativecommons.org/licenses/by-sa/3.0 |
| 署名要求 | 是（AttributionRequired = true；Copyrighted = true） |
| 拍摄时间 | 2008-05-10 07:55:56（EXIF）；上传 2008-06-14 23:37:45 |
| 描述 | Tomb of David Hilbert in Goettingen |
| 相关分类 | Grave of David and Käthe Hilbert；Photographs by kassandro；Göttingen photographs taken on 2008-05-10 |

转载或分发本文件或其演绎作品时，应随附的署名文本：

> Photo: Kassandro, “Göttingen Stadtfriedhof Grab David Hilbert”,
> Wikimedia Commons, CC BY-SA 3.0.
> https://commons.wikimedia.org/wiki/File:G%C3%B6ttingen_Stadtfriedhof_Grab_David_Hilbert.jpg

仓库根 `LICENSE` 是仓库自身的条款，**不改变本文件的许可**：本文件继续保持 CC BY-SA 3.0，
其演绎作品须以相同许可发布并保留上述署名与许可声明。

## 未知与边界

- 除 Commons 所述外未另行取得书面许可，也未主张任何额外授权；此处不做法律裁定。
- GFDL 与 CC BY-SA 并列的部分按 Commons 页面记录，本文不裁定其适用性。
- 本仓库目前为私有、未分发，故「分发触发」的署名义务尚未实际发生；此处是**预先**留下记录。
- 任何检查都不读这张图片，图片内容不被任何结论引用（与库内「图不是证书」同一条纪律）。
