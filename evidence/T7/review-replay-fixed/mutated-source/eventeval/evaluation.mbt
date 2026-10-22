///|
fn metrics_from_counts(reference : Int, prediction : Int, tp : Int) -> Metrics {
  let counts : Counts = {
    reference,
    prediction,
    tp,
    fp: prediction - tp,
    fn_count: reference - tp,
  }
  {
    counts,
    precision: if prediction == 0 {
      None
    } else {
      Some(tp.to_double() / prediction.to_double())
    },
    recall: if reference == 0 {
      None
    } else {
      Some(tp.to_double() / reference.to_double())
    },
    f1: if reference + prediction == 0 {
      None
    } else {
      Some((2 * tp).to_double() / (reference + prediction).to_double())
    },
  }
}

///|
fn evaluate_with_budget(
  input : Task,
  budget : WorkBudget,
) -> Result[Evaluation, EvalError] {
  let matches : Array[SelectedPair] = []
  let false_positives : Array[UnmatchedEvent] = []
  let false_negatives : Array[UnmatchedEvent] = []
  let by_recording : Array[(String, Metrics)] = []
  let label_reference = Array::make(input.labels.length(), 0)
  let label_prediction = Array::make(input.labels.length(), 0)
  let label_tp = Array::make(input.labels.length(), 0)
  let mut candidate_checks = 0
  let mut eligible_edges = 0
  let mut total_reference = 0
  let mut total_prediction = 0
  let mut total_tp = 0
  for rec in input.recordings {
    let mut rec_tp = 0
    for li in 0..<input.labels.length() {
      let label = input.labels[li]
      let refs = rec.reference.filter(e => e.label == label)
      let preds = rec.prediction.filter(e => e.label == label)
      if refs.is_empty() && preds.is_empty() {
        continue
      }
      label_reference[li] = label_reference[li] + refs.length()
      label_prediction[li] = label_prediction[li] + preds.length()
      let adjacency : Array[Array[Int]] = []
      for r in refs {
        let row : Array[Int] = []
        for p in 0..<preds.length() {
          candidate_checks = candidate_checks + 1
          if eligibility(r, preds[p], input.config).eligible {
            row.push(p)
            eligible_edges = eligible_edges + 1
          }
        }
        adjacency.push(row)
      }
      let before = budget.used
      let result = match maximum_matching(adjacency, preds.length(), budget) {
        Err(e) => return Err(e)
        Ok(m) => m
      }
      // Check the producer/consumer accounting boundary without accumulating twice.
      if result.steps != budget.used - before ||
        result.adjacency_checks > result.steps {
        return Err({
          kind: Internal,
          code: "INTERNAL_ERROR",
          message: "Inconsistent matching work accounting",
          path: Some("work.matching_steps"),
          limit: None,
          observed: None,
        })
      }
      let used_refs = Array::make(refs.length(), false)
      let used_preds = Array::make(preds.length(), false)
      for pair in result.pairs {
        let (r, p) = pair
        used_refs[r] = true
        used_preds[p] = true
        matches.push({
          recording_id: rec.id,
          label,
          reference: refs[r],
          prediction: preds[p],
          basis: eligibility(refs[r], preds[p], input.config),
        })
      }
      for r in 0..<refs.length() {
        if !used_refs[r] {
          false_negatives.push({
            recording_id: rec.id,
            event: refs[r],
            candidate_count: result.reference_degree[r],
          })
        }
      }
      for p in 0..<preds.length() {
        if !used_preds[p] {
          false_positives.push({
            recording_id: rec.id,
            event: preds[p],
            candidate_count: result.prediction_degree[p],
          })
        }
      }
      let tp = result.pairs.length()
      label_tp[li] = label_tp[li] + tp
      rec_tp = rec_tp + tp
    }
    by_recording.push(
      (
        rec.id,
        metrics_from_counts(
          rec.reference.length(),
          rec.prediction.length(),
          rec_tp,
        ),
      ),
    )
    total_reference = total_reference + rec.reference.length()
    total_prediction = total_prediction + rec.prediction.length()
    total_tp = total_tp + rec_tp
  }
  let by_label = Array::makei(input.labels.length(), i => {
    (
      input.labels[i],
      metrics_from_counts(label_reference[i], label_prediction[i], label_tp[i]),
    )
  })
  Ok({
    config: input.config,
    summary: metrics_from_counts(total_reference, total_prediction, total_tp),
    by_label,
    by_recording,
    matches,
    false_positives,
    false_negatives,
    candidate_checks,
    eligible_edges,
    matching_steps: budget.used,
  })
}

///|
pub fn evaluate(input : Task) -> Result[Evaluation, EvalError] {
  evaluate_with_budget(input, { used: 0L, limit: 20_000_000L, })
}
