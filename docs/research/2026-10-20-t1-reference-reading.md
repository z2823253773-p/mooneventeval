# T1参考源码只读核对

读取固定提交的[sed_eval/sound_event.py](https://github.com/TUT-ARG/sed_eval/blob/0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb/sed_eval/sound_event.py#L1472)，未安装或执行参考环境。

`validate_onset`（1472–1496行）使用绝对起点偏差与固定collar比较，包含等号。
`validate_offset`（1498–1530行）使用参考事件时长，终点容差为collar和时长比例项的最大值，包含等号。
这些源码条件与PRD中的公式一致。MoonEventEval按已批准PRD以整数微秒/ppm精确实现；这里没有运行浮点参考、没有证明边界parity或计数一致。

T1b仍单独负责参考依赖、版本/哈希锁和self-check；T1完成不代表T1b或M2完成。
