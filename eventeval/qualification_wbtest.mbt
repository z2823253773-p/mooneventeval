// Actual default 20M boundary, using a pre-consumed internal counter, no public knob.

///|
test "qualification_default_work_budget_equality_and_next_step" {
  let exact : WorkBudget = { used: 19_999_997L, limit: 20_000_000L, }
  inspect(
    maximum_matching([[0]], 1, exact).unwrap().steps == 3L,
    content="true",
  )
  inspect(exact.used == 20_000_000L, content="true")
  let over : WorkBudget = { used: 19_999_998L, limit: 20_000_000L, }
  match maximum_matching([[0]], 1, over) {
    Ok(_) => fail("partial matching returned beyond default limit")
    Err(e) => {
      inspect(
        e.limit == Some(20_000_000L) && e.observed == Some(20_000_001L),
        content="true",
      )
      inspect(over.used == 20_000_000L && exit_code(e) == 3, content="true")
    }
  }
}
