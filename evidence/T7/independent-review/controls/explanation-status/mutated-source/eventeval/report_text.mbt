///|
fn text_metric(value : Double?) -> String {
  match value {
    None => "未定义"
    Some(value) => value.to_string()
  }
}

///|
fn text_metrics(value : Metrics) -> String {
  let c = value.counts
  "reference=\{c.reference} prediction=\{c.prediction} TP=\{c.tp} FP=\{c.fp} FN=\{c.fn_count} precision=\{text_metric(value.precision)} recall=\{text_metric(value.recall)} F1=\{text_metric(value.f1)}"
}

///|
fn text_event(value : Event) -> String {
  "id=\{text_identity(value.id)} label=\{text_identity(value.label)} onset_s=\{format_scaled_seconds(value.onset_us,6)} offset_s=\{format_scaled_seconds(value.offset_us,6)}"
}

///|
fn text_basis(value : PairBasis) -> String {
  "label_match=\{value.label_match} onset_pass=\{value.onset_pass} offset_pass=\{value.offset_pass} eligible=\{value.eligible} onset_delta_s=\{format_scaled_seconds(value.onset_delta_us,6)} onset_limit_s=\{format_scaled_seconds(value.onset_limit_us,6)} offset_delta_s=\{format_scaled_seconds(value.offset_delta_us,6)} offset_limit_s=\{format_scaled_seconds(value.offset_limit_scaled,12)}"
}

///|
fn text_unmatched(value : UnmatchedEvent) -> String {
  let reason = if value.candidate_count == 0 {
    "no_eligible_candidate"
  } else {
    "unselected_in_maximum_matching"
  }
  "  recording=\{text_identity(value.recording_id)} \{text_event(value.event)} candidate_count=\{value.candidate_count} reason=\{reason}"
}

///|
pub fn report_text(value : Evaluation) -> Result[String, EvalError] {
  let lines = [
    "MoonEventEval 0.1.0 | collar-max-cardinality/v1",
    "状态：completed",
    "配置：collar_s=\{format_scaled_seconds(value.config.collar_us,6)} offset_ratio=\{format_scaled_seconds(value.config.offset_ratio_ppm,6)}",
    "汇总：\{text_metrics(value.summary)}",
    "按类别：",
  ]
  for row in value.by_label {
    lines.push("  label=\{text_identity(row.0)} \{text_metrics(row.1)}")
  }
  lines.push("按录制：")
  for row in value.by_recording {
    lines.push("  recording=\{text_identity(row.0)} \{text_metrics(row.1)}")
  }
  lines.push("所选配对（最大基数；不优化时间误差）：")
  for pair in value.matches {
    lines.push(
      "  recording=\{text_identity(pair.recording_id)} label=\{text_identity(pair.label)} reference=(\{text_event(pair.reference)}) prediction=(\{text_event(pair.prediction)}) \{text_basis(pair.basis)}",
    )
  }
  lines.push("未匹配预测（FP）：")
  for item in value.false_positives {
    lines.push(text_unmatched(item))
  }
  lines.push("未匹配参考（FN）：")
  for item in value.false_negatives {
    lines.push(text_unmatched(item))
  }
  lines.push(
    "说明：有候选但未选中不表示该事件在所有最大匹配中均不可能被选中。",
  )
  lines.push(
    "工作量：candidate_checks=\{value.candidate_checks} eligible_edges=\{value.eligible_edges} matching_steps=\{value.matching_steps}",
  )
  bounded_output(lines.join("\n") + "\n", 16_777_216)
}

///|
pub fn explanation_text(value : PairExplanation) -> Result[String, EvalError] {
  let lines = [
    "MoonEventEval 0.1.0 | collar-max-cardinality/v1 | pair explanation",
    "状态：completed",
    "配置：collar_s=\{format_scaled_seconds(value.config.collar_us,6)} offset_ratio=\{format_scaled_seconds(value.config.offset_ratio_ppm,6)}",
    "录制：recording=\{text_identity(value.recording_id)}",
    "参考：\{text_event(value.reference)}",
    "预测：\{text_event(value.prediction)}",
    "判断：\{text_basis(value.basis)}",
    "说明：这是配对条件解释，不推断是否被选中；不执行最大匹配。",
  ]
  bounded_output(lines.join("\n") + "\n", 16_777_216)
}
