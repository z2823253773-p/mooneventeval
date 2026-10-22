///|
/// Candidate timing is independent of matching and recording grouping. The
/// caller must group by recording; labels and all timing flags remain available
/// even when a pair is ineligible, so explanation shares exactly this basis.
fn eligibility(
  reference : Event,
  prediction : Event,
  config : Config,
) -> PairBasis {
  let onset_delta_us = prediction.onset_us - reference.onset_us
  let offset_delta_us = prediction.offset_us - reference.offset_us
  let onset_abs = if onset_delta_us < 0L {
    -onset_delta_us
  } else {
    onset_delta_us
  }
  let offset_abs = if offset_delta_us < 0L {
    -offset_delta_us
  } else {
    offset_delta_us
  }
  let fixed_scaled = config.collar_us * 1_000_000L
  let ratio_scaled = (reference.offset_us - reference.onset_us) *
    config.offset_ratio_ppm
  let offset_limit_scaled = if fixed_scaled > ratio_scaled {
    fixed_scaled
  } else {
    ratio_scaled
  }
  let label_match = reference.label == prediction.label
  let onset_pass = onset_abs <= config.collar_us
  let offset_pass = offset_abs * 1_000_000L <= offset_limit_scaled
  {
    label_match,
    onset_pass,
    offset_pass,
    eligible: label_match && onset_pass && offset_pass,
    onset_delta_us,
    offset_delta_us,
    onset_limit_us: config.collar_us,
    offset_limit_scaled,
  }
}
