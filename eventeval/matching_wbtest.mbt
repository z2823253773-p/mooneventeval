// Each assertion catches reuse, a missing augment, an invalid edge, or budget drift.

///|
fn check_matching(
  adjacency : Array[Array[Int]],
  prediction_count : Int,
  expected : Int,
) -> Matching raise {
  let result = maximum_matching(adjacency, prediction_count, {
    used: 0L,
    limit: 20_000_000L,
  }).unwrap()
  inspect(result.pairs.length() == expected, content="true")
  let references = Array::make(adjacency.length(), false)
  let predictions = Array::make(prediction_count, false)
  let prediction_degree = Array::make(prediction_count, 0)
  let mut previous = -1
  for row in adjacency {
    for p in row {
      prediction_degree[p] = prediction_degree[p] + 1
    }
  }
  for pair in result.pairs {
    let (r, p) = pair
    inspect(r > previous, content="true")
    previous = r
    inspect(adjacency[r].contains(p), content="true")
    inspect(!references[r] && !predictions[p], content="true")
    references[r] = true
    predictions[p] = true
  }
  inspect(result.prediction_degree == prediction_degree, content="true")
  for r in 0..<adjacency.length() {
    inspect(result.reference_degree[r] == adjacency[r].length(), content="true")
  }
  result
}

///|
test "matching_augmenting_trap" {
  let result = check_matching([[0, 1], [0]], 2, 2)
  inspect(result.pairs == [(0, 1), (1, 0)], content="true")
}

///|
test "matching_one_to_one_duplicate_and_isolated" {
  let _ = check_matching([[0, 1]], 2, 1)
  let _ = check_matching([[0], [0]], 1, 1)
  let _ = check_matching([[], [1], [], [0, 1]], 3, 2)
}

///|
test "matching_empty_and_fixed_order" {
  inspect(check_matching([], 0, 0).steps == 0L, content="true")
  inspect(check_matching([[]], 0, 0).steps == 1L, content="true")
  let _ = check_matching([], 3, 0)
  inspect(
    check_matching([[0, 1], [0, 1]], 2, 2).pairs == [(0, 0), (1, 1)],
    content="true",
  )
  inspect(
    check_matching([[0, 1], [0, 1], [0, 1]], 2, 2).pairs == [(0, 0), (1, 1)],
    content="true",
  )
}

///|
test "matching_one_edge_budget" {
  let budget : WorkBudget = { used: 0L, limit: 3L, }
  let result = maximum_matching([[0]], 1, budget).unwrap()
  inspect(result.pairs == [(0, 0)], content="true")
  inspect(result.steps == 3L && budget.used == 3L, content="true")
  inspect(result.adjacency_checks == 1L, content="true")
  let short : WorkBudget = { used: 0L, limit: 2L, }
  match maximum_matching([[0]], 1, short) {
    Ok(_) => fail("budget exhaustion returned a partial matching")
    Err(error) => {
      inspect(exit_code(error) == 3, content="true")
      inspect(error.code, content="RESOURCE_LIMIT")
      inspect(error.limit == Some(2L), content="true")
      inspect(error.observed == Some(3L), content="true")
      inspect(short.used == 2L, content="true")
    }
  }
}

///|
test "matching_shared_budget_and_call_delta" {
  let budget : WorkBudget = { used: 0L, limit: 6L, }
  inspect(
    maximum_matching([[0]], 1, budget).unwrap().steps == 3L,
    content="true",
  )
  inspect(
    maximum_matching([[0]], 1, budget).unwrap().steps == 3L,
    content="true",
  )
  inspect(budget.used == 6L, content="true")
  match maximum_matching([[]], 0, budget) {
    Ok(_) => fail("group reset the shared budget")
    Err(error) => {
      inspect(error.observed == Some(7L), content="true")
      inspect(budget.used == 6L, content="true")
    }
  }
  inspect(maximum_matching([], 0, budget).unwrap().steps == 0L, content="true")
}

///|
test "matching_augmentation_budget_every_boundary" {
  // Hand count: root0: entry + first edge + rewrite =3.
  // root1: entry, failed first-free edge, DFS edge0, enter owner0,
  // DFS edge0 (visited), DFS edge1, two path rewrites =8; total11.
  let budget : WorkBudget = { used: 0L, limit: 11L, }
  let result = maximum_matching([[0, 1], [0]], 2, budget).unwrap()
  inspect(result.steps == 11L, content="true")
  inspect(result.adjacency_checks == 5L, content="true")
  for limit in 0..<11 {
    let short : WorkBudget = { used: 0L, limit: limit.to_int64(), }
    match maximum_matching([[0, 1], [0]], 2, short) {
      Ok(_) => fail("incomplete augmentation returned success")
      Err(error) => {
        inspect(exit_code(error) == 3, content="true")
        inspect(short.used == limit.to_int64(), content="true")
        inspect(error.observed == Some(limit.to_int64() + 1L), content="true")
      }
    }
  }
}

///|
test "matching_long_augmenting_chain_explicit_stack" {
  let size = 1000
  let adjacency = Array::makei(size, r => {
    if r + 1 < size {
      [r, r + 1]
    } else {
      [0]
    }
  })
  let result = check_matching(adjacency, size, size)
  inspect(result.pairs[0] == (0, 1), content="true")
  inspect(result.pairs[size - 1] == (999, 0), content="true")
}

///|
fn record_matching_case(id : String, result : Matching) -> Unit {
  let pairs : Array[String] = []
  for pair in result.pairs {
    pairs.push("[\{pair.0},\{pair.1}]")
  }
  println(
    "{\"case\":\"\{id}\",\"pairs\":[\{pairs.join(",")}],\"steps\":\{result.steps},\"adjacency_checks\":\{result.adjacency_checks}}",
  )
}
