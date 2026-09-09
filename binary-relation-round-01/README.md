# 双二进制解释关系试验（binary relation round 01）

用法：`./aeg-binary-relation.sh /path/to/P /path/to/Q`
（源文件只读；副本、剖面、词表、块哈希、假设表、receipt-08 全部落在
`evidence-<时间戳>/`；错误与孔洞保留在 `errors.log` 与假设表的 Unknown 行。）

五阶段：0 pin（SHA-256 + file 类型）→ 1 结构剖面（otool/nm）→
2 词表交集（strings comm）→ 3 字节关系（64B 块哈希共享段）→
4 假设表（同源/内嵌/互释/同前沿）→ 5 receipt-08（接 receipt-07 前驱链）。
